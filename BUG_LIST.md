# Bug List & Technical Debt

This document tracks active bugs, missing features, and technical debt discovered during the QA & Audit process.

## HIGH Priority
| Page | Component | Issue | Estimated Fix |
|------|-----------|-------|---------------|
| Prediction Pipeline | TensorFlow Engine | **OOM (Out Of Memory) Crash** during high concurrency (20+ parallel requests). The Flask server dies. | Implement a Celery/Redis Request Queue to serialize GPU inference. |
| Live Monitoring | WebSocket Client | If the server restarts, the WebSocket client does not automatically reconnect gracefully in all browsers. | Add exponential backoff reconnect logic in JS. |

## MEDIUM Priority
| Page | Component | Issue | Estimated Fix |
|------|-----------|-------|---------------|
| Reports | Export API | The `pdf` and `excel` export formats are stubbed out but do not actually generate valid PDF/XLSX binaries yet. | Implement `reportlab` and `openpyxl`. |
| Dataset | Image Uploader | Uploading massive 4K images blocks the main WSGI thread during resize. | Offload image preprocessing to a background thread. |

## LOW Priority
| Page | Component | Issue | Estimated Fix |
|------|-----------|-------|---------------|
| Settings | Database | Theme preference (Light/Dark mode) is saved in LocalStorage, but not synced to the SQLite user profile. | Add an API route to save user preferences. |
| UI | Navbar | The User Profile avatar is hardcoded to `avatar.jpg`. | Add profile picture upload functionality. |
