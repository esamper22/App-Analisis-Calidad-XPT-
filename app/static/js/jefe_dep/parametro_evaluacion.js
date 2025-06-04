document.addEventListener("DOMContentLoaded", () => {
    // ---------- Referencias y variables ----------
    const parametrosGridBody = document.getElementById("parametrosBody");
    const parametrosPagination = document.getElementById("parametrosPagination");
    const searchParametroInput = document.getElementById("searchParametroInput");

    let modalParametro;
    const modalElement = document.getElementById("addParametroModal");
    if (modalElement) {
        modalParametro = new bootstrap.Modal(modalElement);
    }

    const parametroForm = document.getElementById("parametroForm");
    const formErrorParametro = document.getElementById("formErrorParametro");

    const parametroIdInput = document.getElementById("parametroId");
    const parametroNombreInput = document.getElementById("parametroNombre");
    const parametroDescInput = document.getElementById("parametroDescripcion");

    // Datos iniciales
    let parametrosData = [];
    let filteredParametros = [...parametrosData];
    const pageSizeParametros = 5;
    let currentParametroPage = 1;

    // Botón para agregar nuevas filas de pesos y estados
    const container = document.getElementById('pesosEstadosContainer');
    const addBtn = document.getElementById('addPesoEstadoBtn');
    const modal = document.getElementById('addParametroModal');

    // ---------- Funciones auxiliares ----------
    function mostrarErrorParametro(msg) {
        formErrorParametro.textContent = msg;
        formErrorParametro.classList.remove("d-none");
    }
    function ocultarErrorParametro() {
        formErrorParametro.textContent = "";
        formErrorParametro.classList.add("d-none");
    }
    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
    function getCsrfToken() {
        const input = parametroForm.querySelector('input[name="csrf_token"]');
        return input ? input.value : "";
    }

    // ---------- Render de una página de parámetros ----------
    function renderParametrosPage(page) {
        const start = (page - 1) * pageSizeParametros;
        const end = start + pageSizeParametros;
        const slice = filteredParametros.slice(start, end);

        if (!slice.length) {
            parametrosGridBody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center">No hay parámetros registrados.</td>
                </tr>`;
        } else {
            parametrosGridBody.innerHTML = slice.map((parametro, idx) => {
                const globalIndex = start + idx + 1;
                return `
                    <tr data-parametro-id="${parametro.id}">
                        <th scope="row">${globalIndex}</th>
                        <td>${escapeHtml(parametro.nombre)}</td>
                        <td>${escapeHtml(parametro.descripcion || '')}</td>
                        <td>
                            <button
                                class="btn btn-outline-primary btn-sm rounded-circle me-2 btn-parametro-editar"
                                style="width: 28px; height: 28px;"
                                title="Editar"
                                data-id="${parametro.id}"
                                data-nombre="${escapeHtml(parametro.nombre)}"
                                data-descripcion="${escapeHtml(parametro.descripcion || '')}"
                                data-pesos="${JSON.stringify(parametro.pesos || [])}"
                                data-estados='${escapeHtml(JSON.stringify(Array.isArray(parametro.estados) ? parametro.estados : []))}'
                                data-bs-toggle="modal"
                                data-bs-target="#addParametroModal"
                            >
                                <i class="bi bi-pencil-fill"></i>
                            </button>
                            <button
                                class="btn btn-outline-danger btn-sm rounded-circle btn-parametro-eliminar"
                                style="width: 28px; height: 28px;"
                                title="Eliminar"
                                data-id="${parametro.id}"
                            >
                                <i class="bi bi-trash-fill"></i>
                            </button>
                        </td>
                    </tr>`;
            }).join("");
        }

        renderParametrosPagination();
    }

    // ---------- Paginación ----------
    function renderParametrosPagination() {
        const totalPages = Math.ceil(filteredParametros.length / pageSizeParametros);
        parametrosPagination.innerHTML = "";

        if (totalPages <= 1) return;

        const isSmall = window.innerWidth < 768;
        parametrosPagination.classList.toggle("flex-column", isSmall);

        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            li.className = "page-item" + (i === currentParametroPage ? " active" : "");
            const a = document.createElement("a");
            a.className = "page-link";
            a.href = "#";
            a.textContent = i;
            a.addEventListener("click", (e) => {
                e.preventDefault();
                if (i === currentParametroPage) return;
                currentParametroPage = i;
                renderParametrosPage(currentParametroPage);
            });
            li.appendChild(a);
            parametrosPagination.appendChild(li);
        }
    }

    // ---------- Filtro ----------
    searchParametroInput.addEventListener("input", () => {
        const q = searchParametroInput.value.trim().toLowerCase();
        filteredParametros = parametrosData.filter((p) =>
            p.nombre.toLowerCase().includes(q)
        );
        currentParametroPage = 1;
        renderParametrosPage(currentParametroPage);
    });

    // ---------- Editar ----------
    parametrosGridBody.addEventListener("click", (e) => {
        const button = e.target.closest(".btn-parametro-editar");
        if (button) {
            console.log(`data -pesos: ${button.dataset.pesos}`);
            console.log(`data -estados: ${button.dataset.estados}`);

            modalElement.querySelector(".modal-title").textContent = "Editar Parámetro de Evaluación";
            parametroIdInput.value = button.dataset.id;
            parametroNombreInput.value = button.dataset.nombre;
            parametroDescInput.value = button.dataset.descripcion;

            const pesos = JSON.parse(button.dataset.pesos || "[]");
            let estados = [];
            try {
                estados = JSON.parse(button.dataset.estados || "[]");
            } catch {
                estados = [];
            }

            const container = document.getElementById("pesosEstadosContainer");
            container.innerHTML = "";
            for (let i = 0; i < pesos.length; i++) {
                container.appendChild(createRow(pesos[i], estados[i] || ""));
            }
        }
    });

    // ---------- Nuevo ----------
    document.getElementById("addParametroBtn")?.addEventListener("click", () => {
        modalElement.querySelector(".modal-title").textContent = "Nuevo Parámetro de Evaluación";
        parametroIdInput.value = "";
        parametroForm.reset();
        document.getElementById("pesosEstadosContainer").innerHTML = "";
        document.getElementById("pesosEstadosContainer").appendChild(createRow());
    });

    // ---------- Guardar ----------
    parametroForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        ocultarErrorParametro();

        const id = parametroIdInput.value.trim();
        const nombre = parametroNombreInput.value.trim();
        const descripcion = parametroDescInput.value.trim();

        const pesos = Array.from(document.getElementsByName("pesos[]")).map(input => input.value.trim());
        const estados = Array.from(document.getElementsByName("estados[]")).map(input => input.value.trim());

        if (!nombre) {
            mostrarErrorParametro("El nombre es obligatorio.");
            return;
        }

        if (pesos.length !== estados.length || pesos.length === 0) {
            mostrarErrorParametro("Debe agregar al menos un peso y estado.");
            return;
        }

        const payload = { nombre, descripcion, pesos, estados };
        const urlBase = "/jefe_dep/parametro_evaluacion";
        const url = id ? `${urlBase}/${id}` : urlBase;
        const method = id ? "PUT" : "POST";

        try {
            const res = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify(payload),
            });

            const text = await res.text();
            let data = null;
            try { data = JSON.parse(text); } catch { }

            if (!res.ok) {
                const msg = data?.error || text || `HTTP ${res.status}`;
                throw new Error(msg);
            }

            parametrosData = data.parametros || [];
            filteredParametros = [...parametrosData];
            currentParametroPage = 1;
            renderParametrosPage(currentParametroPage);
            modalParametro.hide();

            Swal.fire({
                icon: "success",
                title: data.message,
                timer: 1500,
                showConfirmButton: false,
            });
        } catch (err) {
            mostrarErrorParametro(err.message || "Error al guardar el parámetro.");
            console.error("[ERROR GUARDAR]", err);
        }
    });

    // ---------- Eliminar ----------
    parametrosGridBody.addEventListener("click", async (e) => {
        const eliminarBtn = e.target.closest(".btn-parametro-eliminar");
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
            const res = await fetch(`/jefe_dep/parametro_evaluacion/${id}`, {
                method: "DELETE",
                headers: { "X-CSRFToken": getCsrfToken() },
            });

            const text = await res.text();
            let data = null;
            try { data = JSON.parse(text); } catch { }

            if (!res.ok) {
                const msg = data?.error || text || `HTTP ${res.status}`;
                throw new Error(msg);
            }

            parametrosData = data.parametros || [];
            filteredParametros = [...parametrosData];
            currentParametroPage = 1;
            renderParametrosPage(currentParametroPage);

            Swal.fire({
                icon: "success",
                title: data.message,
                timer: 1500,
                showConfirmButton: false,
            });
        } catch (err) {
            Swal.fire("Error", err.message || "Error al eliminar el parámetro.", "error");
            console.error("[ERROR ELIMINAR]", err);
        }
    });

    // ---------- Cargar al iniciar ----------
    (async () => {
        try {
            const res = await fetch("/jefe_dep/parametro_evaluacion");
            const text = await res.text();
            let data = null;
            try { data = JSON.parse(text); } catch { }

            if (!res.ok) throw new Error(data?.error || text || `HTTP ${res.status}`);

            parametrosData = data.parametros || [];
            filteredParametros = [...parametrosData];
            renderParametrosPage(currentParametroPage);
        } catch (err) {
            console.error("[ERROR CARGA INICIAL]", err);
            Swal.fire("Error", "No se pudieron cargar los parámetros.", "error");
        }
    })();

    // ---------- Función auxiliar (la misma del HTML previo) ----------

    function createRow(peso = '', estado = '') {
        const row = document.createElement('div');
        row.className = 'd-flex align-items-end mb-2 gap-2 fade-in';

        const pesoInput = document.createElement('input');
        pesoInput.type = 'number';
        pesoInput.className = 'form-control shadow-sm';
        pesoInput.name = 'pesos[]';
        pesoInput.placeholder = 'Peso Ej:(2)';
        pesoInput.required = true;
        pesoInput.min = 1;
        pesoInput.max = 10;
        pesoInput.step = 0.01;
        pesoInput.value = peso;

        const estadoInput = document.createElement('input');
        estadoInput.type = 'text';
        estadoInput.className = 'form-control shadow-sm';
        estadoInput.name = 'estados[]';
        estadoInput.placeholder = 'Estado Ej: (mal)';
        estadoInput.required = true;
        estadoInput.value = estado;

        const delBtn = document.createElement('button');
        delBtn.type = 'button';
        delBtn.className = 'btn btn-outline-danger btn-sm ms-1';
        delBtn.title = 'Eliminar fila';
        delBtn.innerHTML = '<i class="bi bi-trash"></i>';
        delBtn.onclick = () => row.remove();

        row.appendChild(pesoInput);
        row.appendChild(estadoInput);
        row.appendChild(delBtn);

        return row;
    }

    addBtn.addEventListener('click', function () {
        container.appendChild(createRow());
    });

    // Cada vez que se muestra el modal, se reinician las filas
    modal.addEventListener('show.bs.modal', function () {
        container.innerHTML = '';
        container.appendChild(createRow());
    });

});
