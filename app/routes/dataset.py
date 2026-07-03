from flask import Blueprint, render_template
from flask_login import login_required

dataset_bp = Blueprint('dataset', __name__)

@dataset_bp.route('/dataset')
@login_required
def index():
    from flask import session, redirect, url_for
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth_bp.login'))
    return render_template('dataset.html')
