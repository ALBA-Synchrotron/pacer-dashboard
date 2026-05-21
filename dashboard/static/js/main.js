document.addEventListener('DOMContentLoaded', function () {
    const themeController = document.querySelector('.theme-controller');
    const THEME_STORAGE_KEY = 'preferred-theme';

    // Load theme on page load
    function loadTheme() {
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);

        if (savedTheme) {
            // Load from localStorage if available
            applyTheme(savedTheme);
        } else {
            // Default to system preference
            const prefersabyss = window.matchMedia('(prefers-color-scheme: abyss)').matches;
            const systemTheme = prefersabyss ? 'abyss' : 'light';
            applyTheme(systemTheme);
        }
    }

    // Apply theme to the document and update checkbox
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        if (themeController) {
            themeController.checked = (theme === 'abyss');
        }
    }

    // Save theme when controller is changed
    if (themeController) {
        themeController.addEventListener('change', function () {
            const selectedTheme = this.checked ? 'abyss' : 'light';
            localStorage.setItem(THEME_STORAGE_KEY, selectedTheme);
            applyTheme(selectedTheme);
        });
    }

    // Initialize theme
    loadTheme();
});

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("pre code.hljs-target:not(.hljs)").forEach(el => {
        hljs.highlightElement(el);
    });
});

// Re-run after HTMX swaps (your msg cards are loaded via hx-get)
document.body.addEventListener("htmx:afterSwap", (evt) => {
    evt.target.querySelectorAll("pre code.hljs-target:not(.hljs)").forEach(el => {
        hljs.highlightElement(el);
    });
});

