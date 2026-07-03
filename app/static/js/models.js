document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch('/api/model_stats');
        const data = await res.json();
        
        if (data.error) {
            console.error("Model Stats Error:", data.error);
            return;
        }

        const elAcc = document.getElementById('model-acc');
        const elInf = document.getElementById('model-inf');
        const elSize = document.getElementById('model-size');
        const elTf = document.getElementById('model-tf');

        if (elAcc) elAcc.innerHTML = `${data.accuracy}<span class="text-[20px] text-outline-variant">%</span>`;
        if (elInf) elInf.innerHTML = `${Math.round(data.inference_time)}<span class="text-[20px] text-outline-variant">ms</span>`;
        if (elSize) elSize.innerHTML = `${data.size_mb}<span class="text-[20px] text-outline-variant">MB</span>`;
        if (elTf) elTf.textContent = `TF v${data.tf_version}`;

    } catch (err) {
        console.error("Failed to load model stats", err);
    }
});
