# QualiVision AI — Codebase Audit Report

**Audit Date:** 2026-07-04 13:20:35

## 1. File Statistics & LOC

| Extension | File Count | Lines of Code |
|---|---|---|
| `.css` | 1 | 506 |
| `.html` | 35 | 8,791 |
| `.js` | 9 | 930 |
| `.md` | 14 | 990 |
| `.py` | 53 | 4,975 |

## 2. Flask API Routes

| Blueprint | Methods | Path | Function |
|---|---|---|---|
| `analytics` | `GET` | `/analytics` | `index` |
| `api` | `GET` | `/api/analytics` | `get_analytics` |
| `api` | `GET` | `/api/dataset_stats` | `get_dataset_stats` |
| `api` | `GET` | `/api/export` | `export` |
| `api` | `GET` | `/api/history` | `get_history` |
| `api` | `DELETE` | `/api/history/<inspection_id>` | `delete_history` |
| `api` | `GET` | `/api/history/export` | `export_history` |
| `api` | `GET` | `/api/model_stats` | `get_model_stats` |
| `api` | `POST` | `/api/predict` | `predict` |
| `api` | `GET` | `/api/report/pdf` | `export_pdf` |
| `api` | `GET` | `/api/reports/download` | `download_report` |
| `api` | `GET, POST` | `/api/settings` | `handle_settings` |
| `api` | `GET` | `/api/stats` | `get_stats` |
| `api` | `GET` | `/api/system_status` | `system_status` |
| `api` | `GET` | `/health` | `health` |
| `api` | `GET` | `/video_feed` | `video_feed` |
| `auth` | `GET, POST` | `/login` | `login` |
| `auth` | `GET` | `/logout` | `logout` |
| `auth` | `GET` | `/profile` | `profile` |
| `dashboard` | `GET` | `/dashboard` | `index` |
| `dashboard` | `GET` | `/logs` | `logs` |
| `dashboard` | `GET` | `/notifications` | `notifications` |
| `dataset` | `GET` | `/dataset` | `index` |
| `history` | `GET` | `/history` | `index` |
| `inspection` | `GET` | `/inspection` | `index` |
| `knowledge` | `GET` | `/knowledge` | `index` |
| `live` | `GET` | `/live` | `index` |
| `models` | `GET` | `/models` | `index` |
| `reports` | `GET` | `/reports` | `index` |
| `settings` | `GET` | `/settings` | `index` |

## 3. Database Schema

### Table: `predictions`
| Column | Type |
|---|---|
| `id` | `INTEGER` |
| `timestamp` | `DATETIME` |
| `filename` | `TEXT` |
| `prediction` | `TEXT` |
| `confidence` | `REAL` |
| `status` | `TEXT` |
| `inference_time_ms` | `REAL` |
| `image_path` | `TEXT` |
| `camera_source` | `TEXT` |
| `inspection_id` | `TEXT` |
| `operator` | `TEXT` |
| `location` | `TEXT` |
| `shift` | `TEXT` |
| `notes` | `TEXT` |
| `batch_id` | `TEXT` |
| `machine_id` | `TEXT` |
| `model_version` | `TEXT` |
| `gradcam_path` | `TEXT` |

### Table: `settings`
| Column | Type |
|---|---|
| `key` | `TEXT` |
| `value` | `TEXT` |

### Table: `users`
| Column | Type |
|---|---|
| `id` | `INTEGER` |
| `username` | `TEXT` |
| `password_hash` | `TEXT` |
| `role` | `TEXT` |


## 4. Documentation Coverage Assessment

- [x] Codebase audited successfully.
- [ ] API Documentation generated.
- [ ] DB Schema documented.
- [ ] UI Screenshots captured.
