# API Reference

This document outlines the exposed HTTP endpoints in the SmartCam AI application. 
All endpoints are protected by `Flask-Login` and `Flask-Limiter` unless otherwise noted.

## Overview

- **Base URL**: `/api/v1/`
- **Authentication**: Session Cookies (`session` securely signed by Flask)
- **Rate Limit**: 50 req/hour for standard APIs. (Configurable in `app/__init__.py`)

---

## 1. Authentication

### `POST /login`
Authenticates a user and creates a secure session.

- **Parameters**
  - `username` (string): The operator's username.
  - `password` (string): The operator's password.
- **Response**: `302 Found` (Redirects to `/dashboard` on success)

### `GET /logout`
Terminates the current session.

- **Response**: `302 Found` (Redirects to `/login`)

---

## 2. Prediction & Inference

### `POST /api/predict`
Runs inference on an uploaded image.

- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**
  - `file` (File): The image to predict (JPG, PNG, WebP)
- **Response**:
```json
{
    "success": true,
    "prediction": "Fresh",
    "confidence": 98.45,
    "processing_time_ms": 142,
    "heatmap_url": "/static/inspection_history/QC-123_heatmap.jpg"
}
```

---

## 3. History & Analytics

### `GET /api/history`
Fetches a paginated list of past inspections.

- **Parameters**
  - `page` (int, default=1): The page number.
  - `limit` (int, default=50): Items per page.
  - `filter` (string, optional): Filter by `Fresh` or `Rotten`.
- **Response**:
```json
{
    "total_records": 1052,
    "page": 1,
    "records": [
        {
            "id": "QC-20260703-124500",
            "timestamp": "2026-07-03T12:45:00Z",
            "result": "Fresh",
            "confidence": 99.1
        }
    ]
}
```

### `GET /api/reports/download`
Generates an export of the inspection history.

- **Parameters**
  - `format` (string): `csv`, `pdf`, `json`, or `excel`.
- **Response**: File download stream.

---

## 4. WebSockets

- **Namespace**: `/`
- **Event**: `telemetry_update`
- **Payload**:
```json
{
    "timestamp": "2026-07-03T14:32:00Z",
    "cpu_usage": 45.2,
    "memory_usage": 240.1,
    "inspections_last_minute": 12,
    "pass_rate": 88.5
}
```
