document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch('/api/dataset_stats');
        const data = await res.json();
        
        if (data.error) {
            console.error("Dataset Error:", data.error);
            return;
        }

        const elFresh = document.getElementById('ds-fresh');
        const elRotten = document.getElementById('ds-rotten');
        const elSize = document.getElementById('ds-size');
        const elSplit = document.getElementById('ds-split');
        const elTrainPct = document.getElementById('ds-train-pct');
        const elTestPct = document.getElementById('ds-test-pct');

        if (elFresh) elFresh.textContent = data.total_fresh.toLocaleString();
        if (elRotten) elRotten.textContent = data.total_rotten.toLocaleString();
        if (elSize) elSize.innerHTML = `${data.size_mb} <span class="text-headline-md text-on-surface-variant">MB</span>`;
        if (elSplit) elSplit.textContent = `${data.split_train}/${data.split_test}`;
        if (elTrainPct) elTrainPct.textContent = data.split_train;
        if (elTestPct) elTestPct.textContent = data.split_test;

        // Update the CSS donut chart
        const donut = document.querySelector('div[style*="conic-gradient"]');
        if (donut) {
            donut.style.background = `conic-gradient(from 0deg, #3B82F6 0% ${data.split_train}%, #8B5CF6 ${data.split_train}% 100%)`;
        }

    } catch (err) {
        console.error("Failed to load dataset stats", err);
    }
});
