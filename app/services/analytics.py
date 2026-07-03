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

    @staticmethod
    def get_timeseries_data():
        """Fetches data for Chart.js dashboards."""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        # Quality Distribution (Today)
        cursor.execute("SELECT status, COUNT(*) FROM predictions WHERE date(timestamp) = date('now', 'localtime') GROUP BY status")
        quality_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Hourly Volume (Today)
        # SQLite substr for hour: substr(timestamp, 12, 2)
        cursor.execute("SELECT substr(timestamp, 12, 2) as hr, COUNT(*) FROM predictions WHERE date(timestamp) = date('now', 'localtime') GROUP BY hr")
        hourly_data = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Weekly Trend (Last 7 days)
        cursor.execute("SELECT date(timestamp) as dt, COUNT(*) FROM predictions WHERE date(timestamp) >= date('now', '-7 days', 'localtime') GROUP BY dt ORDER BY dt ASC")
        weekly_trend = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "quality": quality_dist,
            "hourly": hourly_data,
            "weekly": weekly_trend
        }
