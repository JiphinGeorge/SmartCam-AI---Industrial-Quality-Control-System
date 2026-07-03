import os
import time
import requests
import psutil
import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
import cv2
import numpy as np

BASE_URL = "http://localhost:5000"
API_PREDICT = f"{BASE_URL}/api/predict"
API_REPORTS = f"{BASE_URL}/api/reports/download"

TEST_DIR = "stress_test_images"
os.makedirs(TEST_DIR, exist_ok=True)

# 1. Synthesize Images
def generate_images():
    print("[*] Synthesizing test images...")
    images = {}
    
    # Fresh Tomato (Red)
    img_fresh = np.zeros((224, 224, 3), dtype=np.uint8)
    cv2.circle(img_fresh, (112, 112), 80, (0, 0, 255), -1)
    cv2.imwrite(os.path.join(TEST_DIR, "fresh.jpg"), img_fresh)
    images["fresh"] = os.path.join(TEST_DIR, "fresh.jpg")
    
    # Rotten Tomato (Brown/Black spots)
    img_rotten = np.zeros((224, 224, 3), dtype=np.uint8)
    cv2.circle(img_rotten, (112, 112), 80, (0, 0, 150), -1)
    cv2.circle(img_rotten, (100, 100), 20, (0, 0, 0), -1)
    cv2.imwrite(os.path.join(TEST_DIR, "rotten.jpg"), img_rotten)
    images["rotten"] = os.path.join(TEST_DIR, "rotten.jpg")
    
    # Unknown (White)
    img_white = np.ones((224, 224, 3), dtype=np.uint8) * 255
    cv2.imwrite(os.path.join(TEST_DIR, "white.jpg"), img_white)
    images["white"] = os.path.join(TEST_DIR, "white.jpg")
    
    # Banana (Yellow)
    img_banana = np.zeros((224, 224, 3), dtype=np.uint8)
    cv2.ellipse(img_banana, (112, 112), (80, 20), 45, 0, 360, (0, 255, 255), -1)
    cv2.imwrite(os.path.join(TEST_DIR, "banana.jpg"), img_banana)
    images["banana"] = os.path.join(TEST_DIR, "banana.jpg")
    
    # Noise (Random)
    img_noise = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    cv2.imwrite(os.path.join(TEST_DIR, "noise.jpg"), img_noise)
    images["noise"] = os.path.join(TEST_DIR, "noise.jpg")
    
    return images

# Globals for metrics
def get_server_process():
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        if p.info['cmdline'] and 'app.py' in p.info['cmdline'] and 'python' in p.info['name'].lower():
            return p
    return None

server_process = get_server_process()

results_lock = threading.Lock()
test_results = {
    'total': 0,
    'success': 0,
    'fail': 0,
    'times': [],
    'ids': [],
    'unknown_handled': 0
}

def send_prediction(img_path, img_type):
    start = time.time()
    try:
        with open(img_path, 'rb') as f:
            files = {'image': f}
            res = requests.post(API_PREDICT, files=files, timeout=10)
            
        if res.status_code == 200:
            data = res.json()
            latency = (time.time() - start) * 1000
            
            with results_lock:
                test_results['total'] += 1
                test_results['success'] += 1
                test_results['times'].append(latency)
                test_results['ids'].append(data.get('inspection_id'))
                
                # Check unknown handling
                if img_type in ['white', 'banana', 'noise']:
                    # We expect the AI to either fail or have low confidence
                    if data.get('status') == 'REVIEW' or data.get('status') == 'REVIEW REQUIRED' or data.get('confidence_level') == 'Low':
                        test_results['unknown_handled'] += 1
                
            return True, data
        else:
            with results_lock:
                test_results['total'] += 1
                test_results['fail'] += 1
            return False, f"HTTP {res.status_code}"
    except Exception as e:
        with results_lock:
            test_results['total'] += 1
            test_results['fail'] += 1
        return False, str(e)

def validate_gradcam(data):
    if not data: return False
    try:
        # data contains image_url and heatmap_url like /inspection_history/2026/07/name.jpg
        # Convert to local paths assuming we are in the root directory
        img_url = data.get('image_url')
        hm_url = data.get('heatmap_url')
        
        if not img_url or not hm_url:
            return False
            
        # Extract path relative to app/inspection_history
        img_path = "app/" + img_url.lstrip('/')
        hm_path = "app/" + hm_url.lstrip('/')
        
        if not os.path.exists(img_path) or not os.path.exists(hm_path):
            return False
            
        orig_img = cv2.imread(img_path)
        hm_img = cv2.imread(hm_path)
        
        if orig_img is None or hm_img is None:
            return False
            
        if orig_img.shape != hm_img.shape:
            return False
            
        return True
    except:
        return False

def run_concurrency_test(images, workers, count):
    print(f"\n[*] Running concurrency test: {workers} workers, {count} total requests")
    
    img_list = list(images.items())
    tasks = []
    
    # Distribute load
    for i in range(count):
        img_type, img_path = img_list[i % len(img_list)]
        tasks.append((img_path, img_type))
        
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(send_prediction, p, t) for p, t in tasks]
        
    # Wait for all
    successful_data = []
    for f in futures:
        success, data = f.result()
        if success:
            successful_data.append(data)
            
    total_time = time.time() - start_time
    print(f"  - Completed in {total_time:.2f}s ({(count/total_time):.2f} req/s)")
    
    # Validate a sample of Grad-CAMs
    if successful_data:
        valid_cam = validate_gradcam(successful_data[0])
        print(f"  - Grad-CAM Validation on sample: {'PASS' if valid_cam else 'FAIL'}")

