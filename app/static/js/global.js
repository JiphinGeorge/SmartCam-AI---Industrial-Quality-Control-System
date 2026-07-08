document.addEventListener("DOMContentLoaded", function() {
    // Topbar Clock Logic
    const clockEl = document.getElementById("topbar-clock");
    if (clockEl) {
        function updateClock() {
            const now = new Date();
            const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            clockEl.textContent = (window.timezoneLabel || "Local") + " " + timeString;
        }
        updateClock();
        setInterval(updateClock, 1000 * 60); // Update every minute
    }
    
    // Topbar Factory Name Injection
    const factoryEl = document.getElementById("topbar-factory-name");
    
    function applySettings(data) {
        if (data.factory_name && factoryEl) {
            factoryEl.textContent = data.factory_name;
        }
        if (data.timezone) {
            // e.g. "UTC+01:00 (Europe/Berlin)" -> "UTC+01:00"
            window.timezoneLabel = data.timezone.split(" ")[0];
            if (clockEl) updateClock();
        }
    }

    // Listen for real-time changes from the Settings page
    window.addEventListener('settingsLoaded', (e) => {
        applySettings(e.detail);
    });

    // On normal pages, fetch settings once
    if (factoryEl) {
        fetch('/api/settings')
            .then(res => res.json())
            .then(data => {
                if (!data.error) applySettings(data);
            })
            .catch(err => console.error("Could not fetch global settings", err));
    }

    // Topbar Theme Toggle
    const themeToggleBtn = document.getElementById("theme-toggle-topbar");
    if (themeToggleBtn) {
        const iconEl = themeToggleBtn.querySelector(".material-symbols-outlined");
        
        function updateIcon() {
            const isDark = document.documentElement.classList.contains("dark");
            iconEl.textContent = isDark ? "light_mode" : "dark_mode";
        }
        updateIcon();

        themeToggleBtn.addEventListener("click", () => {
            const isDark = document.documentElement.classList.toggle("dark");
            localStorage.setItem("theme", isDark ? "dark" : "light");
            updateIcon();
            
            // Dispatch event for settings page to sync
            window.dispatchEvent(new Event('themeChanged'));
        });
    }
    // Settings Page Theme Toggle
    const settingsThemeToggle = document.getElementById("set-theme-toggle");
    const settingsThemeText = document.getElementById("setting-theme-text");
    const settingsThemeIcon = document.getElementById("setting-theme-icon");

    if (settingsThemeToggle) {
        function updateSettingsToggleUI() {
            const isDark = document.documentElement.classList.contains("dark");
            settingsThemeToggle.checked = isDark;
            if (settingsThemeText) settingsThemeText.textContent = isDark ? "Dark Mode" : "Light Mode";
            if (settingsThemeIcon) settingsThemeIcon.textContent = isDark ? "dark_mode" : "light_mode";
        }
        
        // Initial setup
        updateSettingsToggleUI();

        // Listen for changes from the settings toggle
        settingsThemeToggle.addEventListener("change", (e) => {
            const isDark = e.target.checked;
            if (isDark) {
                document.documentElement.classList.add("dark");
            } else {
                document.documentElement.classList.remove("dark");
            }
            localStorage.setItem("theme", isDark ? "dark" : "light");
            updateSettingsToggleUI();
            
            // Sync topbar
            if (themeToggleBtn) {
                const iconEl = themeToggleBtn.querySelector(".material-symbols-outlined");
                iconEl.textContent = isDark ? "light_mode" : "dark_mode";
            }
        });

        // Listen for changes from topbar
        window.addEventListener('themeChanged', updateSettingsToggleUI);
    }
});
