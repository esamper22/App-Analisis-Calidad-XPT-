document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.flash-container');
    if (!container) return;
  
    container.querySelectorAll('.flash-message').forEach(alert => {
      // ---------- ENTRADA ----------
      // Forzamos recálculo y añadimos la clase .show para disparar el fade‑in/slide‑down
      requestAnimationFrame(() => {
        alert.classList.add('show');
      });
  
      // ---------- SALIDA AUTOMÁTICA ----------
      setTimeout(() => fadeAndRemove(alert), 7000);
  
      // ---------- CIERRE MANUAL ----------
      const closeBtn = alert.querySelector('.btn-close');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => fadeAndRemove(alert));
      }
    });
  
    function fadeAndRemove(el) {
      // quitamos la clase show y añadimos fade-out
      el.classList.remove('show');
      el.classList.add('fade-out');
      el.addEventListener('transitionend', () => {
        el.remove();
        if (container.children.length === 0) {
          container.remove();
        }
      }, { once: true });
    }
  });
  