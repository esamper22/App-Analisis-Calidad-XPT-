document.addEventListener('DOMContentLoaded', function() {
    // Animate feature cards on scroll
    const featureCards = document.querySelectorAll('.feature-card');
    
    const animateOnScroll = function() {
        featureCards.forEach(card => {
            const cardPosition = card.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.2;
            const delay = parseInt(card.getAttribute('data-delay')) || 0;
            
            if (cardPosition < screenPosition) {
                setTimeout(() => {
                    card.style.animation = 'fadeInUp 0.8s forwards';
                }, delay);
            }
        });
    };
    
    // Initial check for elements in viewport
    animateOnScroll();
    
    // Check on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Header scroll effect
    const header = document.querySelector('header');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.1)';
            header.style.padding = '10px 0';
        } else {
            header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
            header.style.padding = '15px 0';
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Parallax effect for floating elements
    window.addEventListener('mousemove', function(e) {
        const moveX = (e.clientX - window.innerWidth / 2) / 50;
        const moveY = (e.clientY - window.innerHeight / 2) / 50;
        
        document.getElementById('element1').style.transform = `translate(${moveX * -1}px, ${moveY * -1}px)`;
        document.getElementById('element2').style.transform = `translate(${moveX}px, ${moveY}px)`;
        document.getElementById('element3').style.transform = `translate(${moveX * 0.5}px, ${moveY * 0.5}px)`;
    });
    
    // Button hover effects
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            if (this.classList.contains('primary-btn')) {
                this.style.boxShadow = '0 8px 25px rgba(103, 84, 226, 0.5)';
            }
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
            if (this.classList.contains('primary-btn')) {
                this.style.boxShadow = '0 5px 15px rgba(103, 84, 226, 0.3)';
            }
        });
    });
});