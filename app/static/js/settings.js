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
    async function loadSettings() {
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
                
                // Dispatch event so topbar can update factory name if needed
                window.dispatchEvent(new CustomEvent('settingsLoaded', { detail: data }));
            }
        } catch (e) {
            console.error("Failed to load settings:", e);
        }
    }
    
    // Fetch on page load
    loadSettings();
    
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

    // Discard Changes
    const btnDiscard = document.getElementById('btn-discard');
    if (btnDiscard) {
        btnDiscard.addEventListener('click', () => {
            loadSettings(); // Reload from API without refresh
            const originalText = btnDiscard.textContent;
            btnDiscard.textContent = 'Reverted';
            setTimeout(() => btnDiscard.textContent = originalText, 1500);
        });
    }

    // Check Updates
    const btnUpdates = document.getElementById('btn-check-updates');
    if (btnUpdates) {
        btnUpdates.addEventListener('click', () => {
            const originalText = btnUpdates.innerHTML;
            btnUpdates.disabled = true;
            btnUpdates.innerHTML = `<span class="material-symbols-outlined animate-spin text-sm">sync</span> Checking...`;
            
            // Mock delay
            setTimeout(() => {
                btnUpdates.innerHTML = `<span class="material-symbols-outlined text-green-400 text-sm">check_circle</span> Up to date`;
                setTimeout(() => {
                    btnUpdates.innerHTML = originalText;
                    btnUpdates.disabled = false;
                }, 3000);
            }, 1500);
        });
    }

    // Audio Test via Web Audio API
    if (elVol) {
        elVol.addEventListener('change', () => {
            const volume = parseInt(elVol.value, 10) / 100;
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            const ctx = new AudioContext();
            const osc = ctx.createOscillator();
            const gainNode = ctx.createGain();
            
            // Tone logic
            const toneType = elTone ? elTone.value : "Beep (Standard)";
            if (toneType === "Klaxon (Industrial)") {
                osc.type = "sawtooth";
                osc.frequency.setValueAtTime(150, ctx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(300, ctx.currentTime + 0.5);
            } else if (toneType === "Chime (Subtle)") {
                osc.type = "sine";
                osc.frequency.setValueAtTime(800, ctx.currentTime);
            } else {
                osc.type = "square";
                osc.frequency.setValueAtTime(440, ctx.currentTime);
            }
            
            gainNode.gain.setValueAtTime(volume, ctx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
            
            osc.connect(gainNode);
            gainNode.connect(ctx.destination);
            
            osc.start();
            osc.stop(ctx.currentTime + 0.5);
        });
    }
});
