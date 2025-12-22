
        // Initialize Lucide icons
        lucide.createIcons();
        
        // Toggle password visibility
        function togglePassword() {
            const passwordInput = document.getElementById('password');
            const eyeIcon = document.getElementById('eye-icon');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon.setAttribute('data-lucide', 'eye-off');
            } else {
                passwordInput.type = 'password';
                eyeIcon.setAttribute('data-lucide', 'eye');
            }
            
            // Refresh icon
            lucide.createIcons();
        }
        
        // Optional: 3D tilt effect on mouse move
        const card = document.querySelector('.login-card');
        const container = document.querySelector('.card-container');
        
        container.addEventListener('mousemove', (e) => {
            const rect = container.getBoundingClientRect();
            const x = (e.clientX - rect.left - rect.width / 2) / 25;
            const y = (e.clientY - rect.top - rect.height / 2) / 25;
            
            card.style.transform = `rotateY(${x}deg) rotateX(${-y}deg)`;
        });
        
        container.addEventListener('mouseleave', () => {
            card.style.transform = 'rotateY(0) rotateX(0)';
        });
    