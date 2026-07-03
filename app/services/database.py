import sqlite3
import os
from datetime import datetime
from app.config import Config

class DatabaseService:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(Config.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def initialize():
        """Creates the predictions table with enterprise schema."""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        # In a production environment, use Alembic/migrations. 
        # For this setup, we'll create the expanded table if it doesn't exist.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspection_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                filename TEXT,
                prediction TEXT,
                confidence REAL,
                status TEXT,
                inference_time_ms REAL,
                image_path TEXT,
                camera_source TEXT,
                operator TEXT DEFAULT 'System',
                location TEXT DEFAULT 'Main Line',
                shift TEXT DEFAULT 'Day',
                notes TEXT,
                batch_id TEXT,
                machine_id TEXT DEFAULT 'CAM-01',
                model_version TEXT DEFAULT 'v2.1',
                gradcam_path TEXT
            )
        ''')
        
        # Apply schema updates to existing table if needed (simple approach for SQLite)
        try:
            cursor.execute("ALTER TABLE predictions ADD COLUMN operator TEXT DEFAULT 'System'")
            cursor.execute("ALTER TABLE predictions ADD COLUMN location TEXT DEFAULT 'Main Line'")
            cursor.execute("ALTER TABLE predictions ADD COLUMN shift TEXT DEFAULT 'Day'")
            cursor.execute("ALTER TABLE predictions ADD COLUMN notes TEXT")
            cursor.execute("ALTER TABLE predictions ADD COLUMN batch_id TEXT")
            cursor.execute("ALTER TABLE predictions ADD COLUMN machine_id TEXT DEFAULT 'CAM-01'")
            cursor.execute("ALTER TABLE predictions ADD COLUMN model_version TEXT DEFAULT 'v2.1'")
            cursor.execute("ALTER TABLE predictions ADD COLUMN gradcam_path TEXT")
        except sqlite3.OperationalError:
            pass # Columns already exist
            
        conn.commit()
        conn.close()

    @staticmethod
    def log_prediction(inspection_id, filename, prediction, confidence, status, inference_time_ms, image_path, camera_source, gradcam_path=None, **kwargs):
        """Logs a new inspection to the database."""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        operator = kwargs.get('operator', 'System')
        location = kwargs.get('location', 'Main Line')
        shift = kwargs.get('shift', 'Day')
        notes = kwargs.get('notes', '')
        batch_id = kwargs.get('batch_id', f"B-{datetime.now().strftime('%Y%m%d')}")
        machine_id = kwargs.get('machine_id', 'CAM-01')
        model_version = kwargs.get('model_version', 'v2.1')
        
        cursor.execute('''
            INSERT INTO predictions 
            (inspection_id, timestamp, filename, prediction, confidence, status, inference_time_ms, image_path, camera_source, operator, location, shift, notes, batch_id, machine_id, model_version, gradcam_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            inspection_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), filename, prediction, confidence, status, 
            inference_time_ms, image_path, camera_source, operator, location, shift, notes, batch_id, machine_id, model_version, gradcam_path
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_history(page=1, limit=50, status=None, sort_by='timestamp DESC'):
        """Fetches paginated and filtered inspection history."""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM predictions WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
            
        safe_sort = sort_by if sort_by in ['timestamp DESC', 'timestamp ASC', 'confidence DESC', 'confidence ASC'] else 'timestamp DESC'
        
        query += f" ORDER BY {safe_sort} LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        count_query = "SELECT COUNT(*) FROM predictions WHERE 1=1"
        count_params = []
        if status:
            count_query += " AND status = ?"
            count_params.append(status)
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'data': [dict(row) for row in rows],
            'total': total,
            'page': page,
            'pages': max(1, (total + limit - 1) // limit)
        }

