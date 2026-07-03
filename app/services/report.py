import csv
import json
import io
from datetime import datetime, timedelta
from app.services.database import DatabaseService

class ReportService:
    @staticmethod
    def get_data(timeframe='daily'):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        if timeframe == 'daily':
            start_date = now - timedelta(days=1)
        elif timeframe == 'weekly':
            start_date = now - timedelta(days=7)
        elif timeframe == 'monthly':
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(days=1)
            
        start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT id, timestamp, prediction, confidence, status, inference_time_ms, operator, location, batch_id
            FROM predictions
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        ''', (start_str,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        return [dict(row) for row in rows]

    @staticmethod
    def generate_csv(data):
        output = io.StringIO()
        if not data:
            return output.getvalue()
            
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()

    @staticmethod
    def generate_json(data):
        return json.dumps(data, indent=4)

    @staticmethod
    def generate_excel(data):
        from openpyxl import Workbook
        from io import BytesIO
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Inspection Report"
        
        if data:
            # Write header
            headers = list(data[0].keys())
            ws.append(headers)
            
            # Write rows
            for row in data:
                ws.append([row[h] for h in headers])
                
        output = BytesIO()
        wb.save(output)
        return output.getvalue()

    @staticmethod
    def generate_pdf(data, timeframe):
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(f"QualiVision AI - {timeframe.capitalize()} Report", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 24))

        if not data:
            elements.append(Paragraph("No data found for this timeframe.", styles['Normal']))
        else:
            # Table Header
            table_data = [['ID', 'Timestamp', 'Status', 'Confidence', 'Operator']]
            
            # Add up to 50 rows to avoid giant PDFs for now
            for row in data[:50]:
                table_data.append([
                    str(row['id']),
                    row['timestamp'][:16],
                    row['status'],
                    f"{row['confidence']:.1f}%",
                    row['operator']
                ])
                
            if len(data) > 50:
                table_data.append(['...', '...', '...', '...', '...'])

            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#111c2d')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#2a3547')),
                ('TEXTCOLOR', (0,1), (-1,-1), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#45474c'))
            ]))
            elements.append(t)

        doc.build(elements)
        return output.getvalue()
