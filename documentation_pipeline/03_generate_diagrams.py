import os
import base64
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS_DIR = ROOT / "docs" / "report_assets" / "diagrams"
DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Mermaid Source Definitions
# ──────────────────────────────────────────────

DIAGRAMS = {
    "system_architecture": """
graph TD
    User((Industrial Operator)) -->|HTTPS| WebBrowser[Dashboard UI]
    WebBrowser -->|WSS| WebSocket[Flask-SocketIO]
    WebBrowser -->|HTTPS| FlaskAPI[Flask Routes]
    
    FlaskAPI --> Security[Flask-Login / Limiter]
    Security --> TFEngine[TensorFlow Inference]
    WebSocket --> OpenCV[Camera Service]
    
    TFEngine --> GradCAM[Heatmap Generator]
    TFEngine --> DB[(SQLite Database)]
    """,

    "deployment_diagram": """
graph TD
    subgraph Client
        Browser[Web Browser]
        Camera[Live Webcam]
    end
    subgraph Server [Production Server]
        Nginx[Nginx Proxy]
        subgraph Docker [Docker Container]
            Gunicorn[Gunicorn WSGI]
            Flask[Flask App]
            TF[TensorFlow Runtime]
            OpenCV_Svc[OpenCV Video Capture]
        end
        SQLite[(SQLite db)]
    end
    Client -->|HTTPS / WSS| Nginx
    Nginx -->|Reverse Proxy| Gunicorn
    Gunicorn --> Flask
    Flask --> TF
    Flask --> OpenCV_Svc
    Flask --> SQLite
    """,

    "ai_pipeline": """
graph LR
    Input[Image 224x224] --> Preprocess[Normalize & Scale]
    Preprocess --> Backbone[EfficientNetV2B0]
    Backbone --> Pool[Global Average Pooling]
    Pool --> Dense[Dense Layer / Softmax]
    Dense --> Output[Fresh 98% / Rotten 2%]
    Dense -.-> GradCAM[Extract feature maps]
    GradCAM --> Heatmap[Visual Explanation]
    """,
    
    "erd": """
erDiagram
    users {
        int id PK
        string username
        string password_hash
        string role
    }
    predictions {
        int id PK
        datetime timestamp
        string filename
        string prediction
        float confidence
        string status
        float inference_time_ms
        string image_path
        string camera_source
        string inspection_id
    }
    settings {
        string key PK
        string value
    }
    users ||--o{ predictions : "audits"
    """
}

def mmd_to_image(mmd_code, output_path, fmt="img"):
    # Mermaid.ink requires base64 encoded string
    encoded = base64.urlsafe_b64encode(mmd_code.strip().encode('utf-8')).decode('utf-8')
    url = f"https://mermaid.ink/img/{encoded}?bgColor=ffffff"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
            out_file.write(response.read())
        return True
    except Exception as e:
        print(f"Error fetching {output_path.name}: {e}")
        return False

def main():
    print("="*50)
    print("Phase 3: Generating UML & Architecture Diagrams")
    print("="*50)
    
    for name, code in DIAGRAMS.items():
        # Save raw .mmd
        mmd_path = DIAGRAMS_DIR / f"{name}.mmd"
        mmd_path.write_text(code.strip(), encoding='utf-8')
        
        # Render PNG via Mermaid Ink
        png_path = DIAGRAMS_DIR / f"{name}.png"
        success = mmd_to_image(code, png_path, fmt="img")
        if success:
            print(f"[OK] Generated {name}.png")
        else:
            print(f"[FAIL] Could not generate {name}.png via API")

    print(f"\nAll diagrams saved to {DIAGRAMS_DIR.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
