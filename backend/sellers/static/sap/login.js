/* Progressive enhancement of Django's LoginView. The native POST also works
   without JavaScript; validation, CSRF, sessions and redirects stay on the server. */
function enhanceLogin(form) {
  const password = form.elements.password;
  const username = form.elements.username;
  const toggle = form.querySelector('.login-password-toggle');
  const submit = form.querySelector('.login-submit');
  const label = form.querySelector('.login-submit-label');
  const spinner = form.querySelector('.login-spinner');
  const status = form.querySelector('.login-status');
  const errors = form.querySelector('#login-errors');
  const capsLock = form.querySelector('#caps-lock');
  let pending = false;

  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    const visible = password.type === 'password';
    password.type = visible ? 'text' : 'password';
    toggle.setAttribute('aria-pressed', String(visible));
    toggle.setAttribute('aria-label', visible ? 'Ocultar contraseña' : 'Mostrar contraseña');
  });
  const checkCapsLock = (event) => { capsLock.hidden = !event.getModifierState('CapsLock'); };
  password.addEventListener('keydown', checkCapsLock);
  password.addEventListener('keyup', checkCapsLock);
  password.addEventListener('blur', () => { capsLock.hidden = true; });

  function setPending(value) {
    pending = value;
    form.setAttribute('aria-busy', String(value));
    submit.disabled = value;
    toggle.disabled = value;
    username.readOnly = value;
    password.readOnly = value;
    spinner.hidden = !value;
    label.textContent = value ? 'Iniciando sesión…' : 'Iniciar sesión';
    status.textContent = value ? 'Comprobando credenciales.' : '';
  }

  function showError(message) {
    const paragraph = document.createElement('p');
    paragraph.textContent = message;
    errors.replaceChildren(paragraph);
    errors.hidden = false;
    errors.focus();
  }

  if (!errors.hidden) errors.focus();
  else form.querySelector('[aria-invalid="true"]')?.focus();

  if (!window.fetch || !window.AbortController) return;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (pending) return;
    const data = new FormData(form);
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 30000);
    setPending(true);
    errors.hidden = true;
    try {
      const response = await fetch(form.action, {
        method: 'POST', body: data, credentials: 'same-origin',
        mode: 'same-origin', signal: controller.signal,
      });
      if (response.redirected) {
        // Fetch removes URL fragments. Restore a requested fragment only when
        // its origin, path and query match LoginView's validated destination.
        const destination = new URL(response.url);
        try {
          const next = new URL(form.elements.next.value, window.location.href);
          if (next.origin === destination.origin && next.pathname === destination.pathname &&
              next.search === destination.search) destination.hash = next.hash;
        } catch { /* A malformed `next` leaves Django's destination intact. */ }
        window.location.assign(destination.href);
        return;
      }
      if (response.status === 429) {
        showError('Demasiados intentos de acceso. Espera 15 minutos antes de volver a intentarlo.');
        return;
      }
      if (response.status === 403) {
        showError('No se ha podido verificar la solicitud. Recarga esta página y vuelve a intentarlo.');
        return;
      }
      if (!response.ok) {
        showError('SAP no está disponible en este momento. Inténtalo de nuevo en unos instantes.');
        return;
      }
      const result = new DOMParser().parseFromString(await response.text(), 'text/html');
      const nextForm = result.querySelector('#login-form');
      if (!nextForm || !nextForm.querySelector('[aria-invalid="true"]')) {
        showError('No se ha podido completar el acceso. Recarga esta página y vuelve a intentarlo.');
        return;
      }
      // Keep Django's bound form: field errors, cleared password and CSRF token.
      form.replaceWith(nextForm);
      enhanceLogin(nextForm);
    } catch {
      showError('No se ha podido conectar con SAP. Comprueba tu conexión e inténtalo de nuevo.');
    } finally {
      window.clearTimeout(timeout);
      setPending(false);
    }
  });
}

const loginForm = document.querySelector('#login-form');
if (loginForm) enhanceLogin(loginForm);
