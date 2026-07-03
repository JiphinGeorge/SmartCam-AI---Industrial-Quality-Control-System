from flask import Blueprint, render_template

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def index():
    from flask import session, redirect, url_for
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))
    return render_template('settings.html')
