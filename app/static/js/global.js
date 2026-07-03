document.addEventListener("DOMContentLoaded", function() {
    // Topbar Clock Logic
    const clockEl = document.getElementById("topbar-clock");
    if (clockEl) {
        function updateClock() {
            const now = new Date();
            // Format to local time string like "HH:MM"
            const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            clockEl.textContent = "Local " + timeString;
        }
        updateClock();
        setInterval(updateClock, 1000 * 60); // Update every minute
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
});
