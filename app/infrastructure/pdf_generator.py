# app/infrastructure/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from ..domain.entities import Shareholder, ShareIssuance

def generate_pdf_certificate(shareholder: Shareholder, issuance: ShareIssuance) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Watermark
    c.setFont("Helvetica", 60)
    c.setFillColor(colors.lightgrey, alpha=0.3)  # Semi-transparent watermark
    c.saveState()
    c.translate(width/2, height/2)
    c.rotate(45)
    c.drawCentredString(0, 0, "SAMPLE")  # Replace with "VOID" or company logo in production
    c.restoreState()

    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 100, "Example Corp")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 140, "Share Certificate")

    # Certificate Details
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 200, f"Certificate Number: {issuance.id}")
    c.drawString(100, height - 220, f"Shareholder Name: {shareholder.name}")
    c.drawString(100, height - 240, f"Email: {shareholder.email}")
    c.drawString(100, height - 260, f"Number of Shares: {issuance.number_of_shares:,}")
    c.drawString(100, height - 280, f"Price per Share: ${issuance.price:.2f}")
    c.drawString(100, height - 300, f"Total Value: ${(issuance.number_of_shares * issuance.price):,.2f}")
    c.drawString(100, height - 320, f"Issue Date: {issuance.date.strftime('%B %d, %Y')}")
    c.line(100, height - 340, width - 100, height - 340)  # Horizontal line for separation

    # Footer (Optional Legal Note)
    c.setFont("Helvetica", 10)
    c.drawString(100, 100, "This certificate is a system-generated document for internal use only. Not valid without company seal.")
    c.line(100, 80, width - 100, 80)  # Line for signature

    # Save and return
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

