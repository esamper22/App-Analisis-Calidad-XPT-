import { renderUsers } from "./render-user.js";

document.addEventListener('DOMContentLoaded', () => {
  const editForm = document.getElementById('editUserForm');
  const editBtn = document.getElementById('submitEditUserBtn');

  function getCsrfTokenEdit() {
    return editForm.querySelector('input[name="csrf_token"]').value;
  }

  // Función global para rellenar formulario y mostrar modal
  window.editarUsuario = async function (userId) {
    try {
      const response = await fetch(`/admin/obtener-usuario/${userId}`);
      const data = await response.json();

      if (!response.ok) {
        return Swal.fire('Error', data.error || 'No se pudo cargar el usuario', 'error');
      }

      const user = data.usuario;

      // Llenar formulario
      editForm.elements['editUserId'].value = user.id;
      editForm.elements['nombre_completo'].value = user.nombre_completo;
      editForm.elements['nombre_usuario'].value = user.nombre_usuario;
      editForm.elements['correo'].value = user.correo;
      editForm.elements['rol'].value = user.rol;

      // Mostrar modal
      const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
      modal.show();

    } catch (err) {
      console.error(err);
      Swal.fire('Error', 'No se pudo conectar con el servidor', 'error');
    }
  };


  // Botón de enviar edición
  editBtn.addEventListener('click', async () => {
    const userId = editForm.elements['editUserId'].value;

    const payload = {
      nombre_completo: editForm.elements['nombre_completo'].value.trim(),
      nombre_usuario: editForm.elements['nombre_usuario'].value.trim(),
      correo: editForm.elements['correo'].value.trim(),
      rol: editForm.elements['rol'].value
    };

    if (!payload.nombre_completo || !payload.nombre_usuario || !payload.correo || !payload.rol) {
      return Swal.fire('Campos incompletos', 'Todos los campos son obligatorios.', 'warning');
    }

    try {
      const response = await fetch(`/admin/editar-usuario/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfTokenEdit()
        },
        credentials: 'same-origin',
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (response.status === 400 || response.status === 409) {
        return Swal.fire('Error', result.error, 'warning');
      }
      if (!response.ok) {
        return Swal.fire('Error', result.error || 'Error desconocido', 'error');
      }

      Swal.fire({
        icon: 'success',
        title: 'Actualizado',
        text: result.mensaje,
        timer: 1500,
        showConfirmButton: false
      });

      renderUsers(result.usuarios);
      bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
      editForm.reset();

    } catch (err) {
      console.error(err);
      Swal.fire('Error', 'No se pudo conectar con el servidor', 'error');
    }
  });

  // Función global para eliminar
  window.eliminarUsuario = async function (userId) {
    const confirm = await Swal.fire({
      title: '¿Eliminar usuario?',
      text: 'Esta acción no se puede deshacer.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });

    if (!confirm.isConfirmed) return;

    try {
      const response = await fetch(`/admin/eliminar-usuario/${userId}`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': getCsrfTokenEdit()
        },
        credentials: 'same-origin'
      });

      const result = await response.json();

      if (!response.ok) {
        return Swal.fire('Error', result.error || 'Error al eliminar', 'error');
      }

      Swal.fire({
        icon: 'success',
        title: 'Eliminado',
        text: result.mensaje,
        timer: 1500,
        showConfirmButton: false
      });

      renderUsers(result.usuarios);

    } catch (err) {
      console.error(err);
      Swal.fire('Error', 'No se pudo conectar con el servidor', 'error');
    }
  };
});
