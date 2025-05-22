/**
* Reconstruye el <tbody> de la tabla de usuarios de forma asíncrona y con loader
* @param {Array} users – Lista de usuarios con propiedades:
*                        id, nombre_usuario, nombre_completo, correo, rol, activo
*/
export async function renderUsers (users) {
  const tableBody = document.querySelector('#usersTable tbody');
  tableBody.innerHTML = '';  // Limpia filas previas

  if (!users.length) {
    tableBody.innerHTML = `
      <tr><td colspan="7" class="text-center">No hay usuarios registrados.</td></tr>
    `;
    return;
  }

  // Mostrar loader con SweetAlert2
  Swal.fire({
    title: 'Cargando usuarios...',
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });

  const batchSize = 50; // Número de usuarios a procesar por lote
  for (let i = 0; i < users.length; i += batchSize) {
    const batch = users.slice(i, i + batchSize);

    batch.forEach((user, idx) => {
      const tr = document.createElement('tr');
      tr.dataset.userId = user.id;
      tr.innerHTML = `
        <th scope="row">${i + idx + 1}</th>
        <td>${user.nombre_usuario}</td>
        <td>${user.nombre_completo}</td>
        <td>${user.correo}</td>
        <td>${user.rol.charAt(0).toUpperCase() + user.rol.slice(1)}</td>
        <td>
          <span class="badge bg-${user.activo ? 'success' : 'secondary'}">
            ${user.activo ? 'Activo' : 'Inactivo'}
          </span>
        </td>
        <td>
          <button
            type="button"
            class="btn btn-outline-primary btn-sm rounded-circle shadow-sm me-2 d-inline-flex align-items-center justify-content-center"
            style="width: 32px; height: 32px;"
            title="Editar"
            onclick="editarUsuario(${user.id})"
          ><i class="bi bi-pencil-fill"></i></button>
          <button
            type="button"
            class="btn btn-outline-danger btn-sm rounded-circle shadow-sm d-inline-flex align-items-center justify-content-center"
            style="width: 32px; height: 32px;"
            title="Eliminar"
            onclick="eliminarUsuario(${user.id})"
          ><i class="bi bi-trash-fill"></i></button>
        </td>
      `;
      tableBody.appendChild(tr);
    });

    // Pausa para ceder el hilo y evitar congelamiento
    await new Promise(resolve => setTimeout(resolve, 50));
  }

  Swal.close();
}

