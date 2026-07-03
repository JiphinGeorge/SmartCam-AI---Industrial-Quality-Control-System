from flask import Blueprint, render_template

models_bp = Blueprint('models', __name__)

@models_bp.route('/models')
def index():
    from flask import session, redirect, url_for
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))
    return render_template('model_management.html')
