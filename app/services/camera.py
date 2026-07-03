import cv2
import threading
import time
from app.config import Config
from app.services.logger import get_logger

logger = get_logger('system')

class CameraService:
    def __init__(self):
        self.camera = None
        self.lock = threading.Lock()
        self.is_connected = False
        
    def connect(self):
        with self.lock:
            if self.camera is None or not self.camera.isOpened():
                try:
                    self.camera = cv2.VideoCapture(Config.CAMERA_INDEX)
                    if self.camera.isOpened():
                        self.is_connected = True
                        logger.info(f"Connected to camera at index {Config.CAMERA_INDEX}")
                    else:
                        self.is_connected = False
                        logger.warning(f"Failed to connect to camera at index {Config.CAMERA_INDEX}")
                except Exception as e:
                    self.is_connected = False
                    logger.error(f"Camera connection error: {e}")
                    
    def get_frame(self):
        """Captures a frame from the camera, returning the raw OpenCV BGR array."""
        if not self.is_connected:
            self.connect()
            
        if self.is_connected and self.camera:
            with self.lock:
                success, frame = self.camera.read()
                if success:
                    return frame
        return None
        
    def get_jpeg_frame(self):
        """Gets a frame encoded as a JPEG byte array (for raw streaming)."""
        frame = self.get_frame()
        if frame is not None:
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                return jpeg.tobytes()
        return None

    def release(self):
        with self.lock:
            if self.camera:
                self.camera.release()
                self.camera = None
                self.is_connected = False
                logger.info("Camera released.")

camera_service = CameraService()
