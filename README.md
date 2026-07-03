<div align="center">
  <img src="./app/static/images/avatar.png" alt="SmartCam AI Logo" width="200"/>
  <h1>SmartCam AI</h1>
  <p><strong>Industrial Quality Control System Powered by Deep Learning</strong></p>

  <p>
    <a href="https://github.com/your-username/smartcam-ai"><img src="https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge" alt="Status"></a>
    <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python"></a>
    <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask" alt="Flask"></a>
    <a href="https://tensorflow.org"><img src="https://img.shields.io/badge/TensorFlow-2.x-orange?style=for-the-badge&logo=tensorflow" alt="TensorFlow"></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License"></a>
  </p>
</div>

<br/>

## 📖 Overview

SmartCam AI is an enterprise-grade, real-time computer vision system tailored for **industrial quality control**. Designed for deployment on factory floors, it provides live camera feeds, WebSocket-powered telemetry, AI-driven anomaly detection (using EfficientNetV2B0), and highly visual Grad-CAM explanations for its predictions. 

Whether you are identifying defective machinery parts or sorting agricultural produce, SmartCam AI provides a robust, scalable, and fully audited interface to monitor production quality.

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [📸 Screenshots](#-screenshots)
- [🏗️ System Architecture](#️-system-architecture)
- [🗂️ Folder Structure](#️-folder-structure)
- [💻 Technology Stack](#-technology-stack)
- [🧠 AI Pipeline & Prediction](#-ai-pipeline--prediction)
- [🚀 Installation & Deployment](#-installation--deployment)
- [📊 Performance & Benchmarks](#-performance--benchmarks)
- [🔒 Security & Authentication](#-security--authentication)
- [📚 Supplementary Documentation](#-supplementary-documentation)

---

## ✨ Features

- **Real-Time Live Monitoring**: WebSocket (Socket.IO) powered MJPEG camera streaming and live telemetry updates.
- **Deep Learning Inference**: TensorFlow 2.x backend providing sub-second predictions.
- **Grad-CAM Explanations**: Visual heatmaps explaining exactly *why* the AI made its decision.
- **Out-of-Distribution Handling**: Gracefully catches "Unknown" classes (e.g. random objects on the belt) and flags them for manual review based on a strict 65% confidence threshold.
- **Executive Dashboard**: Beautiful Chart.js analytics for volume, pass rates, and hourly throughput.
- **Role-Based Access Control**: Flask-Login secured endpoints for `Admin` and `Operator` roles.
- **Batch Processing & History**: SQLite backed persistent history with pagination.
- **Automated Reporting**: Export predictions to CSV/JSON for ERP integration.

---

## 📸 Screenshots

| Executive Dashboard | Live Monitoring |
|---------------------|-----------------|
| <img src="./docs/screenshots/02-dashboard.png" alt="Executive Dashboard"> | <img src="./docs/screenshots/03-live-monitoring.png" alt="Live Monitoring"> |

| Grad-CAM Inspection | Dark Mode Dashboard |
|---------------------|---------------------|
| <img src="./docs/screenshots/04-inspection.png" alt="Grad-CAM Inspection"> | <img src="./docs/screenshots/14-dark-mode.png" alt="Dark Mode Dashboard"> |

<details>
<summary>Click to view more screenshots...</summary>

- [Login Page](./docs/screenshots/01-login.png)
- [Mobile Login](./docs/screenshots/16-mobile-view.png)
- [Analytics Charts](./docs/screenshots/07-analytics.png)
- [Inspection History](./docs/screenshots/08-history.png)
- [Dataset Repository](./docs/screenshots/10-dataset.png)
- [Model Management](./docs/screenshots/11-model-manager.png)
</details>

---

## 🏗️ System Architecture

SmartCam AI utilizes a robust Model-View-Controller (MVC) architecture powered by Flask Blueprints and Socket.IO.

```mermaid
graph TD
    User((Industrial Operator)) -->|HTTPS| WebBrowser[Dashboard UI]
    WebBrowser -->|WSS| WebSocket[Flask-SocketIO]
    WebBrowser -->|HTTPS| FlaskAPI[Flask Routes]
    
    FlaskAPI --> Security[Flask-Login / Limiter]
    Security --> TFEngine[TensorFlow Inference]
    WebSocket --> OpenCV[Camera Service]
    
    TFEngine --> GradCAM[Heatmap Generator]
    TFEngine --> DB[(SQLite /inspection_history)]
```
> *For more detailed diagrams including Authentication Flows and DB Schemas, see [PROJECT_ARCHITECTURE.md](docs/PROJECT_ARCHITECTURE.md).*

---

## 🗂️ Folder Structure

```text
📦 smartcam-ai
 ┣ 📂 app
 ┃ ┣ 📂 routes         # Flask Blueprints (api.py, auth.py, dashboard.py)
 ┃ ┣ 📂 services       # Core Business Logic (predictor.py, camera.py)
 ┃ ┣ 📂 static         # CSS (Tailwind), JS, and Images
 ┃ ┗ 📂 templates      # Jinja2 HTML Templates
 ┣ 📂 database         # smartcam.db SQLite store
 ┣ 📂 dataset          # Training images
 ┣ 📂 inspection_history # Processed Grad-CAM images
 ┣ 📂 logs             # App and Error Logs
 ┣ 📂 models           # .keras saved models
 ┣ 📜 app.py           # Main WSGI Entry Point
 ┗ 📜 requirements.txt # Python Dependencies
```

---

## 💻 Technology Stack

- **Backend**: Python 3.10+, Flask, Flask-SocketIO, Werkzeug
- **Frontend**: HTML5, Vanilla JavaScript, Chart.js, TailwindCSS (via CDN)
- **Database**: SQLite3
- **AI / Vision**: TensorFlow 2.x, Keras, OpenCV (cv2)
- **Security**: Flask-Login, Flask-Limiter, Flask-Talisman (CSP)

---

## 🧠 AI Pipeline & Prediction

SmartCam AI utilizes Transfer Learning on an **EfficientNetV2B0** backbone. 
When a frame is captured from the camera or uploaded manually:
1. **Preprocessing**: The image is resized to `224x224` and normalized.
2. **Inference**: The model returns a Softmax probability distribution.
3. **Thresholding**: If the highest probability is below **65%**, the system rejects the prediction and flags it for `REVIEW REQUIRED`. This prevents misclassification of foreign objects on the conveyor belt.
4. **Grad-CAM**: A gradient-weighted class activation map is generated from the final convolutional layer, highlighting the exact pixels that drove the model's decision.

> *For full training metrics and optimizer configurations, see [AI_MODEL_DOCUMENTATION.md](docs/AI_MODEL_DOCUMENTATION.md).*

---

## 🚀 Installation & Deployment

### Local Development (Windows / Linux)
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/smartcam-ai.git
   cd smartcam-ai
   ```
2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**
   ```bash
   python app.py
   ```
5. Navigate to `http://localhost:5000` and login with `admin` / `password`.

### Docker Deployment (Production)
```bash
docker-compose up --build -d
```
*Note: In production, ensure you bind `Flask` to a WSGI server like `gunicorn` or `waitress`.*

---

## 📊 Performance & Benchmarks

During rigorous QA and stress testing with 20 concurrent worker threads:

- **Hardware**: NVIDIA GeForce RTX 3050 Laptop GPU / 16 GB RAM
- **Average Inference Time**: ~3.6s (under peak concurrency load)
- **Throughput**: ~1.6 predictions / second 
- **Peak RAM Usage**: 273.52 MB (No memory leaks detected over 360 continuous predictions)
- **Peak CPU Usage**: 0% (Fully offloaded to CUDA)

> [!CAUTION]
> **TensorFlow High Concurrency Limitation**: Load tests with 20+ concurrent workers trigger an `OOM (Out Of Memory)` crash in TensorFlow due to the 1.6GB VRAM limit on the RTX 3050. To deploy in a heavy industrial setting, you should introduce an inference request queue (e.g. Celery/Redis) or deploy on hardware with higher VRAM capacity (e.g. RTX 4090).

---

## 🔒 Security & Authentication

- **Passwords**: Hashed securely using PBKDF2 (`werkzeug.security`).
- **Rate Limiting**: `Flask-Limiter` enforces a strict 50 requests/hour limit on API endpoints to prevent DDoS.
- **Content Security Policy**: `Flask-Talisman` enforces strict CSP headers, preventing XSS attacks while allowing local `data:` URI images for the dashboard.

---

## 📚 Supplementary Documentation

This repository also includes detailed technical documentation generated during development.

- **[API_REFERENCE.md](docs/API_REFERENCE.md)** — Complete REST API documentation including endpoints, request/response examples, authentication, and status codes.
- **[DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)** — SQLite schema, ER diagrams, relationships, indexes, and database architecture.
- **[PROJECT_ARCHITECTURE.md](docs/PROJECT_ARCHITECTURE.md)** — Complete software architecture, Mermaid diagrams, request lifecycle, AI pipeline, Flask architecture, and deployment flow.
- **[AI_MODEL_DOCUMENTATION.md](docs/AI_MODEL_DOCUMENTATION.md)** — Dataset preparation, EfficientNetV2B0 training pipeline, transfer learning strategy, Grad-CAM implementation, threshold logic, and evaluation metrics.
- **[QA_REPORT.md](docs/QA_REPORT.md)** — Functional testing results, stress testing, UI validation, API verification, and performance benchmarking.
- **[BUG_LIST.md](docs/BUG_LIST.md)** — Known issues, pending improvements, technical debt, feature requests, and future enhancements.
- **[PERFORMANCE_REPORT.md](docs/PERFORMANCE_REPORT.md)** — CPU usage, RAM usage, inference time, throughput, benchmark results, and hardware configuration.
- **[TEST_RESULTS.md](docs/TEST_RESULTS.md)** — End-to-end testing logs, integration testing, validation images, confusion matrix, and production verification.
- **[CHANGELOG.md](docs/CHANGELOG.md)** — Version history and implemented features.
- **[ROADMAP.md](docs/ROADMAP.md)** — Planned future improvements and upcoming milestones.

---

## 👨‍💻 Project Credits

**Project Title:**
SmartCam AI – Industrial Quality Control System

**Developer:**
Jiphin George

**Course:**
Master of Computer Applications (MCA)

**Internship:**
AI & Machine Learning Internship

**Organization:**
Nestsoft Technomaster

**Technology Stack:**
- Python
- Flask
- TensorFlow
- Keras
- EfficientNetV2B0
- OpenCV
- SQLite
- JavaScript
- TailwindCSS
- Chart.js
- Socket.IO

---

## 🙏 Acknowledgements

This project was developed as the capstone internship project for an AI & Machine Learning Industrial Quality Control System.

Special thanks to:
- Nestsoft Technomaster for internship guidance and project mentorship.
- Google Teachable Machine for rapid prototyping during the initial development phase.
- TensorFlow & Keras teams for the deep learning framework.
- Flask and the open-source Python community.
- Google Stitch for the UI inspiration and interface design.
- Open-source dataset contributors for providing tomato image datasets used for model training.
- The creators and maintainers of EfficientNet for transfer learning research.

---

## 📄 License

This project is licensed under the MIT License.

See the LICENSE file for complete details.