def validate_reports():
    print("\n[*] Validating Report Generation...")
    
    # CSV
    try:
        res = requests.get(f"{API_REPORTS}?format=csv")
        csv_valid = res.status_code == 200 and 'timestamp' in res.text.lower() and len(res.text) > 50
        print(f"  - CSV: {'PASS' if csv_valid else 'FAIL'}")
    except Exception as e: print(f"  - CSV: FAIL ({e})")
    
    # JSON
    try:
        res = requests.get(f"{API_REPORTS}?format=json")
        json_valid = res.status_code == 200
        if json_valid:
            try: json.loads(res.text)
            except: json_valid = False
        print(f"  - JSON: {'PASS' if json_valid else 'FAIL'}")
    except Exception as e: print(f"  - JSON: FAIL ({e})")
    
    # PDF
    try:
        res = requests.get(f"{API_REPORTS}?format=pdf")
        pdf_valid = res.status_code == 200 and res.content.startswith(b'%PDF')
        print(f"  - PDF: {'PASS' if pdf_valid else 'FAIL'}")
    except Exception as e: print(f"  - PDF: FAIL ({e})")
    
    # Excel
    try:
        res = requests.get(f"{API_REPORTS}?format=excel")
        # Excel zip files start with PK (50 4B)
        excel_valid = res.status_code == 200 and res.content.startswith(b'PK')
        print(f"  - Excel: {'PASS' if excel_valid else 'FAIL'}")
    except Exception as e: print(f"  - Excel: FAIL ({e})")

def main():
    images = generate_images()
    
    mem_initial = server_process.memory_info().rss / (1024*1024) if server_process else psutil.virtual_memory().used / (1024*1024)
    cpu_peak = 0
    mem_peak = mem_initial
    
    def monitor_resources():
        nonlocal cpu_peak, mem_peak
        while not stop_monitor:
            cpu = server_process.cpu_percent(interval=0.1) if server_process else psutil.cpu_percent(interval=0.1)
            mem = server_process.memory_info().rss / (1024*1024) if server_process else psutil.virtual_memory().used / (1024*1024)
            if cpu > cpu_peak: cpu_peak = cpu
            if mem > mem_peak: mem_peak = mem
            time.sleep(0.5)
            
    global stop_monitor
    stop_monitor = False
    monitor_thread = threading.Thread(target=monitor_resources)
    monitor_thread.start()
    
    global_start = time.time()
    
    try:
        # Phase 1: Sequential Warmup
        run_concurrency_test(images, 1, 10)
        
        # Phase 2: Concurrent Load (5 workers)
        run_concurrency_test(images, 5, 50)
        
        # Phase 3: Concurrent Stress (10 workers)
        run_concurrency_test(images, 10, 100)
        
        # Phase 4: Extreme Concurrent Spike (20 workers)
        run_concurrency_test(images, 20, 200)
        
        # Phase 5: Reports Validation
        validate_reports()
        
    finally:
        stop_monitor = True
        monitor_thread.join()
        
    global_time = time.time() - global_start
    mem_final = server_process.memory_info().rss / (1024*1024) if server_process else psutil.virtual_memory().used / (1024*1024)
    
    # ID Validation
    ids = test_results['ids']
    unique_ids = set([i for i in ids if i is not None])
    id_duplicates = len(ids) - len(unique_ids)
    
    # Generate Report
    report = f"""# SmartCam AI - Performance & Stress Test Report

## 1. Concurrency & Load Metrics
- **Total Requests Sent**: {test_results['total']}
- **Successful Predictions**: {test_results['success']}
- **Failed Predictions**: {test_results['fail']}
- **Total Runtime**: {global_time:.2f} seconds
- **Throughput**: {(test_results['total']/global_time):.2f} images/sec

## 2. Telemetry & Hardware
- **Initial RAM**: {mem_initial:.2f} MB
- **Peak RAM**: {mem_peak:.2f} MB
- **Final RAM**: {mem_final:.2f} MB
- **Memory Leak Detected**: {'YES' if mem_final > mem_initial + 50 else 'NO'} (Threshold 50MB)
- **Peak CPU Usage**: {cpu_peak:.1f}%

## 3. Latency (End-to-End API)
- **Average Inference Time**: {np.mean(test_results['times']):.2f} ms
- **Median Inference Time**: {np.median(test_results['times']):.2f} ms
- **Max Inference Time**: {np.max(test_results['times']):.2f} ms

## 4. Validation Checks
- **Inspection ID Uniqueness**: {'PASS' if id_duplicates == 0 else f'FAIL ({id_duplicates} duplicates)'}
- **Unknown/Edge-Case Images Handled Gracefully**: {test_results['unknown_handled']} detected
"""

    print("\n" + "="*50)
    print("TEST COMPLETE. GENERATING REPORT...")
    print("="*50)
    print(report)
    
    with open("PERFORMANCE_REPORT.md", "w") as f:
        f.write(report)
        
    print("[*] Saved to PERFORMANCE_REPORT.md")

if __name__ == "__main__":
    main()
