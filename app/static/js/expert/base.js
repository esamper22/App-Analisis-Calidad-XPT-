// expert_dashboard.js

document.addEventListener('DOMContentLoaded', () => {
  // ---------- Navegación con transiciones ----------
  const activateSection = (targetId) => {
    document.querySelectorAll('.content-section').forEach(section => {
      section.classList.remove('active');
      if (section.id === targetId) {
        setTimeout(() => section.classList.add('active'), 50);
      }
    });
  };
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href').substring(1);
      document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      activateSection(targetId);
    });
  });

  // ---------- Función auxiliar para formatear fechas ----------
  function formatDateISO(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    if (isNaN(date)) return isoString;
    return date.toISOString().slice(0, 10);
  }

  // ---------- Cargar métricas y renderizar gráficos ----------
  async function loadMetricsAndCharts() {
    try {
      const res = await fetch('/evaluador/metrics');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      // data = { months: [...], completed_per_month: [...], platforms: [...], by_platform: [...] }

      // Gráfico de barras (Progreso Mensual)
      const barCtx = document.getElementById('dashboardChart').getContext('2d');
      new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: data.months,
          datasets: [{
            label: 'Evaluaciones Completadas',
            data: data.completed_per_month,
            backgroundColor: 'rgba(103, 84, 226, 0.8)',
            borderColor: 'rgba(103, 84, 226, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true } }
        }
      });

      // Gráfico de pastel (Distribución por plataforma)
      const pieCtx = document.getElementById('pieChart').getContext('2d');
      new Chart(pieCtx, {
        type: 'pie',
        data: {
          labels: data.platforms,
          datasets: [{
            data: data.by_platform,
            backgroundColor: ['#6754e2', '#42a6ff', '#ff6b6b']
          }]
        },
        options: { responsive: true }
      });
    } catch (err) {
      console.error('[ERROR] Al cargar métricas:', err);
      Swal.fire('Error', 'No se pudieron cargar las métricas.', 'error');
    }
  }

  // ---------- Cargar calendario (días resaltados, eventos) ----------
  async function loadMiniCalendar() {
    const today = new Date();
    const calendarEl = document.getElementById('mini-calendar');
    const monthNames = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

    // Traer eventos próximos (opcional)
    let events = [];
    try {
      const res = await fetch('/evaluador/events');
      if (res.ok) {
        const json = await res.json();
        events = json.events; // [{ date: "2024-03-15", title: "Revisión App Mobile" }, ...]
      }
    } catch { /* Silenciar error */ }

    const daysInMonth = new Date(today.getFullYear(), today.getMonth()+1, 0).getDate();
    let calendarHTML = `<div class="mb-2 fw-bold">${monthNames[today.getMonth()]} ${today.getFullYear()}</div>`;
    calendarHTML += `<div class="d-grid gap-1" style="grid-template-columns: repeat(7, 1fr);">`;

    for (let i = 1; i <= daysInMonth; i++) {
      const iso = new Date(today.getFullYear(), today.getMonth(), i).toISOString().slice(0,10);
      const isToday = (i === today.getDate());
      const hasEvent = events.some(ev => ev.date === iso);
      let cellClass = 'text-center p-1';
      if (isToday) cellClass += ' bg-gradient-primary text-white rounded';
      else if (hasEvent) cellClass += ' bg-info text-white rounded';

      calendarHTML += `<div class="${cellClass}">${i}</div>`;
    }
    calendarHTML += '</div>';
    calendarEl.innerHTML = calendarHTML;

    // Lista de eventos
    const upcomingList = document.getElementById('upcoming-events-list');
    if (upcomingList && events.length) {
      upcomingList.innerHTML = events.map(ev => `
        <a href="#" class="list-group-item list-group-item-action px-3 py-2">
          <i class="fas fa-clock me-2 text-info"></i>${ev.title} - ${formatDateISO(ev.date)}
        </a>
      `).join('');
    }
  }

  // ---------- Inicializar (cargar métricas, calendario) ----------
  loadMetricsAndCharts();
  loadMiniCalendar();
});
