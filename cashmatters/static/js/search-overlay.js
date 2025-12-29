/**
 * Search Overlay Functionality
 * Handles the full-screen search modal
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchOverlay = document.getElementById('searchOverlay');
    const searchInput = document.getElementById('searchOverlayInput');
    const searchClose = document.getElementById('searchClose');

    // Get all search trigger buttons
    const searchTriggers = document.querySelectorAll('.search-trigger, .btn.text-white.p-0 .bi-search');

    // Also handle the nav search button (for backwards compatibility)
    document.querySelectorAll('.bi-search').forEach(function(icon) {
        const btn = icon.closest('button');
        if (btn && !btn.classList.contains('search-trigger')) {
            btn.addEventListener('click', openSearchOverlay);
        }
    });

    // Open search overlay
    function openSearchOverlay(e) {
        if (e) e.preventDefault();
        if (searchOverlay) {
            searchOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            // Focus the input after animation
            setTimeout(function() {
                if (searchInput) searchInput.focus();
            }, 100);
        }
    }

    // Close search overlay
    function closeSearchOverlay() {
        if (searchOverlay) {
            searchOverlay.classList.remove('active');
            document.body.style.overflow = '';
            if (searchInput) searchInput.value = '';
        }
    }

    // Event listeners for search triggers
    searchTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', openSearchOverlay);
    });

    // Close button click
    if (searchClose) {
        searchClose.addEventListener('click', closeSearchOverlay);
    }

    // Close on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && searchOverlay && searchOverlay.classList.contains('active')) {
            closeSearchOverlay();
        }
    });

    // Close when clicking outside the content
    if (searchOverlay) {
        searchOverlay.addEventListener('click', function(e) {
            if (e.target === searchOverlay || e.target.classList.contains('search-overlay-content')) {
                closeSearchOverlay();
            }
        });
    }

    // Prevent closing when clicking inside the form
    const searchForm = searchOverlay ? searchOverlay.querySelector('.search-overlay-form') : null;
    if (searchForm) {
        searchForm.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
});
