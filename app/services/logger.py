import logging
import os

def setup_logger(log_dir):
    """Configures centralized logging for the application."""
    
    # Define log formats
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 1. Application Log
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    app_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'))
    app_handler.setFormatter(formatter)
    app_logger.addHandler(app_handler)
    
    # 2. Prediction Log
    pred_logger = logging.getLogger('prediction')
    pred_logger.setLevel(logging.INFO)
    pred_handler = logging.FileHandler(os.path.join(log_dir, 'prediction.log'))
    pred_handler.setFormatter(formatter)
    pred_logger.addHandler(pred_handler)
    
    # 3. System Log
    sys_logger = logging.getLogger('system')
    sys_logger.setLevel(logging.WARNING)
    sys_handler = logging.FileHandler(os.path.join(log_dir, 'system.log'))
    sys_handler.setFormatter(formatter)
    sys_logger.addHandler(sys_handler)
    
    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    app_logger.addHandler(console_handler)
    
    app_logger.info("Centralized logger initialized.")

def get_logger(name):
    return logging.getLogger(name)
