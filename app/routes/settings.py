from flask import Blueprint, render_template
from flask_login import login_required

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def index():
    from flask import session, redirect, url_for
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))
    return render_template('settings.html')
