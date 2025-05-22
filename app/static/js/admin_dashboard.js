// Función para cambiar entre páginas
// function changePage(pageNumber) {
//     // Ocultar todas las secciones
//     document.querySelectorAll('.content-section').forEach(section => {
//         section.classList.remove('active');
//     });

//     // Mostrar la sección seleccionada
//     const page = document.getElementById('page-' + pageNumber);
//     if (page) {
//         page.classList.add('active');
//     } else {
//         console.warn(`No existe la sección con id page-${pageNumber}`);
//     }

//     // Actualizar el menú lateral usando data-page
//     document.querySelectorAll('.nav-pills .nav-link').forEach(link => {
//         link.classList.remove('active');
//         if (link.dataset.page === String(pageNumber)) {
//             link.classList.add('active');
//         }
//     });

//     // Cerrar el offcanvas en móviles
//     const offcanvas = document.getElementById('offcanvas');
//     const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvas);
//     if (bsOffcanvas && window.innerWidth < 992) {
//         bsOffcanvas.hide();
//     }
// }

function changePage(pageNumber) {
    // 1) Secciones
    document.querySelectorAll('.content-section').forEach(sec =>
        sec.classList.toggle('active', sec.id === 'page-' + pageNumber)
    );

    // 2) Nav activo
    document.querySelectorAll('#sideMenu .nav-link').forEach(link =>
        link.classList.toggle('active', link.dataset.page === String(pageNumber))
    );

    // 3) Cerrar offcanvas en móviles
    const offcanvasEl = document.getElementById('offcanvas');
    const bsOff = bootstrap.Offcanvas.getInstance(offcanvasEl);
    if (bsOff && window.innerWidth < 992) bsOff.hide();
}


// Inicializar gráficos cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap's Offcanvas (if not already initialized)
    // const offcanvasElementList = [].slice.call(document.querySelectorAll('.offcanvas'))
    // const offcanvasList = offcanvasElementList.map(function (offcanvasEl) {
    //   return new bootstrap.Offcanvas(offcanvasEl)
    // })

    // 1) Quitar todos los onclick inline
    // 2) Agregar un único listener que lea data-page
    document.querySelectorAll('#sideMenu .nav-link').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            // Si es un enlace real (Inicio), dejamos la navegación normal
            if (link.href && !link.href.endsWith('#')) {
                return window.location = link.href;
            }
            const pageNumber = link.dataset.page;
            changePage(pageNumber);
        });
    });

    // Gráfico de actividad de usuarios
    const userActivityCtx = document.getElementById('userActivityChart');
    if (userActivityCtx) {
        new Chart(userActivityCtx, {
            type: 'line',
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                datasets: [{
                    label: 'Usuarios Activos',
                    data: [650, 730, 810, 890, 950, 1020, 1080, 1150, 1220, 1280, 1350, 1420],
                    borderColor: '#6754e2',
                    backgroundColor: 'rgba(103, 84, 226, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Gráfico de distribución de aplicaciones
    const appDistributionCtx = document.getElementById('appDistributionChart');
    if (appDistributionCtx) {
        new Chart(appDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Análisis', 'Finanzas', 'Productividad', 'Seguridad', 'Otros'],
                datasets: [{
                    data: [35, 25, 20, 15, 5],
                    backgroundColor: [
                        '#6754e2',
                        '#42a6ff',
                        '#28a745',
                        '#ff6b6b',
                        '#ffc107'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                cutout: '70%'
            }
        });
    }

    // Gráfico de evaluaciones por mes
    const evaluationsCtx = document.getElementById('evaluationsChart');
    if (evaluationsCtx) {
        new Chart(evaluationsCtx, {
            type: 'bar',
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
                datasets: [{
                    label: 'Evaluaciones',
                    data: [65, 78, 90, 85, 95, 110],
                    backgroundColor: '#6754e2'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Gráfico de distribución de usuarios
    const userDistributionCtx = document.getElementById('userDistributionChart');
    if (userDistributionCtx) {
        new Chart(userDistributionCtx, {
            type: 'pie',
            data: {
                labels: ['Administradores', 'Evaluadores', 'Usuarios'],
                datasets: [{
                    data: [15, 35, 50],
                    backgroundColor: [
                        '#ff6b6b',
                        '#42a6ff',
                        '#28a745'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Gráfico de categorías de aplicaciones
    const appCategoriesCtx = document.getElementById('appCategoriesChart');
    if (appCategoriesCtx) {
        new Chart(appCategoriesCtx, {
            type: 'polarArea',
            data: {
                labels: ['Análisis', 'Finanzas', 'Productividad', 'Seguridad', 'Otros'],
                datasets: [{
                    data: [35, 25, 20, 15, 5],
                    backgroundColor: [
                        'rgba(103, 84, 226, 0.7)',
                        'rgba(66, 166, 255, 0.7)',
                        'rgba(40, 167, 69, 0.7)',
                        'rgba(255, 107, 107, 0.7)',
                        'rgba(255, 193, 7, 0.7)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Gráfico de tendencia de evaluaciones
    const evaluationTrendCtx = document.getElementById('evaluationTrendChart');
    if (evaluationTrendCtx) {
        new Chart(evaluationTrendCtx, {
            type: 'line',
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                datasets: [{
                    label: 'Calificación Promedio',
                    data: [4.1, 4.2, 4.0, 4.3, 4.2, 4.4, 4.5, 4.6, 4.5, 4.7, 4.8, 4.9],
                    borderColor: '#42a6ff',
                    backgroundColor: 'rgba(66, 166, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        min: 3.5,
                        max: 5,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
});