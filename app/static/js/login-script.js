document.addEventListener('DOMContentLoaded', function () {
    // Toggle password visibility
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    // Path completos
    const eyeOpenD =
        'M12 4.5C7 4.5 2.73 7.61 1 12' +
        'c1.73 4.39 6 7.5 11 7.5' +
        's9.27-3.11 11-7.5' +
        'C21.27 7.61 17 4.5 12 4.5z' +
        'M12 17c-2.76 0-5-2.24-5-5' +
        's2.24-5 5-5 5 2.24 5 5' +
        's-2.24 5-5 5z' +
        'M12 9c-1.66 0-3 1.34-3 3' +
        's1.34 3 3 3 3-1.34 3-3' +
        's-1.34-3-3-3z';

    const eyeClosedD =
        'M2.81 1.81L1.39 3.22l3.39 3.39' +
        'C3.83 7.79 3.1 9.17 2.73 10.68' +
        'l1.46 1.46c.09-.88.44-1.7 1.01-2.44' +
        'L7.59 12.09c-.19.61-.29 1.24-.29 1.91' +
        'c0 2.76 2.24 5 5 5' +
        'c.93 0 1.8-.25 2.58-.68' +
        'l3.49 3.49l1.41-1.41' +
        'L2.81 1.81z' +
        'M12 6.5c-2.76 0-5 2.24-5 5' +
        'c0 .89.19 1.72.54 2.47' +
        'l1.43-1.43c-.58-.7-.98-1.52-.98-2.47' +
        'c0-2.76 2.24-5 5-5' +
        'c1.93 0 3.58 1.1 4.44 2.74' +
        'l1.46-1.46' +
        'C15.72 6.69 13.97 6.5 12 6.5z';

    togglePassword.addEventListener('click', function () {
        // Cambia tipo
        const isText = passwordInput.type === 'text';
        passwordInput.type = isText ? 'password' : 'text';

        // Cambia path
        const path = this.querySelector('path');
        path.setAttribute('d', isText ? eyeClosedD : eyeOpenD);
    });

    const form = document.getElementById('loginForm');
    const loginButton = document.querySelector('.login-button');
    let originalHTML = loginButton.innerHTML;

    form.addEventListener('submit', async e => {
        e.preventDefault();
    
        // --- Animación de loader ---
        loginButton.innerHTML = '<div class="loader"></div>';
        loginButton.disabled = true;
    
        const formData = new FormData(form);
    
        console.group('🚀 FormData entries');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ':', pair[1]);
        }
        console.groupEnd();
    
        try {
            const resp = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
    
            const data = await resp.json();
    
            loginButton.disabled = false;
    
            if (data.success) {
                loginButton.classList.add('success');
                loginButton.innerHTML = '<span>¡Bienvenido!</span>';
    
                Swal.fire({
                    icon: 'success',
                    title: 'Login exitoso',
                    text: 'Serás redirigido en un momento...',
                    timer: 1500,
                    showConfirmButton: false
                });
    
                return setTimeout(() => window.location = data.next_url, 1500);
            }
    
            // ❌ Mostrar errores usando SweetAlert
            if (data.errors && data.errors.length > 0) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error de autenticación',
                    html: data.errors.map(e => `<p>${e}</p>`).join(''),
                    confirmButtonText: 'Entendido'
                });
            }
    
            shakeEmptyInputs();
            resetButton();
    
        } catch (err) {
            console.error('Fetch error:', err);
            resetButton();
    
            Swal.fire({
                icon: 'error',
                title: 'Error del servidor',
                text: 'Ocurrió un problema. Intenta más tarde.'
            });
        }
    });    
    

    function resetButton() {
        loginButton.classList.remove('success');
        loginButton.innerHTML = originalHTML;
    }

    function shakeEmptyInputs() {
        form.querySelectorAll('input').forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('input-error');
                setTimeout(() => input.classList.remove('input-error'), 3000);
            }
        });
    }

    // function showError(msg) {
    //     let div = form.querySelector('.login-error');
    //     if (!div) {
    //         div = document.createElement('div');
    //         div.className = 'login-error text-danger';
    //         form.prepend(div);
    //     }
    //     div.textContent = msg;
    // }

    // Input focus effects
    const inputs = document.querySelectorAll('input');

    inputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.style.transform = 'scale(1.02)';
        });

        input.addEventListener('blur', function () {
            this.parentElement.style.transform = '';
        });
    });

    // Floating elements parallax effect
    document.addEventListener('mousemove', function (e) {
        const moveX = (e.clientX - window.innerWidth / 2) / 50;
        const moveY = (e.clientY - window.innerHeight / 2) / 50;

        if (document.getElementById('element1')) {
            document.getElementById('element1').style.transform = `translate(${moveX * -1}px, ${moveY * -1}px)`;
        }

        if (document.getElementById('element2')) {
            document.getElementById('element2').style.transform = `translate(${moveX}px, ${moveY}px)`;
        }

        if (document.getElementById('element3')) {
            document.getElementById('element3').style.transform = `translate(${moveX * 0.5}px, ${moveY * 0.5}px)`;
        }
    });

    // Add CSS for loader
    const style = document.createElement('style');
    style.textContent = `
        .loader {
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .login-button.success {
            background: linear-gradient(135deg, #4CAF50, #8BC34A);
        }
    `;
    document.head.appendChild(style);
});