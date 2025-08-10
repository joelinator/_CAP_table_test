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
    
    # Define a custom color palette
    COMPANY_BLUE = colors.HexColor('#003366')
    BODY_TEXT_GRAY = colors.HexColor('#333333')
    LINE_GRAY = colors.HexColor('#C0C0C0')

    # Add a border to the page for a framed look
    c.setStrokeColor(COMPANY_BLUE)
    c.setLineWidth(3)
    c.rect(inch * 0.75, inch * 0.75, width - inch * 1.5, height - inch * 1.5)

    # --- Watermark (Company Name) ---
    c.saveState()
    c.setFont("Helvetica-Bold", 80)  # Larger font for the watermark
    c.setFillColor(LINE_GRAY, alpha=0.1)  # Lighter, more subtle transparency
    c.translate(width/2, height/2)
    c.rotate(45)
    c.drawCentredString(0, 0, "joelinator.org")
    c.restoreState()

    # --- Header ---
    # Add a placeholder for a company logo 
    # You would use c.drawImage('logo.png', x, y, width, height) here.
    # For now, we'll leave a space and a text placeholder.
    c.setFillColor(COMPANY_BLUE)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 100, height - 80, "joelinator.org")
    
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(COMPANY_BLUE)
    c.drawCentredString(width/2, height - 120, "Share Certificate")
    
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height - 150, "Certificate of Ownership")

    # --- Certificate Details Section ---
    y_position = height - 250
    left_margin = 100
    line_spacing = 30
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(BODY_TEXT_GRAY)
    
    # Labels in bold
    c.drawString(left_margin, y_position, "Certificate Number:")
    y_position -= line_spacing
    c.drawString(left_margin, y_position, "Shareholder Name:")
    y_position -= line_spacing
    c.drawString(left_margin, y_position, "Number of Shares:")
    y_position -= line_spacing
    c.drawString(left_margin, y_position, "Issue Date:")

    # Data in regular font, aligned to the right of the labels
    data_x_position = left_margin + 180
    y_position = height - 250
    c.setFont("Helvetica", 12)
    c.drawString(data_x_position, y_position, str(issuance.id))
    y_position -= line_spacing
    c.drawString(data_x_position, y_position, shareholder.name)
    y_position -= line_spacing
    c.drawString(data_x_position, y_position, f"{issuance.number_of_shares:,}")
    y_position -= line_spacing
    c.drawString(data_x_position, y_position, issuance.date.strftime('%B %d, %Y'))

    # Add a separator line
    c.setStrokeColor(LINE_GRAY)
    c.setLineWidth(1)
    c.line(left_margin, y_position - 15, width - left_margin, y_position - 15)

    # --- Financial Details Section ---
    y_position -= line_spacing * 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, y_position, "Financial Details")
    
    y_position -= line_spacing
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y_position, "Price per Share:")
    c.setFont("Helvetica", 12)
    c.drawString(data_x_position, y_position, f"${issuance.price:.2f}")

    y_position -= line_spacing
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y_position, "Total Value:")
    c.setFont("Helvetica", 12)
    c.drawString(data_x_position, y_position, f"${(issuance.number_of_shares * issuance.price):,.2f}")

    # --- Footer ---
    footer_y = 120
    c.setStrokeColor(COMPANY_BLUE)
    c.line(width * 0.6, footer_y, width * 0.9, footer_y)
    
    c.setFont("Helvetica", 10)
    c.setFillColor(BODY_TEXT_GRAY)
    c.drawRightString(width * 0.75, footer_y - 15, "Authorized Signature")
    

    # Save and return
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
