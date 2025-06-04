document.addEventListener("DOMContentLoaded", () => {
    // ---------- Variables y referencias ----------
    const appsGrid = document.getElementById("appsGrid");
    const appsPagination = document.getElementById("appsPagination");

    const modalElement = document.getElementById("addAppModal");
    const modal = new bootstrap.Modal(modalElement);
    const form = document.querySelector(".form-add-app");
    const formError = document.getElementById("formError");

    const appIdInput = document.getElementById("appId");
    const appNameInput = document.getElementById("appName");
    const appDescInput = document.getElementById("appDescription");
    const appCategorySelect = document.getElementById("appCategory");
    const appVersionInput = document.getElementById("appVersion");

    // Iconos
    const iconItems = Array.from(document.querySelectorAll(".icon-item"));
    const iconGrid = document.getElementById("iconGrid");
    const searchIconInput = document.getElementById("iconSearch");
    const selectedIconInput = document.getElementById("selectedIcon");
    const selectedIconNameDiv = document.getElementById("selectedIconName");

    const iconsPerPage = 5;
    let filteredIconItems = [...iconItems];
    let iconPage = 0;

    // Datos de aplicaciones y paginación
    let appsData = [];
    const pageSize = 3;
    let currentPage = 1;

    // ---------- Funciones auxiliares ----------
    function mostrarError(msg) {
        formError.textContent = msg;
        formError.classList.remove("d-none");
    }
    function ocultarError() {
        formError.textContent = "";
        formError.classList.add("d-none");
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function getCsrfToken() {
        const input = form.querySelector('input[name="csrf_token"]');
        return input ? input.value : "";
    }

    // ---------- Render de iconos (lazy loading + búsqueda) ----------
    function renderIconBatch() {
        iconItems.forEach((item) => (item.style.display = "none"));
        const start = iconPage * iconsPerPage;
        const end = start + iconsPerPage;
        filteredIconItems.slice(start, end).forEach((item) => {
            item.style.display = "inline-block";
        });

        const existingNav = iconGrid.querySelector(".icon-nav");
        if (existingNav) existingNav.remove();

        if (filteredIconItems.length > iconsPerPage) {
            const nav = document.createElement("div");
            nav.className = "icon-nav d-flex justify-content-between mt-2";

            const prevBtn = document.createElement("button");
            prevBtn.type = "button";
            prevBtn.className = "btn btn-sm btn-outline-secondary";
            prevBtn.textContent = "←";
            prevBtn.disabled = iconPage === 0;
            prevBtn.addEventListener("click", () => {
                iconPage--;
                renderIconBatch();
            });

            const nextBtn = document.createElement("button");
            nextBtn.type = "button";
            nextBtn.className = "btn btn-sm btn-outline-secondary";
            nextBtn.textContent = "→";
            nextBtn.disabled =
                (iconPage + 1) * iconsPerPage >= filteredIconItems.length;
            nextBtn.addEventListener("click", () => {
                iconPage++;
                renderIconBatch();
            });

            nav.appendChild(prevBtn);
            nav.appendChild(nextBtn);
            iconGrid.appendChild(nav);
        }
    }

    searchIconInput.addEventListener("input", function () {
        const q = this.value.toLowerCase();
        filteredIconItems = iconItems.filter((item) => {
            return item.dataset.icon.toLowerCase().includes(q);
        });
        iconPage = 0;
        renderIconBatch();
    });

    iconGrid.addEventListener("click", function (e) {
        const clicked = e.target.closest(".icon-item");
        if (!clicked) return;
        iconItems.forEach((item) =>
            item.classList.remove("bg-primary", "text-white")
        );
        clicked.classList.add("bg-primary", "text-white");
        const iconName = clicked.dataset.icon;
        selectedIconInput.value = iconName;
        selectedIconNameDiv.textContent = `Ícono seleccionado: ${iconName}`;
    });

    renderIconBatch();

    // ---------- Render de una página de apps ----------
    function renderAppsPage(page) {
        const start = (page - 1) * pageSize;
        const end = start + pageSize;
        const slice = appsData.slice(start, end);

        if (!slice.length) {
            appsGrid.innerHTML = `
        <div class="col-12">
          <div class="alert alert-info text-center mb-0">
            No hay aplicaciones registradas.
          </div>
        </div>`;
        } else {
            appsGrid.innerHTML = slice
                .map((app) => {
                    return `
          <div class="col-md-4 mb-4" data-app-id="${app.id}">
            <div class="app-card shadow-sm h-100">
              <div class="app-card-header d-flex justify-content-between align-items-center p-2">
                <div class="app-icon bg-primary">
                  <i class="bi bi-${escapeHtml(app.icono)}"></i>
                </div>
                <div class="app-actions dropdown">
                  <button class="btn btn-sm btn-icon" data-bs-toggle="dropdown">
                    <i class="bi bi-three-dots-vertical"></i>
                  </button>
                  <ul class="dropdown-menu dropdown-menu-end">
                    <li>
                      <a
                        class="dropdown-item btn-app-editar"
                        href="#"
                        data-bs-toggle="modal"
                        data-bs-target="#addAppModal"
                        data-id="${app.id}"
                        data-nombre="${escapeHtml(app.nombre)}"
                        data-descripcion="${escapeHtml(app.descripcion)}"
                        data-tipo="${app.tipo_aplicacion_id}"
                        data-version="${escapeHtml(app.version)}"
                        data-icono="${escapeHtml(app.icono)}"
                      >
                        <i class="bi bi-pencil me-2"></i>Editar
                      </a>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                      <a
                        class="dropdown-item text-danger btn-app-eliminar"
                        href="#"
                        data-id="${app.id}"
                      >
                        <i class="bi bi-trash me-2"></i>Eliminar
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
              <div class="app-card-body p-3">
                <h5 class="app-name">${escapeHtml(app.nombre)}</h5>
                <p class="app-description mb-1">${escapeHtml(app.descripcion)}</p>
                <div class="app-meta d-flex justify-content-between small text-muted">
                  <span>
                    <i class="bi bi-tag me-1"></i>${escapeHtml(app.categoria || "")}
                  </span>
                  <span>
                    <i class="bi bi-code-slash me-1"></i>${escapeHtml(app.version)}
                  </span>
                </div>
              </div>
            </div>
          </div>`;
                })
                .join("");
        }

        renderPagination();
    }

    // ---------- Render de controles de paginación ----------
    function renderPagination() {
        const totalPages = Math.ceil(appsData.length / pageSize);
        appsPagination.innerHTML = "";

        if (totalPages <= 1) return;

        const isSmall = window.innerWidth < 768;
        appsPagination.classList.toggle("flex-column", isSmall);

        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            li.className = "page-item" + (i === currentPage ? " active" : "");
            const a = document.createElement("a");
            a.className = "page-link";
            a.href = "#";
            a.textContent = i;
            a.addEventListener("click", (e) => {
                e.preventDefault();
                if (i === currentPage) return;
                currentPage = i;
                renderAppsPage(currentPage);
            });
            li.appendChild(a);
            appsPagination.appendChild(li);
        }
    }


    // ---------- Manejo del modal para crear/editar aplicación ----------
    modalElement.addEventListener("show.bs.modal", (event) => {
        const button = event.relatedTarget;
        const titleEl = modalElement.querySelector(".modal-title");
        ocultarError();

        if (button && button.classList.contains("btn-app-editar")) {
            titleEl.textContent = "Editar Aplicación";

            const id = button.dataset.id;
            const nombre = button.dataset.nombre;
            const descripcion = button.dataset.descripcion;
            const tipo = button.dataset.tipo;
            const version = button.dataset.version;
            const icono = button.dataset.icono;

            appIdInput.value = id;
            appNameInput.value = nombre;
            appDescInput.value = descripcion;
            appCategorySelect.value = tipo;
            appVersionInput.value = version;

            iconItems.forEach((item) =>
                item.classList.remove("bg-primary", "text-white")
            );
            const selectedDiv = iconItems.find((it) => it.dataset.icon === icono);
            if (selectedDiv) {
                selectedDiv.classList.add("bg-primary", "text-white");
                selectedIconInput.value = icono;
                selectedIconNameDiv.textContent = `Ícono seleccionado: ${icono}`;
            } else {
                selectedIconInput.value = "";
                selectedIconNameDiv.textContent = "";
            }
        } else {
            titleEl.textContent = "Nueva Aplicación";
            appIdInput.value = "";
            form.reset();
            iconItems.forEach((item) =>
                item.classList.remove("bg-primary", "text-white")
            );
            selectedIconInput.value = "";
            selectedIconNameDiv.textContent = "";
        }
    });

    // ---------- Envío del formulario AJAX para crear/editar ----------
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        ocultarError();

        const id = appIdInput.value.trim();
        const nombre = appNameInput.value.trim();
        const descripcion = appDescInput.value.trim();
        const tipoId = appCategorySelect.value;
        const version = appVersionInput.value.trim();
        const icono = selectedIconInput.value;

        if (!nombre) {
            mostrarError("El nombre de la aplicación es requerido.");
            return;
        }
        if (!descripcion) {
            mostrarError("La descripción es requerida.");
            return;
        }
        if (!tipoId) {
            mostrarError("El tipo de aplicación es requerido.");
            return;
        }
        if (!icono) {
            mostrarError("Debe seleccionar un ícono.");
            return;
        }

        const urlBase = "/jefe_dep/aplicacion";
        const url = id ? `${urlBase}/${id}` : urlBase;
        const method = id ? "PUT" : "POST";
        const token = getCsrfToken();

        const payload = {
            nombre,
            descripcion,
            tipo_aplicacion_id: tipoId,
            version,
            icono,
        };

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
                // no era JSON
            }

            if (!res.ok) {
                const msg = data?.error || text || `HTTP ${res.status}`;
                throw new Error(msg);
            }

            appsData = data.apps || [];
            currentPage = 1;
            renderAppsPage(currentPage);
            modal.hide();

            Swal.fire({
                icon: "success",
                title: data.message,
                timer: 2000,
                showConfirmButton: false,
            });
        } catch (err) {
            mostrarError(err.message || "Error al guardar la aplicación.");
            console.error("[ERROR APP]", err);
        }
    });

    // ---------- Eliminación y edición desde grid (delegación) ----------
    appsGrid.addEventListener("click", async (e) => {
        const editarBtn = e.target.closest(".btn-app-editar");
        const eliminarBtn = e.target.closest(".btn-app-eliminar");

        if (editarBtn) {
            // Bootstrap abrirá el modal gracias a data-bs-toggle / data-bs-target
            return;
        }
        if (eliminarBtn) {
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

            if (result.isConfirmed) {
                try {
                    const token = getCsrfToken();
                    const res = await fetch(`/jefe_dep/aplicacion/${id}`, {
                        method: "DELETE",
                        headers: { "X-CSRFToken": token },
                    });

                    const text = await res.text();
                    let data = null;
                    try {
                        data = JSON.parse(text);
                    } catch { }

                    if (!res.ok) {
                        const msg = data?.error || text || `HTTP ${res.status}`;
                        throw new Error(msg);
                    }

                    appsData = data.apps || [];
                    currentPage = 1;
                    renderAppsPage(currentPage);

                    Swal.fire({
                        icon: "success",
                        title: data.message,
                        timer: 2000,
                        showConfirmButton: false,
                    });
                } catch (err) {
                    Swal.fire(
                        "Error",
                        err.message || "Error al eliminar la aplicación.",
                        "error"
                    );
                    console.error("[ERROR ELIMINAR APP]", err);
                }
            }
        }
    });

    // ---------- Buscador de aplicaciones (filtro) ----------
    const searchAppForm = document.getElementById("searchAppForm");
    const searchAppInput = document.getElementById("searchAppInput");

    // ¿Cómo pongo "mas" de un eventListener?

    async function handleAppSearch(e) {
        e.preventDefault();
        const q = searchAppInput.value.trim().toLowerCase();
        const url = `/jefe_dep/aplicacion?search=${encodeURIComponent(q)}`;
        try {
            const res = await fetch(url, { method: "GET" });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);

            appsData = data.apps || [];
            currentPage = 1;
            renderAppsPage(currentPage);
        } catch (err) {
            console.error("[ERROR BUSCAR APP]", err);
            Swal.fire("Error", "Error al buscar aplicaciones.", "error");
        }
    }

    searchAppForm.addEventListener("change", handleAppSearch);
    searchAppForm.addEventListener("submit", handleAppSearch);

    // ---------- Carga inicial de aplicaciones ----------
    (async function loadInitialApps() {
        try {
            const res = await fetch("/jefe_dep/aplicacion", { method: "GET" });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
            appsData = data.apps || [];
            currentPage = 1;
            renderAppsPage(currentPage);
        } catch (err) {
            console.error("[ERROR INICIAL APP]", err);
        }
    })();
});
