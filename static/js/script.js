// static/js/script.js
 $(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // Form validation
    'use strict';
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Smooth scrolling for anchor links
    $('a[href*="#"]').not('[href="#"]').not('[href="#0"]').click(function(event) {
        if (
            location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') &&
            location.hostname == this.hostname
        ) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                event.preventDefault();
                $('html, body').animate({
                    scrollTop: target.offset().top
                }, 1000);
            }
        }
    });
    
    // Add active class to nav links based on scroll position
    $(window).scroll(function() {
        var scrollDistance = $(window).scrollTop();
        
        // Assign active class to nav links while scrolling
        $('.page-section').each(function(i) {
            if ($(this).position().top <= scrollDistance) {
                $('.navbar-nav a.active').removeClass('active');
                $('.navbar-nav a').eq(i).addClass('active');
            }
        });
    }).scroll();
    
    // Back to top button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });
    
    $('#back-to-top').click(function() {
        $('html, body').animate({scrollTop : 0}, 800);
        return false;
    });
    
    // Number formatting for currency
    function formatCurrency(amount) {
        return '₹' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    }
    
    // Date formatting
    function formatDate(date) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(date).toLocaleDateString(undefined, options);
    }
    
    // Time formatting
    function formatTime(time) {
        const options = { hour: '2-digit', minute: '2-digit' };
        return new Date('1970-01-01T' + time).toLocaleTimeString(undefined, options);
    }
    
    // Export functions for use in other scripts
    window.formatCurrency = formatCurrency;
    window.formatDate = formatDate;
    window.formatTime = formatTime;
});