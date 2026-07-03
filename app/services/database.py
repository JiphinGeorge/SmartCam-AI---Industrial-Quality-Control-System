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
        """Creates the predictions table if it doesn't exist."""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
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
                camera_source TEXT
            )
        ''')
        # We also need to add inspection_id to existing db if it doesn't exist, but we will handle this via ALTER TABLE manually.
        conn.commit()
        conn.close()

    @staticmethod
    def log_prediction(inspection_id, filename, prediction, confidence, status, inference_time_ms, image_path, camera_source):
        """Logs a new inspection to the database."""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions 
            (inspection_id, timestamp, filename, prediction, confidence, status, inference_time_ms, image_path, camera_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inspection_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), filename, prediction, confidence, status, inference_time_ms, image_path, camera_source))
        conn.commit()
        conn.close()
