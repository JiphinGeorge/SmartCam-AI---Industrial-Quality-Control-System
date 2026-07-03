let weeklyChartInstance = null;
let qualityChartInstance = null;
let hourlyChartInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch('/api/analytics');
        const data = await res.json();
        
        renderWeeklyTrend(data.weekly);
        renderQualityPie(data.quality);
        renderHourlyVolume(data.hourly);
        
        if (data.stats) {
            updateKPIs(data.stats, data.quality);
        }
    } catch (err) {
        console.error("Failed to load analytics data", err);
    }
});

// Common Chart.js theme defaults
Chart.defaults.color = 'rgba(255, 255, 255, 0.7)';
Chart.defaults.font.family = "'Inter', sans-serif";

function updateKPIs(stats, quality) {
    const elTotal = document.getElementById('kpi-total');
    const elConf = document.getElementById('kpi-confidence');
    const elRej = document.getElementById('kpi-rejection');
    
    if (elTotal) elTotal.textContent = stats.total_today.toLocaleString();
    if (elConf) elConf.textContent = stats.avg_confidence.toFixed(1) + '%';
    
    if (elRej) {
        const total = stats.total_today;
        const rejectCount = stats.rotten_count || 0;
        const rejRate = total > 0 ? ((rejectCount / total) * 100).toFixed(1) : '0.0';
        elRej.textContent = rejRate + '%';
    }
}

function renderWeeklyTrend(weeklyData) {
    const ctx = document.getElementById('weeklyTrendChart');
    if (!ctx) return;
    
    // Sort chronologically
    weeklyData.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    if (weeklyChartInstance) {
        weeklyChartInstance.destroy();
    }
    
    weeklyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeklyData.map(d => d.date),
            datasets: [{
                label: 'Inspections',
                data: weeklyData.map(d => d.count),
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderQualityPie(qualityData) {
    const ctx = document.getElementById('qualityPieChart');
    if (!ctx) return;
    
    const pass = qualityData['PASS'] || qualityData['Fresh'] || 0;
    const fail = qualityData['FAIL'] || qualityData['Rotten'] || 0;
    const review = qualityData['REVIEW'] || qualityData['Unknown'] || 0;
    
    if (qualityChartInstance) {
        qualityChartInstance.destroy();
    }
    
    qualityChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Pass', 'Fail', 'Review'],
            datasets: [{
                data: [pass, fail, review],
                backgroundColor: ['#10B981', '#EF4444', '#F59E0B'],
                borderWidth: 0,
                cutout: '75%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: 'rgba(255,255,255,0.7)' } }
            }
        }
    });
}

function renderHourlyVolume(hourlyData) {
    const ctx = document.getElementById('hourlyVolumeChart');
    if (!ctx) return;
    
    // Labels 00 to 23
    const labels = Array.from({length: 24}, (_, i) => i.toString().padStart(2, '0'));
    const data = labels.map(hr => hourlyData[hr] || 0);
    
    if (hourlyChartInstance) {
        hourlyChartInstance.destroy();
    }
    
    hourlyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Volume',
                data: data,
                backgroundColor: '#6366f1',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}
