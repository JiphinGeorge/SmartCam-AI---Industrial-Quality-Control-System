from app.services.logger import get_logger

logger = get_logger('app')

class NotificationService:
    @staticmethod
    def send_rotten_alert(filename, confidence, inference_time):
        """Triggers an alert when a rotten item is detected."""
        msg = f"ALERT: Rotten item detected in {filename} (Confidence: {confidence:.2f}%) [Time: {inference_time}ms]"
        logger.warning(msg)
        # Future: Send WebSocket event to UI for toast notification
        from app import socketio
        socketio.emit('notification', {
            'type': 'alert',
            'message': f"Rotten item detected: {filename}",
            'confidence': confidence
        })
        
    @staticmethod
    def log_system_event(event_msg):
        sys_logger = get_logger('system')
        sys_logger.info(event_msg)
        from app import socketio
        socketio.emit('system_log', {'message': event_msg})
