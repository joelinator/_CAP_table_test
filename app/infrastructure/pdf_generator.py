# app/infrastructure/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

def generate_pdf_certificate(shareholder: 'Shareholder', issuance: 'ShareIssuance') -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Watermark
    c.setFont("Helvetica", 60)
    c.setFillColor(colors.lightgrey)
    c.saveState()
    c.translate(width/2, height/2)
    c.rotate(45)
    c.drawCentredString(0, 0, "SAMPLE")
    c.restoreState()

    # Content
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 100, "Share Certificate")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, f"Shareholder: {shareholder.name}")
    c.drawString(100, height - 170, f"Email: {shareholder.email}")
    c.drawString(100, height - 190, f"Number of Shares: {issuance.number_of_shares}")
    c.drawString(100, height - 210, f"Price per Share: ${issuance.price:.2f}")
    c.drawString(100, height - 230, f"Issue Date: {issuance.date.strftime('%Y-%m-%d')}")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
