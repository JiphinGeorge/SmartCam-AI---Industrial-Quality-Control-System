from flask import Blueprint, render_template
from flask_login import login_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    from app.services.report import ReportService
    
    daily_count = len(ReportService.get_data('daily'))
    weekly_count = len(ReportService.get_data('weekly'))
    monthly_count = len(ReportService.get_data('monthly'))
    
    # Estimate PDF size: base 0.5 MB + 0.002 MB per row
    def calc_size(count):
        size = 0.5 + (count * 0.002)
        return round(size, 1)
        
    return render_template('reports.html', 
                           daily_size=calc_size(daily_count),
                           weekly_size=calc_size(weekly_count),
                           monthly_size=calc_size(monthly_count))
