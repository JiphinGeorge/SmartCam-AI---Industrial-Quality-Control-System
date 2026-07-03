from app.services.database import DatabaseService

class AnalyticsService:
    @staticmethod
    def get_dashboard_stats():
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        # Today's Inspections
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE date(timestamp) = date('now', 'localtime')")
        total_today = cursor.fetchone()[0]
        
        # Fresh Count
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE date(timestamp) = date('now', 'localtime') AND status = 'PASS'")
        fresh_count = cursor.fetchone()[0]
        
        # Rotten Count
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE date(timestamp) = date('now', 'localtime') AND status = 'FAIL'")
        rotten_count = cursor.fetchone()[0]
        
        # Average Confidence
        cursor.execute("SELECT AVG(confidence) FROM predictions WHERE date(timestamp) = date('now', 'localtime')")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # Average Inference Time
        cursor.execute("SELECT AVG(inference_time_ms) FROM predictions WHERE date(timestamp) = date('now', 'localtime')")
        avg_time = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_today": total_today,
            "fresh_count": fresh_count,
            "rotten_count": rotten_count,
            "avg_confidence": round(avg_confidence, 1),
            "avg_inference_time": round(avg_time, 1)
        }
