document.addEventListener('DOMContentLoaded', function () {
    const themeController = document.querySelector('.theme-controller');
    const THEME_STORAGE_KEY = 'preferred-theme';

    function loadTheme() {
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);

        if (savedTheme) {
            applyTheme(savedTheme);
        } else {
            const prefersabyss = window.matchMedia('(prefers-color-scheme: abyss)').matches;
            const systemTheme = prefersabyss ? 'abyss' : 'light';
            applyTheme(systemTheme);
        }
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        if (themeController) {
            themeController.checked = (theme === 'abyss');
        }
    }

    if (themeController) {
        themeController.addEventListener('change', function () {
            const selectedTheme = this.checked ? 'abyss' : 'light';
            localStorage.setItem(THEME_STORAGE_KEY, selectedTheme);
            applyTheme(selectedTheme);
        });
    }

    loadTheme();
    restoreFilters();
});

function restoreFilters() {
    const filters = [
        {
            id: "xml-toggle",
            key: "xml",
        }, {
            id: "json-toggle",
            key: "json",
        },
        {
            id: "live-enabled",
            key: "live"
        },
        {
            id: "errored-only-toggle",
            key: "errored"
        }, ...variableFilters
    ]

    for (const filter of filters) {
        const filterElement = document.getElementById(filter.id);
        if (filterElement && localStorage.getItem(filter.key) !== null) {
            filterElement.checked = localStorage.getItem(filter.key) === "true";
        }
    }

    const filterElement = document.getElementById("general-text-search");
    if (filterElement && localStorage.getItem("search") !== null) {
        filterElement.value = localStorage.getItem("search");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("pre code.hljs-target:not(.hljs)").forEach(el => {
        hljs.highlightElement(el);
    });
});

document.body.addEventListener("htmx:afterSwap", (evt) => {
    evt.target.querySelectorAll("pre code.hljs-target:not(.hljs)").forEach(el => {
        hljs.highlightElement(el);
    });
});

function dateRangeFilter(){
    let selectedDateRange = $(document.getElementById("calendar-filter")).val();
    $("#date-range-selection").text(selectedDateRange.replace('/', ' to '));
    const [startDate, endDate] = selectedDateRange.split("/");
    $("#startDate").val(startDate);
    $("#endDate").val(endDate);
}

function resetDateRangeFilter(){
    const calendar = document.getElementById("calendar-filter");
    calendar.value = null;
    $("#startDate").val("");
    $("#endDate").val("");
    calendar.dispatchEvent(new Event("change", { bubbles: true }));
    $("#date-range-selection").text("Select date range");
}
