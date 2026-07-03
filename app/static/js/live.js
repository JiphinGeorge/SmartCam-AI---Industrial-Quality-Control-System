document.addEventListener('DOMContentLoaded', () => {
    const logContainer = document.getElementById('event-log');
    let totalProcessed = 0; // Local counter for the session

    // Initialize Socket.IO
    const socket = io();

    socket.on('connect', () => {
        console.log("Connected to WebSocket");
        addSystemLog("System Online: Connected to telemetry stream", "bg-primary text-on-primary");
    });

    socket.on('disconnect', () => {
        console.log("Disconnected from WebSocket");
        addSystemLog("System Offline: Connection lost", "bg-error text-on-error");
    });

    socket.on('new_prediction', (data) => {
        totalProcessed++;
        
        // Update Telemetry
        if (data.telemetry) {
            document.getElementById('telemetry-fps').innerHTML = `${data.telemetry.fps} <span class="font-mono-data text-[12px] text-on-surface-variant">FPS</span>`;
            document.getElementById('telemetry-cpu').innerHTML = `${data.telemetry.cpu} <span class="font-mono-data text-[12px] text-on-surface-variant">%</span>`;
            document.getElementById('telemetry-ram').innerHTML = `${data.telemetry.ram} <span class="font-mono-data text-[12px] text-error/70">%</span>`;
        }
        
        const totalEl = document.getElementById('telemetry-total');
        if (totalEl) {
            totalEl.textContent = totalProcessed.toLocaleString();
        }

        // Add Log Entry
        const time = data.timestamp;
        const id = data.inspection_id.substring(data.inspection_id.length - 6); // Just get last 6 chars for display
        const conf = data.confidence.toFixed(1);
        
        const div = document.createElement('div');
        
        if (data.status === 'FAIL') {
            div.className = 'flex items-center gap-2 py-1 px-2 bg-error/10 border border-error/20 rounded transition-colors group animate-[pulse-dot_0.5s_ease-out]';
            div.innerHTML = `
                <span class="text-error/70 text-[10px]">${time}</span>
                <span class="w-2 h-2 rounded-full bg-error"></span>
                <span class="text-error flex-1">Item ${id}: Rejected</span>
                <span class="text-error font-bold text-[10px]">${conf}%</span>
            `;
        } else if (data.status === 'REVIEW') {
            div.className = 'flex items-center gap-2 py-1 px-2 bg-[#fb8c00]/10 border border-[#fb8c00]/20 rounded transition-colors group';
            div.innerHTML = `
                <span class="text-[#fb8c00]/70 text-[10px]">${time}</span>
                <span class="w-2 h-2 rounded-full bg-[#fb8c00]"></span>
                <span class="text-[#fb8c00] flex-1">Item ${id}: Review</span>
                <span class="text-[#fb8c00] font-bold text-[10px]">${conf}%</span>
            `;
        } else {
            div.className = 'flex items-center gap-2 py-1 px-2 hover:bg-white/5 rounded transition-colors group';
            div.innerHTML = `
                <span class="text-on-surface-variant text-[10px] opacity-70">${time}</span>
                <span class="w-2 h-2 rounded-full bg-tertiary"></span>
                <span class="text-on-surface flex-1">Item ${id}: Pass</span>
                <span class="text-tertiary opacity-0 group-hover:opacity-100 transition-opacity text-[10px]">${conf}%</span>
            `;
        }

        logContainer.insertBefore(div, logContainer.firstChild);
        
        // Keep list manageable
        if (logContainer.children.length > 50) {
            logContainer.removeChild(logContainer.lastChild);
        }
    });

    function addSystemLog(msg, colorClass) {
        const div = document.createElement('div');
        const time = new Date().toISOString().substring(11, 22);
        div.className = `flex items-center gap-2 py-1 px-2 rounded transition-colors ${colorClass}`;
        div.innerHTML = `
            <span class="opacity-70 text-[10px]">${time}</span>
            <span class="w-2 h-2 rounded-full bg-current"></span>
            <span class="flex-1">${msg}</span>
        `;
        logContainer.insertBefore(div, logContainer.firstChild);
    }
});
