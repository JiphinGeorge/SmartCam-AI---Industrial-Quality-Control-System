document.addEventListener('DOMContentLoaded', () => {
    const btnUpload = document.getElementById('btn-upload');
    const btnBatch = document.getElementById('btn-batch');
    const btnCamera = document.getElementById('btn-camera');
    const btnCapture = document.getElementById('btn-capture');
    const fileUpload = document.getElementById('file-upload');
    const batchUpload = document.getElementById('batch-upload');
    const video = document.getElementById('webcam-video');
    const preview = document.getElementById('preview-image');
    
    let stream = null;

    btnUpload.addEventListener('click', () => {
        fileUpload.click();
    });

    fileUpload.addEventListener('change', async (e) => {
        if (e.target.files.length > 0) {
            stopWebcam();
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append('image', file);
            formData.append('source', 'upload');
            
            // Preview locally
            preview.src = URL.createObjectURL(file);
            preview.classList.remove('hidden');
            video.classList.add('hidden');
            
            await submitPrediction(formData);
        }
    });

    btnBatch.addEventListener('click', () => {
        batchUpload.click();
    });

    batchUpload.addEventListener('change', async (e) => {
        if (e.target.files.length > 0) {
            stopWebcam();
            const files = Array.from(e.target.files);
            
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                document.getElementById('info-source').textContent = `Batch Processing ${i+1}/${files.length}`;
                
                const formData = new FormData();
                formData.append('image', file);
                formData.append('source', 'batch');
                
                preview.src = URL.createObjectURL(file);
                preview.classList.remove('hidden');
                video.classList.add('hidden');
                
                await submitPrediction(formData);
                
                // Add a small delay between batch items
                await new Promise(r => setTimeout(r, 1000));
            }
        }
    });

    btnCamera.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
            video.srcObject = stream;
            video.classList.remove('hidden');
            preview.classList.add('hidden');
            btnCapture.classList.remove('hidden');
            btnCamera.classList.add('hidden');
        } catch (err) {
            console.error("Error accessing camera: ", err);
            alert("Could not access camera.");
        }
    });

    btnCapture.addEventListener('click', async () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('image', blob, 'webcam.jpg');
            formData.append('source', 'webcam');
            
            preview.src = URL.createObjectURL(blob);
            stopWebcam();
            
            await submitPrediction(formData);
        }, 'image/jpeg');
    });

    function stopWebcam() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
            video.classList.add('hidden');
            preview.classList.remove('hidden');
            btnCapture.classList.add('hidden');
            btnCamera.classList.remove('hidden');
        }
    }

    async function submitPrediction(formData) {
        // Show loading state
        document.getElementById('gauge-text').textContent = "...";
        document.getElementById('gauge-label').textContent = "ANALYZING";
        
        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            
            if (data.error) throw new Error(data.error);
            
            updateUI(data);
        } catch (e) {
            console.error("Prediction error:", e);
            document.getElementById('gauge-label').textContent = "ERROR";
        }
    }

    function updateUI(data) {
        // Gauge
        const conf = data.confidence;
        document.getElementById('gauge-text').textContent = conf.toFixed(1) + "%";
        document.getElementById('gauge-label').textContent = data.prediction.toUpperCase();
        document.getElementById('gauge-path').setAttribute('stroke-dasharray', `${conf}, 100`);
        
        // Colors based on pass/fail
        const color = data.status === 'PASS' ? '#adc6ff' : (data.status === 'FAIL' ? '#ffb4ab' : '#fb8c00');
        const textClass = data.status === 'PASS' ? 'text-secondary' : (data.status === 'FAIL' ? 'text-error' : 'text-[#fb8c00]');
        
        document.getElementById('gauge-path').setAttribute('stroke', color);
        document.getElementById('gauge-text').className = `percentage font-mono-data ${textClass}`;
        document.getElementById('gauge-label').className = `font-headline-md text-headline-md font-bold ${textClass} shadow-sm`;

        // Info
        document.getElementById('info-source').textContent = `Source: ${document.getElementById('btn-capture').classList.contains('hidden') ? 'Local Upload' : 'Webcam'}`;
        document.getElementById('info-time').textContent = `Processing Time: ${data.timeline.Total}`;

        // Inference Details
        document.getElementById('insight-text').textContent = data.explanation || "Analyzed visually based on trained patterns.";
        
        if (data.probabilities) {
            let i = 1;
            for (const [cls, prob] of Object.entries(data.probabilities)) {
                if (i > 2) break;
                document.getElementById(`label-class-${i}`).textContent = cls;
                document.getElementById(`prob-class-${i}`).textContent = prob.toFixed(3);
                document.getElementById(`bar-class-${i}`).style.width = (prob * 100) + '%';
                i++;
            }
        }

        // Alert
        const alertBox = document.getElementById('alert-box');
        if (data.status === 'FAIL') {
            alertBox.classList.remove('hidden', 'bg-surface-container/20', 'border-white/10', 'bg-[#fb8c00]/20', 'border-[#fb8c00]/50');
            alertBox.classList.add('bg-error-container/20', 'border-error/50');
            document.getElementById('alert-icon-container').className = 'w-12 h-12 rounded-full bg-error/20 flex items-center justify-center shrink-0 border border-error/30';
            document.getElementById('alert-icon').className = 'material-symbols-outlined text-error text-[24px]';
            document.getElementById('alert-title').className = 'font-headline-md text-headline-md font-bold text-error';
            document.getElementById('alert-title').textContent = `Defect Detected: ${data.prediction}`;
            document.getElementById('alert-desc').textContent = "Immediate routing required. Item fails structural integrity checks.";
        } else if (data.status === 'REVIEW') {
            alertBox.classList.remove('hidden', 'bg-error-container/20', 'border-error/50', 'bg-surface-container/20', 'border-white/10');
            alertBox.classList.add('bg-[#fb8c00]/20', 'border-[#fb8c00]/50');
            document.getElementById('alert-icon-container').className = 'w-12 h-12 rounded-full bg-[#fb8c00]/20 flex items-center justify-center shrink-0 border border-[#fb8c00]/30';
            document.getElementById('alert-icon').className = 'material-symbols-outlined text-[#fb8c00] text-[24px]';
            document.getElementById('alert-title').className = 'font-headline-md text-headline-md font-bold text-[#fb8c00]';
            document.getElementById('alert-title').textContent = "Review Required";
            document.getElementById('alert-desc').textContent = "Confidence threshold not met. Manual inspection recommended.";
        } else {
            alertBox.classList.remove('hidden', 'bg-error-container/20', 'border-error/50', 'bg-[#fb8c00]/20', 'border-[#fb8c00]/50');
            alertBox.classList.add('bg-surface-container/20', 'border-white/10');
            document.getElementById('alert-icon-container').className = 'w-12 h-12 rounded-full bg-surface-container flex items-center justify-center shrink-0 border border-white/10';
            document.getElementById('alert-icon').className = 'material-symbols-outlined text-on-surface text-[24px]';
            document.getElementById('alert-title').className = 'font-headline-md text-headline-md font-bold text-on-surface';
            document.getElementById('alert-title').textContent = "Quality Check Passed";
            document.getElementById('alert-desc').textContent = "Item meets all freshness criteria.";
        }

        // Grad-CAM
        if (data.heatmap_url) {
            document.getElementById('gradcam-placeholder').style.display = 'none';
            const img = document.getElementById('gradcam-image');
            img.src = data.heatmap_url + '?t=' + new Date().getTime(); // cache bust
            img.style.display = 'block';
        }
    }
});
