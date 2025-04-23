/* İrrigo - Main JavaScript */

// Document ready handler
document.addEventListener('DOMContentLoaded', function() {
    // Initialize hamburger menu toggle functionality
    // const navbarToggler = document.querySelector('.navbar-toggler');
    // const navbarCollapse = document.getElementById('navbarNav');
    
    // if (navbarToggler && navbarCollapse) {
    //     // Start with menu closed (this is the default behavior)
    //     navbarCollapse.classList.add('collapse');
        
    //     // Set up toggle functionality
    //     navbarToggler.addEventListener('click', function() {
    //         navbarCollapse.classList.toggle('show');
    //     });
    // }
    
    // Add visual indicator for current page in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
