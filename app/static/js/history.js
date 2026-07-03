document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('history-container');
    const paginationControls = document.getElementById('pagination-controls');
    
    let currentPage = 1;
    let currentLimit = 10;
    let currentStatus = 'All';
    let currentSort = 'timestamp DESC';
    
    const urlParams = new URLSearchParams(window.location.search);
    let currentSearchQuery = urlParams.get('q') || '';

    async function loadHistory() {
        try {
            const res = await fetch(`/api/history?page=${currentPage}&limit=${currentLimit}&status=${currentStatus}&sort_by=${currentSort}&q=${encodeURIComponent(currentSearchQuery)}`);
            const data = await res.json();
            
            renderRows(data.data);
            renderPagination(data.page, data.pages, data.total);
        } catch (error) {
            console.error("Failed to load history:", error);
            container.innerHTML = `<div class="p-md text-error">Failed to load history data.</div>`;
        }
    }

    function renderRows(rows) {
        if (rows.length === 0) {
            container.innerHTML = `<div class="p-md text-on-surface-variant text-center mt-8">No records found.</div>`;
            return;
        }

        container.innerHTML = rows.map(row => {
            const dateObj = new Date(row.timestamp);
            const dateStr = dateObj.toISOString().split('T')[0];
            const timeStr = dateObj.toISOString().split('T')[1].substring(0, 12) + "Z";
            
            let statusColor = '';
            let statusIcon = '';
            let statusText = row.status;
            
            if (row.status === 'PASS' || row.status === 'Fresh') {
                statusColor = 'emerald-500';
                statusIcon = 'check_circle';
            } else if (row.status === 'FAIL' || row.status === 'Rotten') {
                statusColor = 'error';
                statusIcon = 'warning';
            } else {
                statusColor = 'tertiary';
                statusIcon = 'help';
            }

            const imgHtml = row.image_url 
                ? `<img class="w-full h-full object-cover" src="${row.image_url}" />` 
                : `<div class="w-full h-full bg-surface-container flex items-center justify-center"><span class="material-symbols-outlined text-outline-variant text-[24px]">image_not_supported</span></div>`;

            return `
            <div class="grid grid-cols-12 gap-4 px-md py-sm border-b border-white/5 items-center table-row-hover transition-all duration-200">
                <div class="col-span-2 font-mono-data text-mono-data text-on-surface">
                    ${dateStr}<br/>
                    <span class="text-on-surface-variant text-[12px]">${timeStr}</span>
                </div>
                <div class="col-span-1">
                    <div class="w-12 h-12 rounded bg-surface-dim border border-white/10 overflow-hidden relative group">
                        ${imgHtml}
                    </div>
                </div>
                <div class="col-span-2 flex items-center">
                    <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-${statusColor}/10 border border-${statusColor}/20 text-${statusColor} font-label-sm text-label-sm">
                        <span class="material-symbols-outlined text-[14px]">${statusIcon}</span>
                        ${statusText}
                    </div>
                </div>
                <div class="col-span-2 flex items-center gap-2">
                    <span class="font-mono-data text-mono-data text-on-surface font-semibold w-10 text-${statusColor}">${row.confidence.toFixed(1)}%</span>
                    <div class="flex-1 h-1.5 bg-surface-dim rounded-full overflow-hidden">
                        <div class="h-full bg-${statusColor} w-[${row.confidence.toFixed(1)}%]"></div>
                    </div>
                </div>
                <div class="col-span-2 flex flex-col justify-center">
                    <span class="font-mono-data text-[12px] text-on-surface-variant">INF: ${Math.round(row.inference_time_ms)}ms</span>
                    <span class="font-mono-data text-[12px] text-on-surface-variant">OP: ${row.operator || 'System'}</span>
                </div>
                <div class="col-span-1 flex items-center">
                    <span class="material-symbols-outlined text-outline-variant text-[20px]" title="Stored">cloud_done</span>
                </div>
                <div class="col-span-2 flex items-center justify-end gap-2 opacity-50 hover:opacity-100 transition-opacity">
                    <button class="p-1.5 rounded text-on-surface-variant hover:text-error hover:bg-error-container/20 transition-colors" title="Delete">
                        <span class="material-symbols-outlined text-[18px]">delete</span>
                    </button>
                </div>
            </div>
            `;
        }).join('');
    }

    function renderPagination(page, pages, total) {
        const startItem = ((page - 1) * currentLimit) + 1;
        const endItem = Math.min(page * currentLimit, total);
        
        let html = `
        <div class="font-label-sm text-label-sm text-on-surface-variant">
            Showing <span class="text-on-surface font-semibold">${total > 0 ? startItem : 0}</span> to <span class="text-on-surface font-semibold">${endItem}</span> of <span class="text-on-surface font-semibold">${total.toLocaleString()}</span> entries
        </div>
        <div class="flex items-center gap-1">
            <button onclick="window.changePage(${page - 1})" class="p-1.5 rounded-lg border border-white/10 text-on-surface-variant hover:bg-white/5 hover:text-on-surface transition-colors disabled:opacity-50 disabled:cursor-not-allowed" ${page <= 1 ? 'disabled' : ''}>
                <span class="material-symbols-outlined text-[18px]">chevron_left</span>
            </button>
        `;
        
        // Simple pagination buttons (showing few pages for simplicity)
        for (let i = 1; i <= pages; i++) {
            if (i === page) {
                html += `<button class="w-8 h-8 rounded-lg bg-primary/20 text-primary font-label-md text-label-md font-bold flex items-center justify-center border border-primary/30">${i}</button>`;
            } else if (i === 1 || i === pages || (i >= page - 1 && i <= page + 1)) {
                html += `<button onclick="window.changePage(${i})" class="w-8 h-8 rounded-lg text-on-surface-variant hover:bg-white/5 hover:text-on-surface font-label-md text-label-md flex items-center justify-center transition-colors">${i}</button>`;
            } else if (i === page - 2 || i === page + 2) {
                html += `<span class="text-on-surface-variant mx-1">...</span>`;
            }
        }

        html += `
            <button onclick="window.changePage(${page + 1})" class="p-1.5 rounded-lg border border-white/10 text-on-surface-variant hover:bg-white/5 hover:text-on-surface transition-colors disabled:opacity-50 disabled:cursor-not-allowed" ${page >= pages ? 'disabled' : ''}>
                <span class="material-symbols-outlined text-[18px]">chevron_right</span>
            </button>
        </div>
        `;
        
        paginationControls.innerHTML = html;
    }

    // Expose to window for inline onclick handlers
    window.changePage = function(newPage) {
        currentPage = newPage;
        loadHistory();
    };

    // Initial load
    loadHistory();
});
