document.addEventListener('DOMContentLoaded', function() {
    // Toggle password visibility
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    
    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // Change the eye icon
        const eyeIcon = this.querySelector('.eye-icon');
        if (type === 'text') {
            eyeIcon.innerHTML = '<path fill="currentColor" d="M12,9A3,3 0 0,1 15,12A3,3 0 0,1 12,15A3,3 0 0,1 9,12A3,3 0 0,1 12,9M12,4.5C17,4.5 21.27,7.61 23,12C21.27,16.39 17,19.5 12,19.5C7,19.5 2.73,16.39 1,12C2.73,7.61 7,4.5 12,4.5M3.18,12C4.83,15.36 8.24,17.5 12,17.5C15.76,17.5 19.17,15.36 20.82,12C19.17,8.64 15.76,6.5 12,6.5C8.24,6.5 4.83,8.64 3.18,12Z" />';
        } else {
            eyeIcon.innerHTML = '<path fill="currentColor" d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z" />';
        }
    });
    
    // Form submission
    const loginForm = document.getElementById('loginForm');
    
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        // Add loading state to button
        const loginButton = document.querySelector('.login-button');
        const originalButtonText = loginButton.innerHTML;
        loginButton.innerHTML = '<div class="loader"></div>';
        loginButton.disabled = true;
        
        // Simulate API call
        setTimeout(function() {
            // Reset button state
            loginButton.innerHTML = originalButtonText;
            loginButton.disabled = false;
            
            // Here you would normally validate credentials with a server
            // For demo purposes, we'll just show an alert
            if (username && password) {
                // Success animation
                loginButton.classList.add('success');
                loginButton.innerHTML = '<span>¡Bienvenido!</span>';
                
            } else {
                // Show error
                const inputs = document.querySelectorAll('input');
                inputs.forEach(input => {
                    if (!input.value) {
                        input.style.borderColor = 'var(--accent-color)';
                        setTimeout(() => {
                            input.style.borderColor = '';
                        }, 3000);
                    }
                });
            }
        }, 1500);
    });
    
    // Input focus effects
    const inputs = document.querySelectorAll('input');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = '';
        });
    });
    
    // Floating elements parallax effect
    document.addEventListener('mousemove', function(e) {
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