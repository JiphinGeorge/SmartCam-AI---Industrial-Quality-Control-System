from flask import Blueprint, request, jsonify, Response, send_file
import os
import time
from datetime import datetime
import psutil
import uuid

from app.config import Config
from app.services.predictor import PredictorService
from app.services.database import DatabaseService
from app.services.analytics import AnalyticsService
from app.services.report import ReportService
from app.services.notification import NotificationService
from app.services.camera import camera_service
from app.services.gradcam import GradCamService

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model": "loaded" if PredictorService._model is not None else "not loaded",
        "database": "connected",
        "camera": "ready" if camera_service.is_connected else "disconnected"
    })

@api_bp.route('/api/system_status', methods=['GET'])
def system_status():
    return jsonify({
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "ai_online": PredictorService._model is not None,
        "camera_connected": camera_service.is_connected
    })

@api_bp.route('/api/stats', methods=['GET'])
def get_stats():
    conn = DatabaseService.get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM predictions WHERE date(timestamp) = ?", (today,))
    rows = cursor.fetchall()
    
    total = len(rows)
    fresh = sum(1 for r in rows if r['prediction'] == 'Fresh')
    rotten = sum(1 for r in rows if r['prediction'] == 'Rotten')
    unknown = sum(1 for r in rows if r['prediction'] == 'Unknown')
    avg_conf = sum(r['confidence'] for r in rows) / total if total > 0 else 0
    avg_time = sum(r['inference_time_ms'] for r in rows) / total if total > 0 else 0
    
    conn.close()
    
    return jsonify({
        "total_today": total,
        "fresh_count": fresh,
        "rotten_count": rotten,
        "unknown_count": unknown,
        "avg_confidence": avg_conf,
        "avg_time": avg_time
    })

@api_bp.route('/api/export', methods=['GET'])
def export():
    return ReportService.export_csv()

@api_bp.route('/api/report/pdf', methods=['GET'])
def export_pdf():
    from app.services.pdf_generator import PdfGeneratorService
    pdf_path = PdfGeneratorService.generate_daily_report()
    return send_file(pdf_path, as_attachment=True, download_name=f"SmartCam_Report_{datetime.now().strftime('%Y%m%d')}.pdf")

@api_bp.route('/api/predict', methods=['POST'])
def predict():
    start_total = time.time()
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
        
    file = request.files['image']
    source = request.form.get('source', 'upload')
    
    start_load = time.time()
    # Generate unique filename based on date
    now = datetime.now()
    year_month = now.strftime('%Y/%m')
    save_dir = os.path.join(Config.INSPECTION_HISTORY_DIR, year_month)
    os.makedirs(save_dir, exist_ok=True)
    
    unique_id = uuid.uuid4().hex[:8]
    filename = f"{now.strftime('%d_%H%M%S')}_{unique_id}.jpg"
    img_path = os.path.join(save_dir, filename)
    file.save(img_path)
    time_load = int((time.time() - start_load) * 1000)
    
    # Predict
    result = PredictorService.predict(img_path)
    
    # Generate Grad-CAM (save alongside original)
    start_gradcam = time.time()
    heatmap_path = os.path.join(save_dir, f"heatmap_{os.path.splitext(filename)[0]}.jpg")
    GradCamService.generate_heatmap(img_path, save_path=heatmap_path)
    time_gradcam = int((time.time() - start_gradcam) * 1000)
    
    # Inspection ID
    inspection_id = f"QC-{now.strftime('%Y%m%d-%H%M%S')}"
    result['inspection_id'] = inspection_id
    
    # Log to DB
    start_db = time.time()
    DatabaseService.log_prediction(
        inspection_id=inspection_id,
        filename=filename,
        prediction=result['prediction'],
        confidence=result['confidence'],
        status=result['status'],
        inference_time_ms=result['time_inference'],
        image_path=img_path,
        camera_source=source,
        gradcam_path=heatmap_path
    )
    time_db = int((time.time() - start_db) * 1000)
    
    time_total = int((time.time() - start_total) * 1000)
    
    result['timeline'] = {
        'Image Loaded': f"{max(1, time_load)} ms",
        'Preprocessing': f"{max(1, result['time_preprocess'])} ms",
        'AI Inference': f"{max(1, result['time_inference'])} ms",
        'Grad-CAM': f"{max(1, time_gradcam)} ms",
        'Database': f"{max(1, time_db)} ms",
        'Total': f"{time_total} ms"
    }
    
    # Notifications
    if result['status'] == 'FAIL':
        NotificationService.send_rotten_alert(filename, result['confidence'], result['time_inference'])
        
    # Trigger UI update
    import psutil
    from app import socketio
    socketio.emit('new_prediction', {
        'inspection_id': inspection_id,
        'prediction': result['prediction'],
        'confidence': result['confidence'],
        'confidence_level': result['confidence_level'],
        'status': result['status'],
        'time_ms': time_total,
        'timestamp': now.strftime('%H:%M:%S'),
        'explanation': result['explanation'],
        'timeline': result['timeline'],
        'telemetry': {
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'fps': round(1000.0 / max(1, time_total), 1)
        }
    })
    
    result['image_url'] = f"/inspection_history/{year_month}/{filename}"
    result['heatmap_url'] = f"/inspection_history/{year_month}/heatmap_{os.path.splitext(filename)[0]}.jpg"
    
    return jsonify(result)

