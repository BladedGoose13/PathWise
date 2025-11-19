// Selecciona los botones y elementos del menú
const toggler = document.querySelector('.sidebar-toggler');
const sidebar = document.querySelector('.sidebar');

// --- Control del botón de abrir/cerrar menú ---
if (toggler) {
  toggler.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
}

// --- Permitir navegación normal en los enlaces ---
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', e => {
    const href = link.getAttribute('href');

    // Si el enlace tiene un destino válido y no es "#", redirige
    if (href && href !== '#') {
      window.location.href = href;
    } else {
      // Si es "#", evita que recargue la página
      e.preventDefault();
    }
  });
});
