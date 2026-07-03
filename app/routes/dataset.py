from flask import Blueprint, render_template
from flask_login import login_required

dataset_bp = Blueprint('dataset', __name__)

@dataset_bp.route('/dataset')
@login_required
def index():
    return render_template('dataset.html')