def generate_video_stream():
    """Generator for MJPEG video stream."""
    while True:
        frame = camera_service.get_jpeg_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.1)

@api_bp.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@api_bp.route('/history', methods=['GET'])
def get_history():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    status = request.args.get('status')
    if status == 'All':
        status = None
    sort_by = request.args.get('sort_by', 'timestamp DESC')
    
    data = DatabaseService.get_history(page, limit, status, sort_by)
    
    # Map image paths to web URLs
    for row in data['data']:
        if row.get('image_path'):
            # On windows, it might have backslashes. Convert to web-safe URL.
            path_str = row['image_path'].replace('\\', '/')
            if 'app/' in path_str:
                row['image_url'] = '/' + path_str.split('app/')[1]
            elif 'app/static/' in path_str:
                row['image_url'] = path_str.split('app/')[1]
            else:
                row['image_url'] = '/static/images/placeholder.jpg'
                
    return jsonify(data)

@api_bp.route('/analytics', methods=['GET'])
def get_analytics():
    from app.services.analytics import AnalyticsService
    data = AnalyticsService.get_timeseries_data()
    data['stats'] = AnalyticsService.get_dashboard_stats()
    return jsonify(data)

@api_bp.route('/dataset_stats', methods=['GET'])
def get_dataset_stats():
    import os
    dataset_dir = "dataset"
    try:
        fresh_train = len(os.listdir(os.path.join(dataset_dir, 'train', 'fresh')))
        rotten_train = len(os.listdir(os.path.join(dataset_dir, 'train', 'rotten')))
        fresh_test = len(os.listdir(os.path.join(dataset_dir, 'test', 'fresh')))
        rotten_test = len(os.listdir(os.path.join(dataset_dir, 'test', 'rotten')))
        
        total_fresh = fresh_train + fresh_test
        total_rotten = rotten_train + rotten_test
        total = total_fresh + total_rotten
        
        # Calculate size (rough estimate)
        def get_size(start_path = '.'):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
            return total_size
            
        size_bytes = get_size(dataset_dir)
        size_mb = size_bytes / (1024 * 1024)
        
        train_pct = round((fresh_train + rotten_train) / total * 100) if total > 0 else 80
        test_pct = 100 - train_pct
        
        return jsonify({
            'total_fresh': total_fresh,
            'total_rotten': total_rotten,
            'total_images': total,
            'size_mb': round(size_mb, 1),
            'split_train': train_pct,
            'split_test': test_pct
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


