import csv
import pandas as pd
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


csv_file = input("Enter the path to the CSV file: ").strip()
week_start_str = input("Enter the start date of the week (YYYY-MM-DD): ").strip()

try:
    week_start = datetime.strptime(week_start_str, "%Y-%m-%d")
    week_end = week_start + timedelta(days=6)
except ValueError:
    print("Invalid date format. Use YYYY-MM-DD.")
    exit(1)

output_pdf = f"weekly_report_{week_start_str}.pdf"
report_title = f"Team Weekly Status Report – Week of {week_start.strftime('%B %d, %Y')}"

df = pd.read_csv(csv_file)

df['Start time'] = pd.to_datetime(df['Start time'], errors='coerce')

filtered_df = df[(df['Start time'] >= week_start) & (df['Start time'] <= week_end)]

if filtered_df.empty:
    print(f"No responses found between {week_start.date()} and {week_end.date()}.")
    exit(0)

c = canvas.Canvas(output_pdf, pagesize = LETTER)

width, height = LETTER
margin = 1 * inch
y = height-margin

c.setFont("Helvetica-Bold", 18)
c.drawString(margin, y, report_title)
y -= 0.4 * inch

for i, row in filtered_df.iterrows():
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
       c.showPage
       y = height-margin

c.save()