document.addEventListener('DOMContentLoaded', async () => {
    
    const elFact = document.getElementById('set-factory-name');
    const elTime = document.getElementById('set-timezone');
    const elCrit = document.getElementById('set-critical-alerts');
    const elEmail = document.getElementById('set-email-digest');
    const elVol = document.getElementById('set-volume');
    const elTone = document.getElementById('set-tone');
    const elThemeToggle = document.getElementById('set-theme-toggle');
    const elThemeIcon = document.getElementById('setting-theme-icon');
    const elThemeText = document.getElementById('setting-theme-text');

    function updateThemeUI() {
        const isDark = document.documentElement.classList.contains('dark');
        if (elThemeToggle) elThemeToggle.checked = isDark;
        if (elThemeIcon) elThemeIcon.textContent = isDark ? "dark_mode" : "light_mode";
        if (elThemeText) elThemeText.textContent = isDark ? "Dark Mode" : "Light Mode";
    }
    
    updateThemeUI();
    window.addEventListener('themeChanged', updateThemeUI);

    if (elThemeToggle) {
        elThemeToggle.addEventListener('change', (e) => {
            const isDark = e.target.checked;
            if (isDark) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
            localStorage.setItem("theme", isDark ? "dark" : "light");
            updateThemeUI();
            
            // Update topbar icon directly
            const topbarIcon = document.querySelector("#theme-toggle-topbar .material-symbols-outlined");
            if (topbarIcon) {
                topbarIcon.textContent = isDark ? "light_mode" : "dark_mode";
            }
        });
    }

    // Fetch settings
    try {
        const res = await fetch('/api/settings');
        const data = await res.json();
        
        if (data && !data.error) {
            if (elFact && data.factory_name) elFact.value = data.factory_name;
            if (elTime && data.timezone) elTime.value = data.timezone;
            if (elCrit) elCrit.checked = (data.critical_alerts === 'true');
            if (elEmail) elEmail.checked = (data.email_digest === 'true');
            if (elVol) {
                elVol.value = data.alarm_volume || 85;
                document.getElementById('label-volume').innerText = elVol.value + '%';
            }
            if (elTone && data.alert_tone) elTone.value = data.alert_tone;
        }
    } catch (e) {
        console.error("Failed to load settings:", e);
    }
    
    // Save settings
    const btnSave = document.getElementById('btn-save-settings');
    if (btnSave) {
        btnSave.addEventListener('click', async () => {
            const payload = {};
            if (elFact) payload.factory_name = elFact.value;
            if (elTime) payload.timezone = elTime.value;
            if (elCrit) payload.critical_alerts = elCrit.checked ? 'true' : 'false';
            if (elEmail) payload.email_digest = elEmail.checked ? 'true' : 'false';
            if (elVol) payload.alarm_volume = elVol.value;
            if (elTone) payload.alert_tone = elTone.value;
            
            const originalText = btnSave.textContent;
            btnSave.textContent = 'Saving...';
            
            try {
                const res = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    btnSave.textContent = 'Saved!';
                    btnSave.classList.add('bg-green-500');
                    setTimeout(() => {
                        btnSave.textContent = originalText;
                        btnSave.classList.remove('bg-green-500');
                    }, 2000);
                }
            } catch (e) {
                console.error("Failed to save settings:", e);
                btnSave.textContent = 'Error';
                setTimeout(() => btnSave.textContent = originalText, 2000);
            }
        });
    }
});
