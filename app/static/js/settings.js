document.addEventListener('DOMContentLoaded', async () => {
    
    // Toggle switch UI logic
    document.querySelectorAll('.toggle-checkbox').forEach(checkbox => {
        const updateToggle = () => {
            const dot = checkbox.parentElement.querySelector('.toggle-dot');
            const bg = checkbox.parentElement.querySelector('.toggle-label');
            if(checkbox.checked) {
                dot.classList.add('translate-x-4', 'bg-white');
                dot.classList.remove('bg-outline-variant');
                bg.classList.add('bg-blue-500');
                bg.classList.remove('bg-surface-container-highest');
            } else {
                dot.classList.remove('translate-x-4', 'bg-white');
                dot.classList.add('bg-outline-variant');
                bg.classList.remove('bg-blue-500');
                bg.classList.add('bg-surface-container-highest');
            }
        };
        
        // Listen
        checkbox.addEventListener('change', updateToggle);
    });

    const elCrit = document.getElementById('set-critical-alerts');
    const elEmail = document.getElementById('set-email-digest');
    const elVol = document.getElementById('set-volume');
    const elTone = document.getElementById('set-tone');
    
    // Fetch settings
    try {
        const res = await fetch('/api/settings');
        const data = await res.json();
        
        if (data && !data.error) {
            if (elCrit) elCrit.checked = (data.critical_alerts === 'true');
            if (elEmail) elEmail.checked = (data.email_digest === 'true');
            if (elVol) elVol.value = data.alarm_volume || 85;
            if (elTone && data.alert_tone) elTone.value = data.alert_tone;
            
            // manually trigger change to update toggle UI
            document.querySelectorAll('.toggle-checkbox').forEach(c => c.dispatchEvent(new Event('change')));
        }
    } catch (e) {
        console.error("Failed to load settings:", e);
    }
    
    // Save settings
    const btnSave = document.getElementById('btn-save-settings');
    if (btnSave) {
        btnSave.addEventListener('click', async () => {
            const payload = {};
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
                    setTimeout(() => btnSave.textContent = originalText, 2000);
                }
            } catch (e) {
                console.error("Failed to save settings:", e);
                btnSave.textContent = 'Error';
                setTimeout(() => btnSave.textContent = originalText, 2000);
            }
        });
    }
});
