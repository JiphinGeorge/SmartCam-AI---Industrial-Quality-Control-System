import csv
import io
from flask import make_response
from app.services.database import DatabaseService

class ReportService:
    @staticmethod
    def export_csv():
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, filename, prediction, confidence, status, inference_time_ms, camera_source FROM predictions ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['ID', 'Timestamp', 'Filename', 'Prediction', 'Confidence (%)', 'Status', 'Inference Time (ms)', 'Source'])
        for row in rows:
            cw.writerow(list(row))
            
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=inspections_report.csv"
        output.headers["Content-type"] = "text/csv"
        return output
