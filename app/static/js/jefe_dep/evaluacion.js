// evaluacion.js
document.addEventListener("DOMContentLoaded", () => {
  // ---------- Referencias a elementos del DOM ----------
  const evaluationsBody = document.getElementById("evaluationsBody");
  const evaluationsPagination = document.getElementById("evaluationsPagination");
  const searchEvalInput = document.getElementById("searchEvaluationsInput");
  const clearSearchEvalBtn = document.getElementById("clearSearchEval");
  const addEvalBtn = document.getElementById("addEvalBtn");
  const evalModalElement = document.getElementById("addEvaluationModal");
  const evalModal = new bootstrap.Modal(evalModalElement);
  const evalForm = document.getElementById("evaluationForm");
  const formErrorEval = document.createElement("div");
  const evalIdInput = document.getElementById("evaluationId");
  const appSearchInput = document.getElementById("appSearch");
  const appSelect = document.getElementById("appSelect");
  const evaluadorSearchInput = document.getElementById("evaluadorSearch");
  const evaluadoresSelect = document.getElementById("evaluadoresSelect");
  const selectAllParamsBtn = document.getElementById("selectAllParams");
  const clearAllParamsBtn = document.getElementById("clearAllParams");
  const parametrosContainer = document.getElementById("parametrosContainer");
  const fechaInicioInput = document.getElementById("fechaInicio");
  const fechaFinInput = document.getElementById("fechaFin");
  const rondasInput = document.getElementById("rondas");
  const comentariosInput = document.getElementById("comentarios");

  // Insertar contenedor de errores en el modal (antes del primer campo)
  formErrorEval.className = "text-danger small px-4 mb-2 d-none";
  evalModalElement.querySelector(".modal-body").prepend(formErrorEval);

  // Datos y paginación
  let evaluationsData = [];
  let filteredEvaluations = [];
  const pageSize = 5;
  let currentPage = 1;

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
    const end = start + pageSize;
    const slice = filteredEvaluations.slice(start, end);

    if (!slice.length) {
      evaluationsBody.innerHTML = `
        <tr>
          <td colspan="8" class="text-center">No hay evaluaciones.</td>
        </tr>`;
    } else {
      evaluationsBody.innerHTML = slice.map((ev, idx) => {
        const num = start + idx + 1;
        const badgeClass =
          ev.estado === "pendiente" ? "bg-warning text-dark" :
            ev.estado === "en progreso" ? "bg-info text-dark" :
              ev.estado === "completada" ? "bg-success text-white" :
                "bg-secondary text-white";
        // Concatenar nombres de parámetros y usuarios
        const paramLabels = `${ev.parametros.length} Parametros`  // ev.parametros.map(p => `<span class="badge bg-light text-dark me-1">${escapeHtml(p.nombre)}</span>`).join("");
        const userLabels = `${ev.usuarios.length} Expertos` // ev.usuarios.map(u => `<span class="badge bg-light text-dark me-1">${escapeHtml(u.nombre_completo)}</span>`).join("");

        return `
          <tr data-eval-id="${ev.id}"
              data-aplicacion-id="${ev.aplicacion_id}"
              data-estado="${ev.estado}"
              data-fecha-inicio="${ev.fecha_inicio}"
              data-fecha-fin="${ev.fecha_fin}"
              data-rondas="${ev.rondas}"
              data-comentarios="${escapeHtml(ev.comentarios || "")}"
              data-parametros='${JSON.stringify(ev.parametros.map(p => p.id))}'
              data-usuarios='${JSON.stringify(ev.usuarios.map(u => u.id))}'>
            <th scope="row">${num}</th>
            <td>${escapeHtml("ID: " + ev.aplicacion_id)}</td>
            <td>${paramLabels}</td>
            <td>${userLabels}</td>
            <td><span class="badge ${badgeClass} text-capitalize">${ev.estado.replace("_", " ")}</span></td>
            <td>${formatDate(ev.fecha_inicio)}</td>
            <td>${formatDate(ev.fecha_fin)}</td>
            <td>
              <button class="btn btn-outline-secondary btn-sm rounded-circle me-2 btn-eval-edit"
  title="Editar"
  data-id="${ev.id}">
  <i class="bi bi-pencil-fill"></i>
</button>

              <button class="btn btn-outline-success btn-sm rounded-circle me-2 btn-eval-send"
                title="Enviar"
                data-id="${ev.id}"
                ${ev.estado !== "pendiente" ? "disabled" : ""}>
          <i class="bi bi-send-fill"></i>
              </button>
              <button class="btn btn-outline-danger btn-sm rounded-circle btn-eval-delete"
                title="Eliminar"
                data-id="${ev.id}">
          <i class="bi bi-trash-fill"></i>
              </button>
              <button class="btn btn-outline-primary btn-sm rounded-circle me-2"
                onclick="showEvaluationDetails(${ev.id})"
                title="Ver detalles">
          <i class="bi bi-eye-fill"></i>
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
      ev.usuarios.some(u => u.nombre_completo.toLowerCase().includes(q)) ||
      ev.parametros.some(p => p.nombre.toLowerCase().includes(q)) ||
      ev.aplicacion_id.toString().includes(q)
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

  // ---------- Modal: Mostrar datos en Ver Detalles ----------
  window.showEvaluationDetails = function (id) {
    const evalData = evaluationsData.find(ev => ev.id === id);
    if (!evalData) {
      Swal.fire("Error", "Evaluación no encontrada.", "error");
      return;
    }

    // Crear o seleccionar el modal
    let detailsModal = document.getElementById("evaluationDetailsModal");
    if (!detailsModal) {
      detailsModal = document.createElement("div");
      detailsModal.className = "modal fade";
      detailsModal.id = "evaluationDetailsModal";
      detailsModal.tabIndex = -1;
      detailsModal.innerHTML = `
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content shadow-lg rounded-4 border-0">
          <!-- Header mejorado -->
          <div class="modal-header bg-gradient-primary text-white rounded-top-4">
            <h5 class="modal-title">
              <i class="bi bi-info-circle-fill me-2"></i>Detalles de Evaluación
            </h5>
            <button type="button" class="btn-close btn-close-white fs-5" data-bs-dismiss="modal" aria-label="Cerrar"></button>
          </div>
          <!-- Cuerpo del modal -->
          <div class="modal-body bg-light p-4">
            <div id="evaluationDetailsContent" class="container-fluid"></div>
          </div>
          <!-- Footer estilizado -->
          <div class="modal-footer bg-white border-top-0">
            <button type="button" class="btn btn-outline-secondary rounded-pill px-4" data-bs-dismiss="modal">
              <i class="bi bi-x-circle me-1"></i>Cerrar
            </button>
          </div>
        </div>
      </div>
    `;
      document.body.appendChild(detailsModal);
    }

    // Construir contenido con diseño en tarjetas y filas
    const estadoBadgeClass =
      evalData.estado === "pendiente" ? "bg-warning text-dark" :
        evalData.estado === "en progreso" ? "bg-info text-dark" :
          evalData.estado === "completada" ? "bg-success text-white" :
            "bg-secondary text-white";

    const detallesHtml = `
    <div class="row gy-3">
      <!-- Bloque: Información General -->
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body py-2">
            <div class="row">
              <div class="col-md-4 mb-2">
                <h6 class="text-muted mb-1">ID Evaluación</h6>
                <p class="fw-semibold mb-0">${evalData.id}</p>
              </div>
              <div class="col-md-4 mb-2">
                <h6 class="text-muted mb-1">Aplicación ID</h6>
                <p class="fw-semibold mb-0">${evalData.aplicacion_id}</p>
              </div>
              <div class="col-md-4 mb-2">
                <h6 class="text-muted mb-1">Estado</h6>
                <span class="badge ${estadoBadgeClass} text-capitalize">${evalData.estado.replace("_", " ")}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bloque: Fechas y Rondas -->
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body py-2">
            <div class="row">
              <div class="col-md-3 mb-2">
                <h6 class="text-muted mb-1">Fecha Inicio</h6>
                <p class="mb-0">${formatDate(evalData.fecha_inicio)}</p>
              </div>
              <div class="col-md-3 mb-2">
                <h6 class="text-muted mb-1">Fecha Fin</h6>
                <p class="mb-0">${formatDate(evalData.fecha_fin)}</p>
              </div>
              <div class="col-md-3 mb-2">
                <h6 class="text-muted mb-1">Rondas</h6>
                <p class="mb-0">${evalData.rondas}</p>
              </div>
              <div class="col-md-3 mb-2">
                <h6 class="text-muted mb-1">Comentarios</h6>
                <p class="mb-0 text-wrap">${escapeHtml(evalData.comentarios || "N/A")}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bloque: Parámetros y Evaluadores -->
      <div class="col-12">
        <div class="row g-3">
          <div class="col-md-6">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-bottom-0">
                <h6 class="mb-0"><i class="bi bi-list-check me-1"></i> Parámetros</h6>
              </div>
              <div class="card-body py-2">
                <ul class="list-group list-group-flush">
                  ${evalData.parametros.map(p => `
                    <li class="list-group-item py-1">
                      <i class="bi bi-dot me-2 text-primary"></i> ${escapeHtml(p.nombre)}
                    </li>
                  `).join("") || `<li class="list-group-item py-1 text-muted">Sin parámetros asignados.</li>`}
                </ul>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-bottom-0">
                <h6 class="mb-0"><i class="bi bi-people-fill me-1"></i> Evaluadores</h6>
              </div>
              <div class="card-body py-2">
                <ul class="list-group list-group-flush">
                  ${evalData.usuarios.map(u => `
                    <li class="list-group-item py-1">
                      <i class="bi bi-person-check me-2 text-success"></i> ${escapeHtml(u.nombre_completo || u.nombre)}
                    </li>
                  `).join("") || `<li class="list-group-item py-1 text-muted">Sin evaluadores asignados.</li>`}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

    detailsModal.querySelector("#evaluationDetailsContent").innerHTML = detallesHtml;
    bootstrap.Modal.getOrCreateInstance(detailsModal).show();
  };


  // ---------- Modal: Mostrar datos en Crear/Editar ----------
  // Delegación de eventos para abrir el modal al editar
  evaluationsBody.addEventListener("click", (e) => {
    const btnEdit = e.target.closest(".btn-eval-edit");
    if (!btnEdit) return;
    // Abre el modal y pasa el botón como relatedTarget
    const event = new Event("show.bs.modal", { bubbles: true, cancelable: true });
    event.relatedTarget = btnEdit;
    evalModalElement.dispatchEvent(event);
    evalModal.show();
  });

  evalModalElement.addEventListener("show.bs.modal", (event) => {
    ocultarErrorEval();
    const btn = event.relatedTarget;
    const title = evalModalElement.querySelector(".modal-title");

    if (btn === addEvalBtn) {
      // Modo CREAR
      title.textContent = "Nueva Evaluación";
      evalIdInput.value = "";
      appSelect.value = "";
      // Deseleccionar todos evaluadores y parámetros
      Array.from(evaluadoresSelect.options).forEach(opt => opt.selected = false);
      Array.from(parametrosContainer.querySelectorAll("input[type=checkbox]"))
        .forEach(chk => chk.checked = false);
      fechaInicioInput.value = "";
      fechaFinInput.value = "";
      rondasInput.value = "1";
      comentariosInput.value = "";
    } else if (btn && btn.classList.contains("btn-eval-edit")) {
      // Modo EDITAR
      title.textContent = "Editar Evaluación";
      const row = btn.closest("tr");
      const id = row.dataset.evalId;
      const aplicacion_id = row.dataset.aplicacionId;
      const estado_val = row.dataset.estado;
      const inicio = row.dataset.fechaInicio?.substr(0, 10) || "";
      const fin = row.dataset.fechaFin?.substr(0, 10) || "";
      const rondas_val = row.dataset.rondas || "1";
      const comentariosVal = row.dataset.comentarios || "";

      // Parámetros y usuarios vienen como JSON-strings en attributes
      let parsedParams, parsedUsers;
      try { parsedParams = JSON.parse(row.dataset.parametros); }
      catch { parsedParams = []; }
      try { parsedUsers = JSON.parse(row.dataset.usuarios); }
      catch { parsedUsers = []; }

      evalIdInput.value = id;
      appSelect.value = aplicacion_id;
      // Seleccionar checkboxes de parámetros
      Array.from(parametrosContainer.querySelectorAll("input[type=checkbox]")).forEach(chk => {
        chk.checked = parsedParams.includes(parseInt(chk.value));
      });
      // Seleccionar usuarios en el multi-select
      Array.from(evaluadoresSelect.options).forEach(opt => {
        opt.selected = parsedUsers.includes(parseInt(opt.value));
      });
      fechaInicioInput.value = inicio;
      fechaFinInput.value = fin;
      rondasInput.value = rondas_val;
      comentariosInput.value = comentariosVal;
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

    const id = evalIdInput.value.trim();
    const aplicacionId = parseInt(appSelect.value);
    const evaluadoresIds = Array.from(evaluadoresSelect.selectedOptions).map(o => parseInt(o.value));
    const selectedParams = Array.from(parametrosContainer.querySelectorAll("input[type=checkbox]:checked"))
      .map(chk => parseInt(chk.value));
    const inicioVal = fechaInicioInput.value;
    const finVal = fechaFinInput.value;
    const rondasVal = parseInt(rondasInput.value);
    const comentariosVal = comentariosInput.value.trim();

    // Validaciones
    if (!aplicacionId) {
      mostrarErrorEval("Selecciona la aplicación a evaluar.");
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
    if (!rondasVal || rondasVal < 1) {
      mostrarErrorEval("Ingresa un número de rondas válido.");
      return;
    }

    const payload = {
      aplicacion_id: aplicacionId,
      usuarios: evaluadoresIds,
      parametros: selectedParams,
      fecha_inicio: inicioVal,
      fecha_fin: finVal,
      rondas: rondasVal,
      comentarios: comentariosVal
    };
    const urlBase = "/jefe_dep/evaluacion";
    const url = id ? `${urlBase}/${id}` : urlBase;
    const method = id ? "PUT" : "POST";

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
      try { data = JSON.parse(text); } catch { }

      if (!res.ok) {
        const errMsg = data?.error || text || `HTTP ${res.status}`;
        throw new Error(errMsg);
      }

      evaluationsData = data.evaluaciones || [];
      filteredEvaluations = [...evaluationsData];
      currentPage = 1;
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

  // ---------- Enviar Evaluación a Evaluadores ----------
  evaluationsBody.addEventListener("click", async (e) => {
    const btnSend = e.target.closest(".btn-eval-send");
    if (!btnSend) return;

    const id = btnSend.dataset.id;
    const result = await Swal.fire({
      title: "¿Enviar evaluación?",
      text: "Esto notificará a los evaluadores y cambiará el estado.",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Sí, enviar",
      cancelButtonText: "Cancelar"
    });
    if (!result.isConfirmed) return;

    try {
      const res = await fetch(`/jefe_dep/evaluacion/${id}/enviar`, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrfToken() }
      });
      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch { }

      if (!res.ok) {
        const errMsg = data?.error || text || `HTTP ${res.status}`;
        throw new Error(errMsg);
      }

      evaluationsData = data.evaluaciones || [];
      filteredEvaluations = [...evaluationsData];
      renderEvaluationsPage(currentPage);

      Swal.fire({
        icon: "success",
        title: data.message,
        timer: 1500,
        showConfirmButton: false
      });
    } catch (err) {
      Swal.fire("Error", err.message || "Error al enviar la evaluación.", "error");
      console.error("[ERROR ENVIAR EVALUACIÓN]", err);
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
      try { data = JSON.parse(text); } catch { }

      if (!res.ok) {
        const errMsg = data?.error || text || `HTTP ${res.status}`;
        throw new Error(errMsg);
      }

      evaluationsData = data.evaluaciones || [];
      filteredEvaluations = [...evaluationsData];
      currentPage = 1;
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
      const res = await fetch("/jefe_dep/evaluacion");
      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch { }

      if (!res.ok) throw new Error(data?.message || text || `HTTP ${res.status}`);

      evaluationsData = data.evaluaciones || [];
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
