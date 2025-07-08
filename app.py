import pandas as pd

from datetime import datetime, timedelta

from reportlab.lib.pagesizes import LETTER

from reportlab.pdfgen import canvas

from reportlab.lib.units import inch

from flask import Flask, request, jsonify

import io

import base64
 
app = Flask(__name__)
 
@app.route('/convert', methods=['POST'])

def convert():

    data = request.get_json()
 
    if 'rows' not in data or 'week_start' not in data:

        return jsonify({"error": "Missing rows or week_start"}), 400
 
    rows = data['rows']

    week_start_str = data['week_start']
 
    try:

        week_start = datetime.strptime(week_start_str, '%Y-%m-%d')

        week_end = week_start + timedelta(days=6)

    except ValueError:

        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
 
    df = pd.DataFrame(rows)

    df['Start time'] = pd.to_datetime(df['Start time'], errors='coerce')
 
    filtered_df = df[(df['Start time'] >= week_start) & (df['Start time'] <= week_end)]
 
    if filtered_df.empty:

        return jsonify({

            "message": f"No responses found between {week_start.date()} and {week_end.date()}",

            "content_base64": None

        }), 200
 
    output = io.BytesIO()

    c = canvas.Canvas(output, pagesize=LETTER)

    width, height = LETTER

    margin = 1 * inch

    y = height - margin
 
    report_title = f"Team Weekly Status Report – Week of {week_start.strftime('%B %d, %Y')}"

    c.setFont("Helvetica-Bold", 18)

    c.drawString(margin, y, report_title)

    y -= 0.4 * inch
 
    for _, row in filtered_df.iterrows():

        name = row.get('Name1', 'Unknown')

        project = row.get('Project', 'No Project Specified')

        progress = str(row.get('Progress', '')).strip()

        blockers = str(row.get('Blockers', '')).strip()

        next_steps = str(row.get('Next Steps', '')).strip()

        update = str(row.get('Weekly Status Update', '')).strip()
 
        c.setFont("Helvetica-Bold", 14)

        c.drawString(margin, y, f"{name} - {project}")

        y -= 0.25 * inch
 
        c.setFont("Helvetica", 12)

        sections = [

            ("Progress", progress),

            ("Blockers", blockers),

            ("Next Steps", next_steps),

            ("General Update", update)

        ]
 
        for label, content in sections:

            if content:

                c.drawString(margin + 0.2 * inch, y, f"{label}:")

                y -= 0.2 * inch

                for line in content.split('\n'):

                    c.drawString(margin + 0.6 * inch, y, f"- {line}")

                    y -= 0.2 * inch

                y -= 0.1 * inch
 
        y -= 0.3 * inch

        if y < margin:

            c.showPage()

            y = height - margin
 
    c.save()

    output.seek(0)
 
    pdf_bytes = output.getvalue()

    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
 
    return jsonify({

        "filename": f"weekly_report_{week_start_str}.pdf",

        "content_base64": pdf_base64

    })
 
if __name__ == '__main__':

    app.run()

 