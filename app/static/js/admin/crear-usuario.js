import { renderUsers } from "./render-user.js";

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('addUserForm');
  const submitBtn = document.getElementById('submitUserBtn');

  submitBtn.addEventListener('click', async (e) => {
    e.preventDefault(); // Prevenir envío tradicional del formulario

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    const csrfToken = formData.get('csrf_token');

    try {
      const response = await fetch('/admin/crear-usuario', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        credentials: 'same-origin',
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (response.status === 400) {
        // Manejar errores de validación de WTForms
        const errorMessages = result.fields 
          ? Object.entries(result.fields)
              .map(([field, msg]) => `<strong>${field}</strong>: ${msg}`)
              .join('<br>')
          : result.error;
        
        Swal.fire({
          title: 'Errores en el formulario',
          html: errorMessages,
          icon: 'warning'
        });
        return;
      }

      if (response.status === 409) {
        Swal.fire('Conflicto', result.error, 'warning');
        return;
      }

      if (!response.ok) {
        Swal.fire('Error', result.error || 'Error desconocido', 'error');
        return;
      }

      // Éxito: actualizar UI
      Swal.fire({
        icon: 'success',
        title: result.mensaje,
        timer: 1500,
        showConfirmButton: false
      });

      renderUsers(result.usuarios);
      bootstrap.Modal.getInstance(form.closest('.modal')).hide();
      form.reset();

    } catch (error) {
      console.error('Error:', error);
      Swal.fire('Error', 'Error de conexión con el servidor', 'error');
    }
  });
});
