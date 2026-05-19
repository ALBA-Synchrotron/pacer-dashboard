// Cookie helper functions
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function setTheme(theme) {
    const html = document.querySelector("html");
    html.setAttribute("data-theme", theme);

    const checkbox = document.querySelector("#theme-indicator input[type='checkbox']");
    if (checkbox) {
        checkbox.checked = theme === "light";
    }

    // Save to cookie
    setCookie("theme", theme, 365);
}

function toggleTheme() {
    const html = document.querySelector("html");
    const currentTheme = html.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    setTheme(newTheme);
}

// Initialize theme on page load
(function initTheme() {
    const savedTheme = getCookie("theme");

    if (savedTheme) {
        // Use saved theme from cookie
        setTheme(savedTheme);
    } else {
        // Use system preference
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        const theme = prefersDark ? "dark" : "light";
        setTheme(theme);
    }
})();

$("#theme-toggle-btn").on("click", function (e) {
    e.preventDefault();
    toggleTheme();
});

$("#theme-indicator, #theme-indicator *").on("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    toggleTheme();
});