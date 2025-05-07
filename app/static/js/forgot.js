// static/js/forgot.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('forgotForm');
    const btn  = document.getElementById('forgotButton');
  
    form.addEventListener('submit', async e => {
      e.preventDefault();
      btn.disabled = true;
      btn.textContent = 'Enviando…';
  
      const formData = new FormData(form);
      try {
        const resp = await fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await resp.json();
  
        if (data.success) {
          // SweetAlert2 feedback (asegúrate de incluir la librería)
          Swal.fire({
            icon: 'success',
            title: '¡Listo!',
            text: 'Revisa tu correo para el enlace de restablecimiento.',
            confirmButtonText: 'Aceptar'
          });
          form.reset();
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: data.error || 'No se pudo enviar el enlace.',
          });
        }
      } catch (err) {
        console.error(err);
        Swal.fire({
          icon: 'error',
          title: 'Oops...',
          text: 'Error de conexión. Intenta más tarde.'
        });
      } finally {
        btn.disabled = false;
        btn.textContent = 'Enviar enlace';
      }
    });
  });
  