from flask import Blueprint, render_template
from flask_login import login_required

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def index():
    from flask import current_app
    from flask_login import current_user
    if current_user.role != 'Administrator':
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))
    return render_template('settings.html')
