from pathlib import Path
from datetime import timedelta
from urllib.parse import urlsplit

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
env = environ.Env()
environ.Env.read_env(ROOT_DIR / ".env")

DEBUG = env.bool("DJANGO_DEBUG", default=False)
SECRET_KEY = env("DJANGO_SECRET_KEY")
if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5:
    raise ImproperlyConfigured("Genera DJANGO_SECRET_KEY con get_random_secret_key().")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"] if DEBUG else [])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
render_hostname = env("RENDER_EXTERNAL_HOSTNAME", default="")
if not DEBUG and render_hostname:
    ALLOWED_HOSTS.append(render_hostname)
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_hostname}")
if not DEBUG:
    if not ALLOWED_HOSTS or any("*" in host or host.startswith(".") or "/" in host for host in ALLOWED_HOSTS):
        raise ImproperlyConfigured("Producción requiere DJANGO_ALLOWED_HOSTS con dominios exactos.")
    for origin in CSRF_TRUSTED_ORIGINS:
        parsed = urlsplit(origin)
        if parsed.scheme != "https" or not parsed.hostname or "*" in origin or parsed.path or parsed.query or parsed.fragment or parsed.username:
            raise ImproperlyConfigured("Los orígenes CSRF de producción deben ser orígenes HTTPS exactos.")

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "axes", "sellers", "quality", "action_plans",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates", ROOT_DIR / "frontend" / "dist"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
database_url = env("DATABASE_URL", default="")
DATABASES = {"default": env.db_url_config(database_url) if database_url else {
    "ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3",
}}
if not DEBUG and DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured("Producción requiere DATABASE_URL de PostgreSQL persistente.")
if not DEBUG:
    DATABASES["default"].setdefault("OPTIONS", {}).setdefault("sslmode", "require")
    if DATABASES["default"]["OPTIONS"]["sslmode"] not in ("require", "verify-ca", "verify-full"):
        raise ImproperlyConfigured("PostgreSQL de producción requiere TLS.")
DATABASES["default"]["CONN_MAX_AGE"] = 0
if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    DATABASES["default"].setdefault("OPTIONS", {}).update({"connect_timeout": 5})

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
# Persistido en PostgreSQL: no depende de la memoria de un worker ni de Redis.
# Se limita por usuario para no confiar en cabeceras IP del cliente/proxy.
AXES_LOCKOUT_PARAMETERS = ["username"]
# W006 exige IP incluso al limitar globalmente por username. Aquí rotar IP,
# cookies o User-Agent no cambia la clave; lo comprueba config.tests.
# Evitamos bloquear a todos los evaluadores por compartir la IP del proxy.
SILENCED_SYSTEM_CHECKS = ["axes.W006"]
AXES_CLIENT_IP_CALLABLE = "config.security.no_client_ip"
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_RESET_ON_SUCCESS = True
AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False
AXES_DISABLE_ACCESS_LOG = True
AXES_SENSITIVE_PARAMETERS = ["username", "ip_address", "csrfmiddlewaretoken"]
AXES_LOCKOUT_TEMPLATE = "registration/locked_out.html"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
LANGUAGE_CODE = "es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
frontend_dist = ROOT_DIR / "frontend" / "dist"
STATICFILES_DIRS = [("react", frontend_dist)] if frontend_dist.exists() else []
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["sellers.permissions.IsMarketplaceAgent"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 8 * 60 * 60
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
# El probe interno debe ejecutar SQL: Render también acepta 301 como saludable.
# Este endpoint sólo devuelve ok/unavailable, sin sesión ni datos de dominio.
SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
WHITENOISE_IMMUTABLE_FILE_TEST = r"^/static/react/assets/.+-[A-Za-z0-9_-]{8,}\.(css|js)$"
if env.bool("DJANGO_TRUST_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SAP_DEMO_MODE = env.bool("SAP_DEMO_MODE", default=False)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "axes": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
