// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize page navigation
    initPageNavigation();
    
    // Initialize Charts
    initializeCharts();
    
    // Initialize form validation
    initFormValidation();
});

// Page Navigation
function initPageNavigation() {
    // Handle menu item clicks
    document.querySelectorAll('[data-page]').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const targetPage = this.getAttribute('data-page');
            navigateToPage(targetPage);
        });
    });
    
    // Handle hash changes
    window.addEventListener('hashchange', function() {
        const hash = window.location.hash.substring(1);
        if (hash) {
            navigateToPage(hash);
        }
    });
    
    // Check initial hash
    const initialHash = window.location.hash.substring(1);
    if (initialHash) {
        navigateToPage(initialHash);
    }
}

// Navigate to specific page
function navigateToPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show target page
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // Update menu active state
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        
        document.querySelectorAll(`.menu-item[data-page="${pageName}"]`).forEach(item => {
            item.classList.add('active');
        });
        
        // Close mobile sidebar if open
        const offcanvasSidebar = document.getElementById('offcanvasSidebar');
        if (offcanvasSidebar) {
            const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasSidebar);
            if (bsOffcanvas) {
                bsOffcanvas.hide();
            }
        }
        
        // Update URL hash without scrolling
        const scrollPosition = window.scrollY;
        window.location.hash = pageName;
        window.scrollTo(0, scrollPosition);
    }
}

// Initialize Charts
function initializeCharts() {
    // Project Analysis Progress Chart
    const projectChartCtx = document.getElementById('projectChart');
    if (projectChartCtx) {
        new Chart(projectChartCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Completed Projects',
                        data: [5, 8, 12, 15, 18, 22, 26, 30, 34, 38, 42, 45],
                        borderColor: '#6754e2',
                        backgroundColor: 'rgba(103, 84, 226, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Ongoing Projects',
                        data: [10, 12, 15, 18, 20, 17, 15, 13, 11, 9, 7, 5],
                        borderColor: '#42a6ff',
                        backgroundColor: 'rgba(66, 166, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
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

    // Expert Distribution Chart
    const expertChartCtx = document.getElementById('expertChart');
    if (expertChartCtx) {
        new Chart(expertChartCtx, {
            type: 'doughnut',
            data: {
                labels: ['Market Research', 'Risk Assessment', 'Product Development', 'Competitive Analysis', 'Other'],
                datasets: [{
                    data: [35, 20, 25, 15, 5],
                    backgroundColor: [
                        '#6754e2',
                        '#42a6ff',
                        '#28a745',
                        '#ffc107',
                        '#ff6b6b'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                },
                cutout: '70%'
            }
        });
    }
}

// Form Validation
function initFormValidation() {
    // Add Expert Form
    const addExpertForm = document.getElementById('addExpertForm');
    const saveExpertBtn = document.getElementById('saveExpertBtn');
    
    if (addExpertForm && saveExpertBtn) {
        saveExpertBtn.addEventListener('click', function() {
            // Check form validity
            if (!addExpertForm.checkValidity()) {
                // Trigger browser validation UI
                addExpertForm.reportValidity();
                return;
            }
            
            // Form is valid, simulate saving
            const modal = bootstrap.Modal.getInstance(document.getElementById('addExpertModal'));
            
            // Show success message
            showToast('Expert added successfully!', 'success');
            
            // Close modal
            if (modal) {
                modal.hide();
            }
            
            // Reset form
            addExpertForm.reset();
        });
    }
    
    // Settings Forms
    document.querySelectorAll('.settings-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show success message
            showToast('Settings saved successfully!', 'success');
        });
    });
    
    // Profile Form
    const profileForm = document.querySelector('.profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show success message
            showToast('Profile updated successfully!', 'success');
        });
    }
    
    // Color Options
    const colorOptions = document.querySelectorAll('.color-option');
    if (colorOptions.length > 0) {
        colorOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Remove active class from all options
                colorOptions.forEach(opt => opt.classList.remove('active'));
                
                // Add active class to clicked option
                this.classList.add('active');
                
                // Get selected color
                const selectedColor = this.style.backgroundColor;
                
                // Update primary color (this is just a simulation)
                document.documentElement.style.setProperty('--primary-color', selectedColor);
                
                // Show success message
                showToast('Theme color updated!', 'success');
            });
        });
    }
}

// Toast Notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Toast content
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toastEl);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // Remove toast element after it's hidden
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

// Handle pagination clicks
document.addEventListener('click', function(e) {
    if (e.target.closest('.pagination .page-link')) {
        e.preventDefault();
        const pageLink = e.target.closest('.page-link');
        const pagination = pageLink.closest('.pagination');
        
        // Skip if disabled
        if (pageLink.parentElement.classList.contains('disabled')) {
            return;
        }
        
        // Update active page
        pagination.querySelectorAll('.page-item').forEach(item => {
            item.classList.remove('active');
        });
        
        if (!pageLink.textContent.includes('Previous') && !pageLink.textContent.includes('Next')) {
            pageLink.parentElement.classList.add('active');
        }
        
        // Scroll to top of container
        const container = pagination.closest('.card');
        if (container) {
            container.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
});

// Handle tab navigation
document.addEventListener('shown.bs.tab', function(e) {
    // Scroll to top of tab content
    const tabContent = e.target.getAttribute('data-bs-target');
    const tabPane = document.querySelector(tabContent);
    if (tabPane) {
        tabPane.scrollTop = 0;
    }
});

// Handle responsive behavior
window.addEventListener('resize', function() {
    adjustResponsiveLayout();
});

function adjustResponsiveLayout() {
    const width = window.innerWidth;
    
    // Adjust table columns for small screens
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        if (width < 768) {
            table.classList.add('table-responsive');
        } else {
            table.classList.remove('table-responsive');
        }
    });
}

// Initialize responsive adjustments
adjustResponsiveLayout();