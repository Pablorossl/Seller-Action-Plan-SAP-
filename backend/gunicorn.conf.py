"""WSGI sencillo para el proxy HTTPS del proveedor."""
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "sync"
timeout = 30
graceful_timeout = 30
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
# Sin query string, cookies, cuerpo ni usuario autenticado en el access log.
access_log_format = '%(m)s %(U)s %(s)s %(L)s'
capture_output = True
# Django decide si confía en X-Forwarded-Proto con DJANGO_TRUST_PROXY.
secure_scheme_headers = {}
