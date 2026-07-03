from flask import Blueprint, render_template
from flask_login import login_required

models_bp = Blueprint('models', __name__)

@models_bp.route('/models')
@login_required
def index():
    from flask import session, redirect, url_for
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth_bp.login'))
    return render_template('model_management.html')
