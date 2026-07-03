import os

class Config:
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smartcam-industrial-secret-key')
    
    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(os.path.dirname(BASE_DIR), 'database', 'smartcam.db')
    MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), 'models', 'best_model.keras')
    TRAINING_SUMMARY_PATH = os.path.join(os.path.dirname(BASE_DIR), 'models', 'training_summary.json')
    INSPECTION_HISTORY_DIR = os.path.join(BASE_DIR, 'inspection_history')
    LOGS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'logs')
    
    # Camera Settings
    CAMERA_INDEX = 0
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    
    # AI Prediction
    THRESHOLD = 0.5
    INPUT_SIZE = (224, 224)
    CLASSES = ["Fresh", "Rotten"]
    
    # UI Theme
    THEME = 'dark'

    @classmethod
    def setup_directories(cls):
        os.makedirs(os.path.dirname(cls.DB_PATH), exist_ok=True)
        os.makedirs(cls.INSPECTION_HISTORY_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
