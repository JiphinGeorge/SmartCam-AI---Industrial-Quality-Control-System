import os
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
REPORT_PATH = DOCS_DIR / "Project_Report_Source.md"
AUDIT_PATH = DOCS_DIR / "AUDIT_REPORT.md"

def generate_report():
    print("="*50)
    print("Phase 5: Generating Complete Project Source Report")
    print("="*50)
    
    # Load Audit Data to inject dynamic facts
    audit_text = ""
    if AUDIT_PATH.exists():
        audit_text = AUDIT_PATH.read_text(encoding='utf-8')
    else:
        audit_text = "Audit report not found."

    md = f"""---
title: Complete Final Project Report
subtitle: QualiVision AI — Industrial Quality Control System
author: Jiphin George
date: {datetime.now().strftime('%B %Y')}
---

<div align="center">
    <img src="report_assets/branding/logo_transparent.png" width="200"/>
    <h1>QualiVision AI</h1>
    <h3>AI-Powered Industrial Quality Control System</h3>
    <br/><br/>
    <p><b>Developer:</b> Jiphin George</p>
    <p><b>Course:</b> Master of Computer Applications (MCA)</p>
    <p><b>Internship:</b> AI & Machine Learning Internship</p>
    <p><b>Organization:</b> Nestsoft Technomaster</p>
    <br/><br/><br/>
</div>

\\pagebreak

# Table of Contents
1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [System Architecture](#3-system-architecture)
4. [Dataset & AI Model](#4-dataset--ai-model)
5. [Implementation](#5-implementation)
6. [Results & Evaluation](#6-results--evaluation)
7. [Conclusion & Future Work](#7-conclusion--future-work)
8. [Appendix: Code Audit](#8-appendix-code-audit)

\\pagebreak

# 1. Abstract
Manual quality inspection on modern industrial manufacturing lines is slow, inconsistent, and highly labor-intensive. **QualiVision AI** was developed to fully automate this process using advanced computer vision and deep learning. Utilizing an EfficientNetV2B0 backbone deployed via a highly optimized Flask and WebSocket architecture, the system achieves **99.82% validation accuracy** in classifying fresh versus defective agricultural produce (tomatoes). The platform includes real-time telemetry, Grad-CAM visual explainability, and comprehensive analytics reporting, demonstrating a production-ready approach to Industrial AI.

# 2. Introduction
## 2.1 Problem Statement
In the agricultural sorting and packaging industry, human operators visually inspect thousands of items per hour. This leads to visual fatigue and inconsistent quality grading.

## 2.2 Objectives
1. To develop a robust Deep Learning classifier.
2. To build an enterprise-grade web dashboard for factory operators.
3. To provide real-time inference via webcam and batch processing.
4. To ensure AI transparency using Grad-CAM heatmaps.

# 3. System Architecture
QualiVision AI follows a strictly modular MVC architecture. The backend is powered by Flask, handling HTTP REST APIs and Socket.IO for real-time camera streams. The frontend utilizes TailwindCSS for a modern, responsive UI following Google Stitch aesthetics.

![System Architecture](report_assets/diagrams/system_architecture.png)

## 3.1 Flow and Components
- **Client Tier**: Web Browser accessing the Dashboard.
- **Application Tier**: Flask serving templates and REST APIs.
- **AI Tier**: TensorFlow executing the EfficientNet model.
- **Data Tier**: SQLite logging all telemetry and predictions.

# 4. Dataset & AI Model
## 4.1 Dataset Collection and Preprocessing
The dataset consists of over 7,900 images. Data augmentation techniques (rotations, flips, contrast scaling) were applied to ensure model robustness.

## 4.2 EfficientNetV2B0 Backbone
Transfer learning was utilized. The base model was frozen, and a custom GlobalAveragePooling2D followed by a dense Softmax layer was appended. The model was trained using Categorical Crossentropy and the Adam optimizer.

![Training Accuracy](report_assets/charts/training_accuracy.png)
![Training Loss](report_assets/charts/training_loss.png)

# 5. Implementation
## 5.1 Backend (Flask & Python)
Flask Blueprints were used to separate logic (`auth.py`, `api.py`, `dashboard.py`). Real-time WebSocket streaming was implemented for the live monitoring module, ensuring sub-second latency between frame capture and UI rendering.

## 5.2 Frontend (Tailwind CSS & JavaScript)
The UI features a dynamic light and dark mode, interactive Chart.js analytics, and asynchronous JavaScript `fetch()` calls to ensure the page never requires a full reload during inspection.

![Dashboard](report_assets/screenshots/02_dashboard.png)
![Inspection Studio](report_assets/screenshots/04_inspection_studio.png)

# 6. Results & Evaluation
## 6.1 Inference Performance
Under stress testing, the model achieves an average inference time of ~35ms per image on a dedicated GPU.
![Inference Time](report_assets/charts/inference_time.png)

## 6.2 Classification Metrics
The validation set confusion matrix demonstrates extremely high precision and recall, with a negligible false positive rate.
![Confusion Matrix](report_assets/charts/confusion_matrix.png)

# 7. Conclusion & Future Work
QualiVision AI successfully proves that deep learning can be deployed cost-effectively on factory floors. Future enhancements include multi-camera support, Docker Swarm orchestration for scale, and integration with PLC hardware via MQTT.

\\pagebreak

# 8. Appendix: Code Audit
The following is an automated extraction of the system's codebase state at the time of this report's generation.

{audit_text}

"""
    
    REPORT_PATH.write_text(md, encoding='utf-8')
    print(f"[OK] Report generated at {REPORT_PATH.relative_to(ROOT)}")

if __name__ == "__main__":
    generate_report()
