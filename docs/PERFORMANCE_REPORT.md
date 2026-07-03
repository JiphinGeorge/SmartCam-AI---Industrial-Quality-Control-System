# SmartCam AI - Performance & Stress Test Report

## 1. Concurrency & Load Metrics
- **Total Requests Sent**: 360
- **Successful Predictions**: 159
- **Failed Predictions**: 201
- **Total Runtime**: 229.69 seconds
- **Throughput**: 1.57 images/sec

## 2. Telemetry & Hardware
- **Initial RAM**: 273.52 MB
- **Peak RAM**: 273.52 MB
- **Final RAM**: 273.48 MB
- **Memory Leak Detected**: NO (Threshold 50MB)
- **Peak CPU Usage**: 0.0%

## 3. Latency (End-to-End API)
- **Average Inference Time**: 3690.07 ms
- **Median Inference Time**: 3861.60 ms
- **Max Inference Time**: 4865.30 ms

## 4. Validation Checks
- **Inspection ID Uniqueness**: PASS
- **Unknown/Edge-Case Images Handled Gracefully**: 33 detected
