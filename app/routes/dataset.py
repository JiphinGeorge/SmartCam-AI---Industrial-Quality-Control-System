from flask import Blueprint, render_template

dataset_bp = Blueprint('dataset', __name__)

@dataset_bp.route('/dataset')
def index():
    from flask import session, redirect, url_for
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth.login'))
    return render_template('dataset.html')
