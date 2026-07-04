import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs" / "manuals"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

MANUALS = {
    "User_Manual.md": "# QualiVision AI User Manual\n\n## 1. Getting Started\nNavigate to the dashboard...\n\n## 2. Live Monitoring\nUse the live stream to watch inferences in real-time.\n",
    "Administrator_Guide.md": "# Administrator Guide\n\n## 1. User Management\nAdd and remove users.\n\n## 2. Model Uploads\nHow to swap the `.keras` files.\n",
    "Developer_Guide.md": "# Developer Guide\n\n## 1. Setup\n`pip install -r requirements.txt`\n\n## 2. Architecture\nSee `Project_Report_Source.md`.\n",
    "Deployment_Guide.md": "# Deployment Guide\n\n## 1. Docker\nRun `docker-compose up -d`.\n\n## 2. Nginx & Gunicorn\nConfigure reverse proxy.\n",
}

def main():
    print("="*50)
    print("Phase 7: Generating User Documentation")
    print("="*50)
    
    for filename, content in MANUALS.items():
        path = DOCS_DIR / filename
        path.write_text(content, encoding='utf-8')
        print(f"[OK] Generated {filename}")

if __name__ == "__main__":
    main()
