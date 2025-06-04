document.addEventListener('DOMContentLoaded', () => {
  const encuestaForm = document.getElementById('encuestaForm');
  const modalElement = document.getElementById('addEncuestaModal');
  const modal = new bootstrap.Modal(modalElement);
  const formError = document.getElementById('formError');
  const tbody = document.getElementById('encuestasBody');

  // Funciones para mostrar y ocultar errores en el div
  function mostrarError(mensaje) {
    formError.textContent = mensaje;
    formError.classList.remove('d-none');
  }
  function ocultarError() {
    formError.textContent = '';
    formError.classList.add('d-none');
  }

  // Obtener token CSRF
  function getCsrfToken() {
    const input = encuestaForm.querySelector('input[name="csrf_token"]');
    return input ? input.value : '';
  }

  // Función para escapar texto y evitar XSS
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Función para renderizar la tabla de encuestas
  function renderEncuestas(encuestas) {
    if (!Array.isArray(encuestas) || encuestas.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="3" class="text-center">No hay encuestas registradas.</td>
        </tr>`;
      return;
    }

    tbody.innerHTML = encuestas.map((encuesta, index) => `
      <tr data-encuesta-id="${encuesta.id}">
        <th scope="row">${index + 1}</th>
        <td class="pregunta-text">${escapeHtml(encuesta.pregunta)}</td>
        <td>
          <button type="button"
            class="btn btn-outline-primary btn-sm rounded-circle shadow-sm me-2 btn-editar"
            style="width: 32px; height: 32px;" title="Editar"
            data-id="${encuesta.id}"
            data-pregunta="${escapeHtml(encuesta.pregunta)}">
            <i class="bi bi-pencil-fill"></i>
          </button>
          <button type="button"
            class="btn btn-outline-danger btn-sm rounded-circle shadow-sm btn-eliminar"
            style="width: 32px; height: 32px;" title="Eliminar"
            data-id="${encuesta.id}">
            <i class="bi bi-trash-fill"></i>
          </button>
        </td>
      </tr>
    `).join('');
  }

  // Abrir modal para crear o editar
  modalElement.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const titleEl = modalElement.querySelector('.modal-title');
    const idInput = document.getElementById('encuestaId');
    const preguntaEl = document.getElementById('pregunta');

    ocultarError();

    if (button && button.dataset.id) {
      // Modo edición
      titleEl.textContent = 'Editar Encuesta';
      idInput.value = button.dataset.id;
      preguntaEl.value = button.dataset.pregunta || '';
    } else {
      // Modo creación
      titleEl.textContent = 'Nueva Encuesta';
      idInput.value = '';
      encuestaForm.reset();
    }
  });

  // Envío del formulario para crear o editar encuesta
  encuestaForm.addEventListener('submit', async e => {
    e.preventDefault();
    ocultarError();

    const id = document.getElementById('encuestaId').value.trim();
    const pregunta = document.getElementById('pregunta').value.trim();

    if (!pregunta) {
      mostrarError('La pregunta es requerida.');
      return;
    }
    if (pregunta.length > 500) {
      mostrarError('La pregunta no puede exceder 500 caracteres.');
      return;
    }

    const baseUrl = '/jefe_dep/encuestas';
    const url = id ? `${baseUrl}/${id}` : baseUrl;
    const method = id ? 'PUT' : 'POST';
    const token = getCsrfToken();
    const body = JSON.stringify({ pregunta });

    try {
      const res = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token
        },
        body
      });

      let data;
      try {
        data = await res.json();
      } catch {
        const text = await res.text();
        throw new Error(text || 'Error inesperado del servidor');
      }

      if (!res.ok) {
        throw new Error(data.error || `HTTP ${res.status}`);
      }

      renderEncuestas(data.encuestas);
      modal.hide();

      Swal.fire({
        icon: 'success',
        title: data.message,
        timer: 2000,
        showConfirmButton: false
      });

    } catch (err) {
      mostrarError(err.message || 'Error al guardar la encuesta.');
      console.error('[ERROR ENCUESTA]', err);
    }
  });

  // Delegación de eventos para botones editar y eliminar en tbody
  tbody.addEventListener('click', async e => {
    const editarBtn = e.target.closest('.btn-editar');
    const eliminarBtn = e.target.closest('.btn-eliminar');

    if (editarBtn) {
      // Abrir modal con datos para editar
      const id = editarBtn.dataset.id;
      const pregunta = editarBtn.dataset.pregunta;

      // Crear botón temporal para disparar modal con datos
      const modalToggleBtn = document.createElement('button');
      modalToggleBtn.type = 'button'; // importante para que no sea submit
      modalToggleBtn.style.display = 'none'; // oculto
      modalToggleBtn.setAttribute('data-bs-toggle', 'modal');
      modalToggleBtn.setAttribute('data-bs-target', '#addEncuestaModal');
      modalToggleBtn.dataset.id = id;
      modalToggleBtn.dataset.pregunta = pregunta;

      document.body.appendChild(modalToggleBtn);
      modalToggleBtn.click();
      document.body.removeChild(modalToggleBtn);

    } else if (eliminarBtn) {
      // Solo si no fue editar, ejecutamos eliminar
      const id = eliminarBtn.dataset.id;
      const result = await Swal.fire({
        title: '¿Estás seguro?',
        text: "¡No podrás revertir esto!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      });

      if (result.isConfirmed) {
        try {
          const token = getCsrfToken();
          const res = await fetch(`/jefe_dep/encuestas/${id}`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': token }
          });

          let data;
          try {
            data = await res.json();
          } catch {
            const text = await res.text();
            throw new Error(text || 'Error inesperado del servidor');
          }

          if (!res.ok) {
            throw new Error(data.error || `HTTP ${res.status}`);
          }

          renderEncuestas(data.encuestas);

          Swal.fire({
            icon: 'success',
            title: data.message,
            timer: 2000,
            showConfirmButton: false
          });

        } catch (err) {
          Swal.fire('Error', err.message || 'Error al eliminar la encuesta.', 'error');
          console.error('[ERROR ELIMINAR]', err);
        }
      }
    }
  });

});
