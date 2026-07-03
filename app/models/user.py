from flask_login import UserMixin
from app.services.database import DatabaseService

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = str(id)
        self.username = username
        self.role = role

    @staticmethod
    def get(user_id):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(id=row['id'], username=row['username'], role=row['role'])
        return None

    @staticmethod
    def find_by_username(username):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = User(id=row['id'], username=row['username'], role=row['role'])
            user.password_hash = row['password_hash']
            return user
        return None
