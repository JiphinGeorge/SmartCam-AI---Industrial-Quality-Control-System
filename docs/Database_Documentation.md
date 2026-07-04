# QualiVision AI — Database Documentation

## Table: `predictions`

**Schema:**
```sql
CREATE TABLE predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                filename TEXT,
                prediction TEXT,
                confidence REAL,
                status TEXT,
                inference_time_ms REAL,
                image_path TEXT,
                camera_source TEXT
            , inspection_id TEXT, operator TEXT DEFAULT 'System', location TEXT DEFAULT 'Main Line', shift TEXT DEFAULT 'Day', notes TEXT, batch_id TEXT, machine_id TEXT DEFAULT 'CAM-01', model_version TEXT DEFAULT 'v2.1', gradcam_path TEXT)
```

| CID | Name | Type | NotNull | Default | PK |
|---|---|---|---|---|---|
| 0 | `id` | `INTEGER` | 0 | None | 1 |
| 1 | `timestamp` | `DATETIME` | 0 | CURRENT_TIMESTAMP | 0 |
| 2 | `filename` | `TEXT` | 0 | None | 0 |
| 3 | `prediction` | `TEXT` | 0 | None | 0 |
| 4 | `confidence` | `REAL` | 0 | None | 0 |
| 5 | `status` | `TEXT` | 0 | None | 0 |
| 6 | `inference_time_ms` | `REAL` | 0 | None | 0 |
| 7 | `image_path` | `TEXT` | 0 | None | 0 |
| 8 | `camera_source` | `TEXT` | 0 | None | 0 |
| 9 | `inspection_id` | `TEXT` | 0 | None | 0 |
| 10 | `operator` | `TEXT` | 0 | 'System' | 0 |
| 11 | `location` | `TEXT` | 0 | 'Main Line' | 0 |
| 12 | `shift` | `TEXT` | 0 | 'Day' | 0 |
| 13 | `notes` | `TEXT` | 0 | None | 0 |
| 14 | `batch_id` | `TEXT` | 0 | None | 0 |
| 15 | `machine_id` | `TEXT` | 0 | 'CAM-01' | 0 |
| 16 | `model_version` | `TEXT` | 0 | 'v2.1' | 0 |
| 17 | `gradcam_path` | `TEXT` | 0 | None | 0 |

---

## Table: `settings`

**Schema:**
```sql
CREATE TABLE settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
```

| CID | Name | Type | NotNull | Default | PK |
|---|---|---|---|---|---|
| 0 | `key` | `TEXT` | 0 | None | 1 |
| 1 | `value` | `TEXT` | 0 | None | 0 |

---

## Table: `users`

**Schema:**
```sql
CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
```

| CID | Name | Type | NotNull | Default | PK |
|---|---|---|---|---|---|
| 0 | `id` | `INTEGER` | 0 | None | 1 |
| 1 | `username` | `TEXT` | 1 | None | 0 |
| 2 | `password_hash` | `TEXT` | 1 | None | 0 |
| 3 | `role` | `TEXT` | 1 | None | 0 |

---

