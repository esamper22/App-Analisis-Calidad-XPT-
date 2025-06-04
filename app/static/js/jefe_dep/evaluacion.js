document.addEventListener("DOMContentLoaded", () => {
  // ---------- Referencias a elementos del DOM ----------
  const evaluationsBody        = document.getElementById("evaluationsBody");
  const evaluationsPagination  = document.getElementById("evaluationsPagination");
  const searchEvalInput        = document.getElementById("searchEvaluationsInput");
  const clearSearchEvalBtn     = document.getElementById("clearSearchEval");
  const addEvalBtn             = document.getElementById("addEvalBtn");
  const evalModalElement       = document.getElementById("addEvaluationModal");
  const evalModal              = new bootstrap.Modal(evalModalElement);
  const evalForm               = document.getElementById("evaluationForm");
  const formErrorEval          = document.createElement("div");
  const evalIdInput            = document.getElementById("evaluationId");
  const appSearchInput         = document.getElementById("appSearch");
  const appSelect              = document.getElementById("appSelect");
  const paramSelect            = document.getElementById("paramSelect");
  const evaluadorSearchInput   = document.getElementById("evaluadorSearch");
  const evaluadoresSelect      = document.getElementById("evaluadoresSelect");
  const selectAllParamsBtn     = document.getElementById("selectAllParams");
  const clearAllParamsBtn      = document.getElementById("clearAllParams");
  const parametrosContainer    = document.getElementById("parametrosContainer");
  const fechaInicioInput       = document.getElementById("fechaInicio");
  const fechaFinInput          = document.getElementById("fechaFin");
  const comentariosInput       = document.getElementById("comentarios");

  // Inserta contenedor de errores en el modal (antes del primer campo)
  formErrorEval.className = "text-danger small px-4 mb-2 d-none";
  evalModalElement.querySelector(".modal-body").prepend(formErrorEval);

  // Datos y paginación
  let evaluationsData     = [];
  let filteredEvaluations = [];
  const pageSize          = 5;
  let currentPage         = 1;

  // ---------- Funciones Auxiliares ----------
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
  function mostrarErrorEval(msg) {
    formErrorEval.textContent = msg;
    formErrorEval.classList.remove("d-none");
  }
  function ocultarErrorEval() {
    formErrorEval.textContent = "";
    formErrorEval.classList.add("d-none");
  }
  function getCsrfToken() {
    const input = evalForm.querySelector('input[name="csrf_token"]');
    return input ? input.value : "";
  }
  function formatDate(d) {
    if (!d) return "";
    const date = new Date(d);
    if (isNaN(date)) return d;
    return date.toISOString().slice(0, 10);
  }

  // ---------- Render Tabla y Paginación ----------
  function renderEvaluationsPage(page) {
    const start = (page - 1) * pageSize;
    const end   = start + pageSize;
    const slice = filteredEvaluations.slice(start, end);

    if (!slice.length) {
      evaluationsBody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center">No hay evaluaciones.</td>
        </tr>`;
    } else {
      evaluationsBody.innerHTML = slice.map((ev, idx) => {
        const num = start + idx + 1;
        const badgeClass =
          ev.estado === "pendiente"    ? "bg-warning text-dark" :
          ev.estado === "en progreso"  ? "bg-info text-dark"    :
          ev.estado === "completada"   ? "bg-success text-white" :
          "bg-secondary text-white";
        return `
          <tr data-eval-id="${ev.id}">
            <th scope="row">${num}</th>
            <td>${escapeHtml(ev.aplicacion_nombre)}</td>
            <td>${escapeHtml(ev.parametro_nombre)}</td>
            <td><span class="badge ${badgeClass} text-capitalize">${ev.estado.replace("_", " ")}</span></td>
            <td>${formatDate(ev.fecha_inicio)}</td>
            <td>${formatDate(ev.fecha_fin)}</td>
            <td>
              <button class="btn btn-outline-secondary btn-sm rounded-circle me-2 btn-eval-edit"
                      title="Editar"
                      data-id="${ev.id}"
                      data-aplicacion-id="${ev.aplicacion_id}"
                      data-parametro-id="${ev.parametro_id}"
                      data-estado="${ev.estado}"
                      data-fecha-inicio="${ev.fecha_inicio}"
                      data-fecha-fin="${ev.fecha_fin}">
                <i class="bi bi-pencil-fill"></i>
              </button>
              <button class="btn btn-outline-danger btn-sm rounded-circle btn-eval-delete"
                      title="Eliminar"
                      data-id="${ev.id}">
                <i class="bi bi-trash-fill"></i>
              </button>
            </td>
          </tr>`;
      }).join("");
    }
    renderEvaluationsPagination();
  }

  function renderEvaluationsPagination() {
    const totalPages = Math.ceil(filteredEvaluations.length / pageSize);
    evaluationsPagination.innerHTML = "";
    if (totalPages <= 1) return;

    const isSmall = window.innerWidth < 768;
    evaluationsPagination.classList.toggle("flex-column", isSmall);

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
        renderEvaluationsPage(currentPage);
      });
      li.appendChild(a);
      evaluationsPagination.appendChild(li);
    }
  }

  // ---------- Filtrado en tiempo real ----------
  searchEvalInput.addEventListener("input", () => {
    const q = searchEvalInput.value.trim().toLowerCase();
    filteredEvaluations = evaluationsData.filter(ev =>
      ev.aplicacion_nombre.toLowerCase().includes(q) ||
      ev.parametro_nombre.toLowerCase().includes(q)
    );
    currentPage = 1;
    renderEvaluationsPage(currentPage);
  });
  clearSearchEvalBtn.addEventListener("click", () => {
    searchEvalInput.value = "";
    filteredEvaluations = [...evaluationsData];
    currentPage = 1;
    renderEvaluationsPage(currentPage);
  });

  // ---------- Modal: Mostrar datos en Crear/Editar ----------
  evalModalElement.addEventListener("show.bs.modal", (event) => {
    ocultarErrorEval();
    const btn = event.relatedTarget;
    const title = evalModalElement.querySelector(".modal-title");

    if (btn === addEvalBtn) {
      // Modo CREAR
      title.textContent = "Nueva Evaluación";
      evalIdInput.value       = "";
      appSelect.value         = "";
      paramSelect.value       = "";
      estadoSelect.value      = "pendiente";
      fechaInicioInput.value  = "";
      fechaFinInput.value     = "";
      // Deseleccionar todos evaluadores
      Array.from(evaluadoresSelect.options).forEach(opt => opt.selected = false);
      // Deseleccionar todos parámetros
      Array.from(parametrosContainer.querySelectorAll("input[type=checkbox]"))
        .forEach(chk => { chk.checked = false; });
    } else if (btn.classList.contains("btn-eval-edit")) {
      // Modo EDITAR
      title.textContent = "Editar Evaluación";
      const id             = btn.dataset.id;
      const aplicacion_id  = btn.dataset.aplicacionId;
      const parametro_id   = btn.dataset.parametroId;
      const estado_val     = btn.dataset.estado;
      const inicio         = btn.dataset.fechaInicio?.substr(0,10) || "";
      const fin            = btn.dataset.fechaFin?.substr(0,10) || "";

      evalIdInput.value      = id;
      appSelect.value        = aplicacion_id;
      paramSelect.value      = parametro_id;
      estadoSelect.value     = estado_val;
      fechaInicioInput.value = inicio;
      fechaFinInput.value    = fin;
      // Evaluadores no cambian al editar, se asume que solo se edita estado o fechas
    }
  });

  // ---------- Botones "Seleccionar todos" / "Deseleccionar" parámetros ----------
  selectAllParamsBtn.addEventListener("click", () => {
    parametrosContainer.querySelectorAll("input[type=checkbox]")
      .forEach(chk => chk.checked = true);
  });
  clearAllParamsBtn.addEventListener("click", () => {
    parametrosContainer.querySelectorAll("input[type=checkbox]")
      .forEach(chk => chk.checked = false);
  });

  // ---------- Guardar (Crear / Actualizar) via AJAX ----------
  evalForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    ocultarErrorEval();

    const id             = evalIdInput.value.trim();
    const aplicacionId   = appSelect.value;
    const parametroId    = paramSelect.value;
    const evaluadoresIds = Array.from(evaluadoresSelect.selectedOptions).map(o => o.value);
    const selectedParams = Array.from(parametrosContainer.querySelectorAll("input[type=checkbox]:checked"))
                                .map(chk => chk.value);
    const estadoVal      = estadoSelect.value;
    const inicioVal      = fechaInicioInput.value;
    const finVal         = fechaFinInput.value;
    const comentariosVal = comentariosInput.value.trim();

    // Validaciones rápidas
    if (!aplicacionId) {
      mostrarErrorEval("Selecciona la aplicación a evaluar.");
      return;
    }
    if (!parametroId) {
      mostrarErrorEval("Selecciona un parámetro.");
      return;
    }
    if (!evaluadoresIds.length) {
      mostrarErrorEval("Elige al menos un evaluador.");
      return;
    }
    if (!selectedParams.length) {
      mostrarErrorEval("Selecciona al menos un parámetro de evaluación.");
      return;
    }
    if (!inicioVal) {
      mostrarErrorEval("Selecciona la fecha de inicio.");
      return;
    }
    if (!finVal) {
      mostrarErrorEval("Selecciona la fecha de fin.");
      return;
    }
    if (new Date(finVal) < new Date(inicioVal)) {
      mostrarErrorEval("La fecha de fin no puede ser anterior a la fecha de inicio.");
      return;
    }

    const payload = {
      aplicacion_id:  parseInt(aplicacionId),
      parametro_id:   parseInt(parametroId),
      evaluadores:    evaluadoresIds.map(v => parseInt(v)),
      parametros:     selectedParams.map(v => parseInt(v)),
      estado:         estadoVal,
      fecha_inicio:   inicioVal,
      fecha_fin:      finVal,
      comentarios:    comentariosVal
    };
    const urlBase = "/jefe_dep/evaluacion";
    const url     = id ? `${urlBase}/${id}` : urlBase;
    const method  = id ? "PUT" : "POST";

    try {
      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken()
        },
        body: JSON.stringify(payload)
      });
      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch {}

      if (!res.ok) {
        const errMsg = data?.error || text || `HTTP ${res.status}`;
        throw new Error(errMsg);
      }

      evaluationsData     = data.evaluaciones || [];
      filteredEvaluations = [...evaluationsData];
      currentPage         = 1;
      renderEvaluationsPage(currentPage);
      evalModal.hide();

      Swal.fire({
        icon: "success",
        title: data.message,
        timer: 1500,
        showConfirmButton: false
      });
    } catch (err) {
      mostrarErrorEval(err.message || "Error al guardar la evaluación.");
      console.error("[ERROR GUARDAR EVALUACIÓN]", err);
    }
  });

  // ---------- Eliminar Evaluación ----------
  evaluationsBody.addEventListener("click", async (e) => {
    const btnDel = e.target.closest(".btn-eval-delete");
    if (!btnDel) return;

    const id = btnDel.dataset.id;
    const result = await Swal.fire({
      title: "¿Estás seguro?",
      text: "¡No podrás revertir esta acción!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar"
    });
    if (!result.isConfirmed) return;

    try {
      const res = await fetch(`/jefe_dep/evaluacion/${id}`, {
        method: "DELETE",
        headers: { "X-CSRFToken": getCsrfToken() }
      });
      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch {}

      if (!res.ok) {
        const errMsg = data?.error || text || `HTTP ${res.status}`;
        throw new Error(errMsg);
      }

      evaluationsData     = data.evaluaciones || [];
      filteredEvaluations = [...evaluationsData];
      currentPage         = 1;
      renderEvaluationsPage(currentPage);

      Swal.fire({
        icon: "success",
        title: data.message,
        timer: 1500,
        showConfirmButton: false
      });
    } catch (err) {
      Swal.fire("Error", err.message || "Error al eliminar la evaluación.", "error");
      console.error("[ERROR ELIMINAR EVALUACIÓN]", err);
    }
  });

  // ---------- Cargar Evaluaciones Iniciales ----------
  (async () => {
    try {
      const res  = await fetch("/jefe_dep/evaluacion");
      const text = await res.text();
      let data   = null;
      try { data = JSON.parse(text); } catch {}

      if (!res.ok) throw new Error(data?.message || text || `HTTP ${res.status}`);

      evaluationsData     = data.evaluaciones || [];
      filteredEvaluations = [...evaluationsData];
      renderEvaluationsPage(currentPage);
    } catch (err) {
      console.error("[ERROR CARGA INICIAL EVALUACIONES]", err);
      Swal.fire("Error", "No se pudieron cargar las evaluaciones.", "error");
    }
  })();

  // ---------- Búsquedas dentro de Selects (filtrar opciones) ----------
  appSearchInput.addEventListener("input", () => {
    const f = appSearchInput.value.toLowerCase();
    Array.from(appSelect.options).forEach(opt => {
      if (!opt.value) return;
      opt.style.display = opt.text.toLowerCase().includes(f) ? "" : "none";
    });
  });
  evaluadorSearchInput.addEventListener("input", () => {
    const f = evaluadorSearchInput.value.toLowerCase();
    Array.from(evaluadoresSelect.options).forEach(opt => {
      opt.style.display = opt.text.toLowerCase().includes(f) ? "" : "none";
    });
  });
});
