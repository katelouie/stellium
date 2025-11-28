// Force light mode as default on first visit
(function () {
    // Only run if no preference has been set yet
    if (!localStorage.getItem('theme')) {
        localStorage.setItem('theme', 'light');
        document.documentElement.dataset.theme = 'light';
    }
})();