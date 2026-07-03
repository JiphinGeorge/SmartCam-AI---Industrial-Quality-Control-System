# QualiVision AI - High Level Architecture

This document contains detailed architectural diagrams for the QualiVision AI Industrial QC System.

## 1. High Level Architecture

```mermaid
graph TD
    User((Industrial Operator)) -->|HTTPS| WebBrowser[Web Browser]
    WebBrowser -->|HTTPS / WSS| FlaskServer[Flask Web Server]
    
    subgraph QualiVision AI Application Node
        FlaskServer --> APIRouter[API Router / Blueprints]
        FlaskServer --> SocketRouter[WebSocket Event Loop]
        
        APIRouter --> Security[Talisman/Limiter/Flask-Login]
        Security --> Services[Business Logic Services]
        
        Services --> DB[(SQLite Database)]
        Services --> AIEngine[TensorFlow Keras Engine]
        Services --> CameraEngine[OpenCV Camera Stream]
    end
```

## 2. Backend Architecture

```mermaid
graph LR
    subgraph Flask App Structure
        Main[app.py] --> Init[__init__.py Factory]
        Init --> Routes[Blueprints]
        
        subgraph Routes
            API[api.py]
            Auth[auth.py]
            Views[dashboard.py]
            Reports[reports.py]
            Upload[upload.py]
        end
        
        Init --> Services[Services Layer]
        
        subgraph Services Layer
            DBS[database.py]
            AI[predictor.py]
            Cam[camera.py]
            WS[websocket.py]
        end
        
        Routes --> Services
    end
```

## 3. AI Pipeline

```mermaid
graph TD
    Input[Raw Image/Camera Frame] --> Preprocess[OpenCV Preprocessing]
    Preprocess --> Resize[Resize to 224x224]
    Resize --> Normalize[Normalize 0-1]
    Normalize --> Inference[EfficientNetV2B0 Model]
    Inference --> Predictions[Softmax Probabilities]
    
    Predictions --> ConfCheck{Confidence > 65%?}
    ConfCheck -->|Yes| GradCAM[Generate Grad-CAM Heatmap]
    ConfCheck -->|No| Review[Flag for Manual Review]
    
    GradCAM --> Overlay[Overlay Heatmap on Base Image]
    Overlay --> DBStore[Save to /inspection_history]
```

## 4. Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Flask(auth.py)
    participant Database

    User->>Browser: Enters Credentials
    Browser->>Flask(auth.py): POST /login (username, password)
    Flask(auth.py)->>Database: SELECT * FROM users WHERE username=?
    Database-->>Flask(auth.py): User Record + Hashed Password
    Flask(auth.py)->>Flask(auth.py): Verify check_password_hash()
    
    alt Success
        Flask(auth.py)->>Browser: Set Session Cookie
        Browser->>Flask(auth.py): GET /dashboard
        Flask(auth.py)-->>Browser: 200 OK (Render dashboard.html)
    else Failure
        Flask(auth.py)-->>Browser: 401 Unauthorized (Redirect to /login)
    end
```

## 5. Live Monitoring Flow (WebSocket)

```mermaid
sequenceDiagram
    participant Browser (analytics.js)
    participant Flask-SocketIO
    participant OpenCV Thread
    participant TensorFlow Service
    
    Browser (analytics.js)->>Flask-SocketIO: Connect (wss://)
    loop Every 5 Seconds
        OpenCV Thread->>OpenCV Thread: Capture Frame
        OpenCV Thread->>TensorFlow Service: Run Prediction
        TensorFlow Service-->>OpenCV Thread: Return Result
        OpenCV Thread->>Flask-SocketIO: socketio.emit('telemetry_update')
        Flask-SocketIO-->>Browser (analytics.js): JSON Payload
        Browser (analytics.js)->>Browser (analytics.js): Update Chart.js & UI
    end
```
