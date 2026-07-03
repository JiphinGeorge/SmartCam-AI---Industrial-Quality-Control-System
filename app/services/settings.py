from app.services.database import DatabaseService

class SettingsService:
    @staticmethod
    def get_all():
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        conn.close()
        
        settings = {}
        for row in rows:
            settings[row[0]] = row[1]
        return settings

    @staticmethod
    def update(settings_dict):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        for k, v in settings_dict.items():
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
            
        conn.commit()
        conn.close()
        return True
