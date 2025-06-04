document.addEventListener("DOMContentLoaded", () => {
    // ---------- Referencias y variables ----------
    const tiposGridBody = document.getElementById("tiposBody");
    const tiposPagination = document.getElementById("tiposPagination");
    const searchTipoInput = document.getElementById("searchTipoInput");

    const modalTipo = new bootstrap.Modal(document.getElementById("addTipoModal"));
    const tipoForm = document.getElementById("tipoForm");
    const formErrorTipo = document.getElementById("formErrorTipo");

    const tipoIdInput = document.getElementById("tipoId");
    const tipoNombreInput = document.getElementById("tipoNombre");
    const tipoDescInput = document.getElementById("tipoDescripcion");

    // Datos iniciales pasados por Jinja
    let tiposData = [];
    let filteredTipos = [...tiposData];
    const pageSizeTipos = 5;
    let currentTipoPage = 1;

    // ---------- Funciones auxiliares ----------
    function mostrarErrorTipo(msg) {
        formErrorTipo.textContent = msg;
        formErrorTipo.classList.remove("d-none");
    }
    function ocultarErrorTipo() {
        formErrorTipo.textContent = "";
        formErrorTipo.classList.add("d-none");
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function getCsrfToken() {
        const input = tipoForm.querySelector('input[name="csrf_token"]');
        return input ? input.value : "";
    }

    // ---------- Render de una página de tipos ----------
    function renderTiposPage(page) {
        const start = (page - 1) * pageSizeTipos;
        const end = start + pageSizeTipos;
        const slice = filteredTipos.slice(start, end);

        if (!slice.length) {
            tiposGridBody.innerHTML = `
        <tr>
          <td colspan="3" class="text-center">No hay tipos registrados.</td>
        </tr>`;
        } else {
            tiposGridBody.innerHTML = slice
                .map((tipo, idx) => {
                    const globalIndex = start + idx + 1;
                    return `
            <tr data-tipo-id="${tipo.id}">
              <th scope="row">${globalIndex}</th>
              <td>${escapeHtml(tipo.nombre)}</td>
              <td>
                <button
                  class="btn btn-outline-primary btn-sm rounded-circle me-2 btn-tipo-editar"
                  style="width: 28px; height: 28px;"
                  title="Editar"
                  data-id="${tipo.id}"
                  data-nombre="${escapeHtml(tipo.nombre)}"
                  data-descripcion="${escapeHtml(tipo.descripcion || '')}"
                  data-bs-toggle="modal"
                  data-bs-target="#addTipoModal"
                >
                  <i class="bi bi-pencil-fill"></i>
                </button>
                <button
                  class="btn btn-outline-danger btn-sm rounded-circle btn-tipo-eliminar"
                  style="width: 28px; height: 28px;"
                  title="Eliminar"
                  data-id="${tipo.id}"
                >
                  <i class="bi bi-trash-fill"></i>
                </button>
              </td>
            </tr>`;
                })
                .join("");
        }

        renderTiposPagination();
    }

    // ---------- Render de controles de paginación para tipos ----------
    function renderTiposPagination() {
        const totalPages = Math.ceil(filteredTipos.length / pageSizeTipos);
        tiposPagination.innerHTML = "";

        if (totalPages <= 1) return;

        const isSmall = window.innerWidth < 768;
        tiposPagination.classList.toggle("flex-column", isSmall);

        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            li.className = "page-item" + (i === currentTipoPage ? " active" : "");
            const a = document.createElement("a");
            a.className = "page-link";
            a.href = "#";
            a.textContent = i;
            a.addEventListener("click", (e) => {
                e.preventDefault();
                if (i === currentTipoPage) return;
                currentTipoPage = i;
                renderTiposPage(currentTipoPage);
            });
            li.appendChild(a);
            tiposPagination.appendChild(li);
        }
    }

    // ---------- Filtrado en tiempo real de tipos ----------
    searchTipoInput.addEventListener("input", () => {
        const q = searchTipoInput.value.trim().toLowerCase();
        filteredTipos = tiposData.filter((tipo) =>
            tipo.nombre.toLowerCase().includes(q)
        );
        currentTipoPage = 1;
        renderTiposPage(currentTipoPage);
    });

    // ---------- Manejo del modal para crear/editar tipo ----------
    document.getElementById("addTipoModal").addEventListener("show.bs.modal", (event) => {
        const button = event.relatedTarget;
        ocultarErrorTipo();

        if (button && button.classList.contains("btn-tipo-editar")) {
            // Modo edición
            document.getElementById("addTipoModalLabel").textContent = "Editar Tipo de Aplicación";
            const id = button.dataset.id;
            const nombre = button.dataset.nombre;
            const descripcion = button.dataset.descripcion;

            tipoIdInput.value = id;
            tipoNombreInput.value = nombre;
            tipoDescInput.value = descripcion;
        } else {
            // Modo creación
            document.getElementById("addTipoModalLabel").textContent = "Nuevo Tipo de Aplicación";
            tipoIdInput.value = "";
            tipoForm.reset();
        }
    });

    // ---------- Envío AJAX para crear o editar tipo ----------
    tipoForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        ocultarErrorTipo();

        const id = tipoIdInput.value.trim();
        const nombre = tipoNombreInput.value.trim();
        const descripcion = tipoDescInput.value.trim();

        if (!nombre) {
            mostrarErrorTipo("El nombre es obligatorio.");
            return;
        }

        const urlBase = "/jefe_dep/tipo_aplicacion";
        const url = id ? `${urlBase}/${id}` : urlBase;
        const method = id ? "PUT" : "POST";
        const token = getCsrfToken();

        const payload = { nombre, descripcion };

        try {
            const res = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": token,
                },
                body: JSON.stringify(payload),
            });

            const text = await res.text();
            let data = null;
            try {
                data = JSON.parse(text);
            } catch {
                // Si no es JSON, data queda en null
            }

            if (!res.ok) {
                const msg = data?.error || text || `HTTP ${res.status}`;
                throw new Error(msg);
            }

            // Actualizar tiposData con la lista completa devuelta por el servidor
            tiposData = data.tipos || [];
            filteredTipos = [...tiposData];
            currentTipoPage = 1;
            renderTiposPage(currentTipoPage);
            modalTipo.hide();

            Swal.fire({
                icon: "success",
                title: data.message,
                timer: 1500,
                showConfirmButton: false,
            });
        } catch (err) {
            mostrarErrorTipo(err.message || "Error al guardar el tipo.");
            console.error("[ERROR TIPO]", err);
        }
    });

    // ---------- Eliminación de tipo (delegación) ----------
    document.getElementById("tiposBody").addEventListener("click", async (e) => {
        const eliminarBtn = e.target.closest(".btn-tipo-eliminar");
        if (!eliminarBtn) return;

        const id = eliminarBtn.dataset.id;
        const result = await Swal.fire({
            title: "¿Estás seguro?",
            text: "¡No podrás revertir esto!",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
        });

        if (!result.isConfirmed) return;

        try {
            const token = getCsrfToken();
            const res = await fetch(`/jefe_dep/tipo_aplicacion/${id}`, {
                method: "DELETE",
                headers: { "X-CSRFToken": token },
            });

            const text = await res.text();
            let data = null;
            try {
                data = JSON.parse(text);
            } catch {
                // No era JSON
            }

            if (!res.ok) {
                const msg = data?.error || text || `HTTP ${res.status}`;
                throw new Error(msg);
            }

            tiposData = data.tipos || [];
            filteredTipos = [...tiposData];
            currentTipoPage = 1;
            renderTiposPage(currentTipoPage);

            Swal.fire({
                icon: "success",
                title: data.message,
                timer: 1500,
                showConfirmButton: false,
            });
        } catch (err) {
            Swal.fire("Error", err.message || "Error al eliminar el tipo.", "error");
            console.error("[ERROR ELIMINAR TIPO]", err);
        }
    });

    //   ---------- Obtener tipos desde Ajax ----------
    (async () => {
        try {
            const res = await fetch("/jefe_dep/tipo_aplicacion");
            const text = await res.text();
            let data = null;
            try {
                data = JSON.parse(text);
            } catch {
                // No era JSON
            }

            if (!res.ok) {
                const msg = data?.error || text || `HTTP ${res.status}`;
                throw new Error(msg);
            }
            
            tiposData = data.tipos || [];
            filteredTipos = [...tiposData];
            currentTipoPage = 1;
            renderTiposPage(currentTipoPage);
            modalTipo.hide();

        } catch (err) {
            console.error("[ERROR CARGAR TIPOS]", err);
            Swal.fire("Error", "No se pudieron cargar los tipos de aplicación.", "error");
        }
    })();
});
