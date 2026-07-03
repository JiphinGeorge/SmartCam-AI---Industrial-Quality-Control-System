from flask import Flask, render_template
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    
    from app.config import Config
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'smartcam-industrial-secret'
    Config.setup_directories()
    
    # Initialize plugins
    socketio.init_app(app)
    
    from flask_talisman import Talisman
    # Disable HTTPS redirect in development/local, set strict CSP
    csp = {
        'default-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'https://cdn.tailwindcss.com',
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com'
        ],
        'img-src': ['\'self\'', 'data:', 'blob:', 'https:'],
        'script-src': ['\'self\'', '\'unsafe-inline\'', '\'unsafe-eval\'', 'https:'],
        'style-src': ['\'self\'', '\'unsafe-inline\'', 'https:']
    }
    Talisman(app, content_security_policy=csp, force_https=False)
    
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    # Apply to auth blueprint specifically
    
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.get(user_id)
    
    # Initialize logger
    from app.services.logger import setup_logger
    setup_logger(Config.LOGS_DIR)
    
    # Register blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.inspection import inspection_bp
    from app.routes.analytics import analytics_bp
    from app.routes.reports import reports_bp
    from app.routes.history import history_bp
    from app.routes.dataset import dataset_bp
    from app.routes.models import models_bp
    from app.routes.settings import settings_bp
    from app.routes.knowledge import knowledge_bp
    from app.routes.live import live_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inspection_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(live_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    @app.route('/inspection_history/<path:filename>')
    def serve_inspection_history(filename):
        from flask import send_from_directory
        from app.config import Config
        return send_from_directory(Config.INSPECTION_HISTORY_DIR, filename)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app
