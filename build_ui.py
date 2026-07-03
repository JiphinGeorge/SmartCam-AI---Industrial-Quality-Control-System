import re

def build_ui():
    with open('app/templates/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # The new robust dashboard UI
    new_main = """<main class="flex-1 mt-24 mb-16 px-gutter w-full max-w-[1600px] mx-auto relative z-10">
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-lg">
        
        <!-- Left Column: Inspection Controls & Camera (Cols 1-2) -->
        <div class="lg:col-span-2 flex flex-col gap-md">
            
            <!-- Tabs for Modes -->
            <div class="glass-card rounded-xl p-sm flex gap-sm">
                <button onclick="setMode('webcam')" id="tab-webcam" class="flex-1 py-2 font-label-sm text-primary border-b-2 border-primary">LIVE WEBCAM</button>
                <button onclick="setMode('upload')" id="tab-upload" class="flex-1 py-2 font-label-sm text-on-surface-variant hover:text-primary">IMAGE UPLOAD</button>
                <button onclick="setMode('batch')" id="tab-batch" class="flex-1 py-2 font-label-sm text-on-surface-variant hover:text-primary">BATCH SCAN</button>
            </div>
            
            <!-- Vision Window -->
            <div class="glass-card rounded-xl overflow-hidden relative border border-white/10" style="aspect-ratio: 4/3;">
                <img id="video-feed" src="/video_feed" class="w-full h-full object-cover bg-black" alt="Live Feed" />
                
                <div id="upload-mode-ui" class="absolute inset-0 bg-surface/90 hidden flex flex-col items-center justify-center p-lg text-center">
                    <span class="material-symbols-outlined text-4xl text-primary mb-4">upload_file</span>
                    <h3 class="text-on-surface font-title-md mb-2">Upload Inspection Image</h3>
                    <input type="file" id="image-upload" class="hidden" accept="image/*" onchange="handleUpload(this)">
                    <button onclick="document.getElementById('image-upload').click()" class="bg-primary-container text-on-primary px-6 py-2 rounded-lg font-label-sm hover:opacity-90 glow-primary">SELECT FILE</button>
                </div>
                
                <div id="batch-mode-ui" class="absolute inset-0 bg-surface/90 hidden flex flex-col items-center justify-center p-lg text-center">
                    <span class="material-symbols-outlined text-4xl text-primary mb-4">folder_open</span>
                    <h3 class="text-on-surface font-title-md mb-2">Batch Folder Inspection</h3>
                    <button onclick="alert('Batch mode active')" class="bg-primary-container text-on-primary px-6 py-2 rounded-lg font-label-sm hover:opacity-90 glow-primary">START BATCH</button>
                </div>

                <div class="absolute inset-0 bg-gradient-to-t from-surface-container-highest/90 to-transparent pointer-events-none flex items-end p-sm">
                    <span class="font-mono-data text-primary bg-surface/80 px-sm py-xs rounded border border-white/10 flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-primary status-dot"></div> <span id="camera-status">WEBCAM_ACTIVE</span>
                    </span>
                </div>
            </div>
            
        </div>
        
        <!-- Right Column 1: AI Analysis & Grad-CAM (Col 3) -->
        <div class="flex flex-col gap-md">
            <!-- Latest Prediction Card -->
            <div class="glass-card rounded-xl p-md border border-white/5 relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4"><span class="material-symbols-outlined text-secondary opacity-20 text-6xl">memory</span></div>
                <h3 class="font-label-sm text-on-surface-variant mb-4 flex items-center gap-2"><span class="material-symbols-outlined text-lg">policy</span> LATEST ANALYSIS</h3>
                
                <div class="flex justify-between items-end border-b border-white/10 pb-4 mb-4">
                    <div>
                        <div class="text-xs text-on-surface-variant mb-1">PREDICTION</div>
                        <div id="live-prediction" class="font-headline-lg text-primary">WAITING</div>
                    </div>
                    <div class="text-right">
                        <div class="text-xs text-on-surface-variant mb-1">STATUS</div>
                        <div id="live-status" class="font-mono-data bg-surface px-2 py-1 rounded text-primary border border-white/5">--</div>
                    </div>
                </div>
                
                <div class="space-y-3 font-mono-data text-sm">
                    <div class="flex justify-between">
                        <span class="text-on-surface-variant">CONFIDENCE</span>
                        <span id="live-confidence" class="text-on-surface">--%</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-on-surface-variant">INFERENCE_TIME</span>
                        <span id="live-time" class="text-on-surface">--ms</span>
                    </div>
                </div>
            </div>
            
            <!-- AI Focus Area (Grad-CAM) -->
            <div class="glass-card rounded-xl p-md border border-white/5 flex-1 flex flex-col">
                <h3 class="font-label-sm text-on-surface-variant mb-4 flex items-center gap-2"><span class="material-symbols-outlined text-lg">visibility</span> AI FOCUS AREA</h3>
                <div class="w-full flex-1 rounded-lg bg-surface-container overflow-hidden relative border border-white/10 flex items-center justify-center">
                    <img id="heatmap-image" src="" class="w-full h-full object-cover hidden" />
                    <span id="heatmap-placeholder" class="text-on-surface-variant font-mono-data text-xs">AWAITING_INSPECTION</span>
                </div>
            </div>
        </div>
        
        <!-- Right Column 2: Dashboard Widgets & Timeline (Col 4) -->
        <div class="flex flex-col gap-md">
            
            <!-- Quick Stats -->
            <div class="grid grid-cols-2 gap-sm">
                <div class="glass-card rounded-xl p-sm border border-white/5 text-center">
                    <div class="text-xs font-label-sm text-on-surface-variant mb-1">TOTAL_TODAY</div>
                    <div id="stat-total" class="font-headline-lg-mobile text-on-surface">0</div>
                </div>
                <div class="glass-card rounded-xl p-sm border border-white/5 text-center">
                    <div class="text-xs font-label-sm text-on-surface-variant mb-1">FRESH</div>
                    <div id="stat-fresh" class="font-headline-lg-mobile text-primary">0</div>
                </div>
                <div class="glass-card rounded-xl p-sm border border-white/5 text-center">
                    <div class="text-xs font-label-sm text-on-surface-variant mb-1">ROTTEN</div>
                    <div id="stat-rotten" class="font-headline-lg-mobile text-error">0</div>
                </div>
                <div class="glass-card rounded-xl p-sm border border-white/5 text-center">
                    <div class="text-xs font-label-sm text-on-surface-variant mb-1">AVG_CONF</div>
                    <div id="stat-avg-conf" class="font-headline-lg-mobile text-secondary">0%</div>
                </div>
            </div>
            
            <!-- Model Metadata -->
            <div class="glass-card rounded-xl p-md border border-white/5">
                <h3 class="font-label-sm text-on-surface-variant mb-3 flex items-center gap-2"><span class="material-symbols-outlined text-lg">model_training</span> MODEL_METADATA</h3>
                <div class="space-y-2 font-mono-data text-xs">
                    <div class="flex justify-between"><span class="text-on-surface-variant">Architecture</span><span class="text-on-surface">EfficientNetV2B0</span></div>
                    <div class="flex justify-between"><span class="text-on-surface-variant">Version</span><span class="text-on-surface">{{ metadata.version }}</span></div>
                    <div class="flex justify-between"><span class="text-on-surface-variant">Accuracy</span><span class="text-on-surface text-primary">{{ metadata.accuracy }}</span></div>
                    <div class="flex justify-between"><span class="text-on-surface-variant">Training_Date</span><span class="text-on-surface">{{ metadata.training_date }}</span></div>
                </div>
            </div>

            <!-- Activity Timeline -->
            <div class="glass-card rounded-xl p-md border border-white/5 flex-1 flex flex-col overflow-hidden">
                <h3 class="font-label-sm text-on-surface-variant mb-3 flex items-center gap-2"><span class="material-symbols-outlined text-lg">history</span> ACTIVITY_LOG</h3>
                <div id="timeline" class="flex-1 overflow-y-auto space-y-3 pr-2">
                    <!-- Dynamic timeline items -->
                </div>
            </div>
            
            <a href="/api/export" target="_blank" class="bg-secondary-container text-on-secondary px-6 py-3 rounded-lg font-label-sm hover:opacity-90 transition-opacity text-center flex justify-center items-center gap-2"><span class="material-symbols-outlined">download</span> EXPORT REPORT (CSV)</a>
        </div>
    </div>
    
    <!-- System Health Footer Widget -->
    <div class="mt-md glass-card rounded-xl p-sm flex justify-around border border-white/5 font-mono-data text-xs">
        <div class="flex items-center gap-2"><div id="health-db" class="w-2 h-2 rounded-full bg-primary"></div> DB_CONNECTED</div>
        <div class="flex items-center gap-2"><div id="health-ai" class="w-2 h-2 rounded-full bg-primary"></div> AI_ONLINE</div>
        <div class="flex items-center gap-2"><span class="text-on-surface-variant">CPU:</span> <span id="health-cpu">--%</span></div>
        <div class="flex items-center gap-2"><span class="text-on-surface-variant">MEM:</span> <span id="health-mem">--%</span></div>
    </div>
</main>
"""

    scripts = """
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.1/socket.io.js"></script>
    <script>
        const socket = io();
        
        function setMode(mode) {
            // Update tabs
            ['webcam', 'upload', 'batch'].forEach(m => {
                const btn = document.getElementById('tab-' + m);
                btn.className = (m === mode) ? "flex-1 py-2 font-label-sm text-primary border-b-2 border-primary" : "flex-1 py-2 font-label-sm text-on-surface-variant hover:text-primary";
                document.getElementById(m + '-mode-ui')?.classList.add('hidden');
            });
            
            if(mode === 'webcam') {
                document.getElementById('video-feed').classList.remove('hidden');
                document.getElementById('camera-status').textContent = 'WEBCAM_ACTIVE';
            } else {
                document.getElementById('video-feed').classList.add('hidden');
                document.getElementById(mode + '-mode-ui').classList.remove('hidden');
                document.getElementById('camera-status').textContent = mode.toUpperCase() + '_READY';
            }
        }
        
        function handleUpload(input) {
            if (input.files && input.files[0]) {
                const formData = new FormData();
                formData.append('image', input.files[0]);
                formData.append('source', 'upload');
                
                fetch('/api/predict', { method: 'POST', body: formData })
                    .then(r => r.json())
                    .then(data => {
                        // The server will also emit a socket event which updates the UI
                        console.log("Uploaded successfully", data);
                        
                        // Set the uploaded image as the main feed temporarily
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            document.getElementById('video-feed').src = e.target.result;
                            document.getElementById('video-feed').classList.remove('hidden');
                            document.getElementById('upload-mode-ui').classList.add('hidden');
                        }
                        reader.readAsDataURL(input.files[0]);
                        
                        // Set heatmap
                        setTimeout(() => {
                            // Fetch heatmap
                            document.getElementById('heatmap-image').src = '/inspection_history/' + new Date().getFullYear() + '/' + (new Date().getMonth()+1).toString().padStart(2, '0') + '/heatmap_' + data.filename;
                            document.getElementById('heatmap-image').classList.remove('hidden');
                            document.getElementById('heatmap-placeholder').classList.add('hidden');
                        }, 500);
                    });
            }
        }
        
        socket.on('new_prediction', function(data) {
            // Update live card
            document.getElementById('live-prediction').textContent = data.prediction;
            document.getElementById('live-prediction').className = 'font-headline-lg ' + (data.prediction === 'Fresh' ? 'text-primary' : 'text-error');
            document.getElementById('live-status').textContent = data.status;
            document.getElementById('live-status').className = 'font-mono-data px-2 py-1 rounded border border-white/5 ' + (data.status === 'PASS' ? 'bg-primary-container/20 text-primary' : 'bg-error-container/20 text-error');
            document.getElementById('live-confidence').textContent = data.confidence.toFixed(1) + '%';
            document.getElementById('live-time').textContent = data.time_ms + 'ms';
            
            // Add to timeline
            const timeline = document.getElementById('timeline');
            const item = document.createElement('div');
            item.className = 'text-xs pb-3 border-b border-white/5';
            item.innerHTML = `<div class="flex justify-between mb-1"><span class="text-on-surface-variant">${data.timestamp}</span><span class="${data.status === 'PASS' ? 'text-primary' : 'text-error'}">${data.status}</span></div>
                              <div class="flex justify-between font-mono-data"><span class="text-on-surface">${data.prediction}</span><span class="text-on-surface-variant">${data.confidence.toFixed(1)}%</span></div>`;
            timeline.prepend(item);
            
            // Limit timeline to 10 items
            if(timeline.children.length > 10) timeline.lastChild.remove();
            
            // Refresh stats
            fetchStats();
        });
        
        socket.on('notification', function(data) {
            if(data.type === 'alert') {
                // Flash the screen or show toast
                document.body.classList.add('bg-error/20');
                setTimeout(() => document.body.classList.remove('bg-error/20'), 500);
            }
        });
        
        function fetchStats() {
            fetch('/api/stats').then(r => r.json()).then(data => {
                document.getElementById('stat-total').textContent = data.total_today;
                document.getElementById('stat-fresh').textContent = data.fresh_count;
                document.getElementById('stat-rotten').textContent = data.rotten_count;
                document.getElementById('stat-avg-conf').textContent = data.avg_confidence.toFixed(1) + '%';
            });
        }
        
        function fetchHealth() {
            fetch('/api/system_status').then(r => r.json()).then(data => {
                document.getElementById('health-cpu').textContent = data.cpu_percent + '%';
                document.getElementById('health-mem').textContent = data.memory_percent + '%';
                document.getElementById('health-db').className = "w-2 h-2 rounded-full bg-primary"; // Assume DB always connected for now
                document.getElementById('health-ai').className = "w-2 h-2 rounded-full " + (data.ai_online ? 'bg-primary' : 'bg-error status-dot');
            });
        }
        
        setInterval(fetchHealth, 5000);
        
        // Initial fetch
        fetchStats();
        fetchHealth();
        setMode('webcam');
    </script>
    """

    # Replace <main>...</main>
    new_html = re.sub(r'<main.*?</main>', new_main, html, flags=re.DOTALL)
    
    # Insert scripts before </body>
    new_html = new_html.replace('</body>', scripts + '\n</body>')

    with open('app/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

if __name__ == '__main__':
    build_ui()
