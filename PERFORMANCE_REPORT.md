# SmartCam AI - Performance & Stress Test Report

## 1. Concurrency & Load Metrics
- **Total Requests Sent**: 360
- **Successful Predictions**: 49
- **Failed Predictions**: 311
- **Total Runtime**: 120.24 seconds
- **Throughput**: 2.99 images/sec

## 2. Telemetry & Hardware
- **Initial RAM**: 273.48 MB
- **Peak RAM**: 273.48 MB
- **Final RAM**: 273.48 MB
- **Memory Leak Detected**: NO (Threshold 50MB)
- **Peak CPU Usage**: 0.0%

## 3. Latency (End-to-End API)
- **Average Inference Time**: 2853.33 ms
- **Median Inference Time**: 2760.80 ms
- **Max Inference Time**: 7733.66 ms

## 4. Validation Checks
- **Inspection ID Uniqueness**: FAIL ({id_duplicates} duplicates)
- **Unknown/Edge-Case Images Handled Gracefully**: 11 detected
