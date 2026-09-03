"""
Certificate PDF generation using ReportLab.

This is the single place in the codebase that knows how to render a
certificate PDF. It is intentionally free of any DB-writing logic so it
stays reusable/testable in isolation.
"""
import logging
from pathlib import Path

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

from app.core.config import settings

logger = logging.getLogger("app.certificate")

NAVY = HexColor("#1e293b")
GOLD = HexColor("#b8860b")
SLATE = HexColor("#475569")
LIGHT_GOLD = HexColor("#f0e6c8")
CORAL = HexColor("#e76f51")
TEAL = HexColor("#2a9d8f")
SKY = HexColor("#457b9d")


def _centered_text(c: canvas.Canvas, text: str, y: float, font: str, size: int, color, page_width: float):
    c.setFont(font, size)
    c.setFillColor(color)
    w = stringWidth(text, font, size)
    c.drawString((page_width - w) / 2.0, y, text)


def generate_certificate_pdf(
    *,
    employee_full_name: str,
    employee_code: str,
    certificate_id: str,
    achieved_hours: float,
    target_hours: float,
    issue_date_str: str,
    course_title: str | None = None,
) -> str:
    """
    Renders a certificate PDF to settings.CERTIFICATES_DIR and returns the
    absolute file path (as a string).
    """
    filename = f"{certificate_id}.pdf"
    filepath: Path = settings.CERTIFICATES_DIR / filename

    page_size = landscape(A4)
    page_width, page_height = page_size

    c = canvas.Canvas(str(filepath), pagesize=page_size)

    # --- Background ---
    c.setFillColor(HexColor("#fffdf7"))
    c.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # Colorful corner accents make the certificate recognizable when printed.
    c.setFillColor(CORAL)
    c.wedge(-18 * mm, page_height - 32 * mm, 28 * mm, page_height + 14 * mm, 270, 90, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.wedge(page_width - 28 * mm, -14 * mm, page_width + 18 * mm, 32 * mm, 90, 90, fill=1, stroke=0)

    # --- Outer border ---
    margin = 14 * mm
    c.setStrokeColor(NAVY)
    c.setLineWidth(2.5)
    c.rect(margin, margin, page_width - 2 * margin, page_height - 2 * margin, fill=0, stroke=1)

    # --- Inner decorative border ---
    inner_margin = margin + 5 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.rect(inner_margin, inner_margin, page_width - 2 * inner_margin, page_height - 2 * inner_margin, fill=0, stroke=1)
    c.setFillColor(CORAL)
    c.rect(inner_margin, page_height - inner_margin - 2 * mm, 42 * mm, 2 * mm, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(page_width - inner_margin - 42 * mm, inner_margin, 42 * mm, 2 * mm, fill=1, stroke=0)

    # --- Organization branding area (top) ---
    emblem_x = page_width / 2
    emblem_y = page_height - 21 * mm
    c.setFillColor(GOLD)
    c.circle(emblem_x, emblem_y, 5 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#fffdf7"))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(emblem_x, emblem_y - 3, "LD")
    _centered_text(c, settings.ORGANIZATION_NAME.upper(), page_height - 32 * mm, "Helvetica-Bold", 16, NAVY, page_width)

    # Thin gold rule under org name
    rule_w = 70 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line((page_width - rule_w) / 2, page_height - 36 * mm, (page_width + rule_w) / 2, page_height - 36 * mm)

    # --- Certificate title ---
    _centered_text(c, "CERTIFICATE OF LEARNING ACHIEVEMENT", page_height - 52 * mm, "Helvetica-Bold", 28, NAVY, page_width)

    # --- "presented to" ---
    _centered_text(c, "This certificate is proudly presented to", page_height - 66 * mm, "Helvetica-Oblique", 13, SLATE, page_width)

    # --- Employee name ---
    _centered_text(c, employee_full_name, page_height - 82 * mm, "Helvetica-Bold", 30, GOLD, page_width)

    # underline beneath name
    name_w = stringWidth(employee_full_name, "Helvetica-Bold", 30)
    underline_w = max(name_w + 20 * mm, 90 * mm)
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.8)
    c.line((page_width - underline_w) / 2, page_height - 86 * mm, (page_width + underline_w) / 2, page_height - 86 * mm)

    # --- Achievement statement ---
    statement = (
        f"in recognition of successfully completing {achieved_hours:g} hours of learning "
        f"and achieving the required learning target of {target_hours:g} hours."
    )
    c.setFont("Helvetica", 12)
    c.setFillColor(SLATE)
    max_text_width = page_width - 2 * inner_margin - 40 * mm
    words = statement.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if stringWidth(trial, "Helvetica", 12) <= max_text_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = page_height - 98 * mm
    for line in lines:
        _centered_text(c, line, y, "Helvetica", 12, SLATE, page_width)
        y -= 6 * mm

    if course_title:
        _centered_text(c, f"Course: {course_title}", y - 2 * mm, "Helvetica-Bold", 11, NAVY, page_width)

    # --- Bottom section: Employee ID / Certificate ID / Date / Signature ---
    bottom_y = margin + 22 * mm

    left_x = inner_margin + 15 * mm
    right_x = page_width - inner_margin - 15 * mm

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(NAVY)
    c.drawString(left_x, bottom_y + 14 * mm, f"Employee ID: {employee_code}")
    c.drawString(left_x, bottom_y + 8 * mm, f"Certificate ID: {certificate_id}")
    c.drawString(left_x, bottom_y + 2 * mm, f"Issue Date: {issue_date_str}")

    # Signature area (right side)
    sig_line_w = 55 * mm
    c.setStrokeColor(SLATE)
    c.setLineWidth(0.8)
    c.line(right_x - sig_line_w, bottom_y + 10 * mm, right_x, bottom_y + 10 * mm)

    c.setFont("Helvetica", 9)
    c.setFillColor(SLATE)
    sig_name = settings.CERTIFICATE_SIGNATURE_NAME
    sig_w = stringWidth(sig_name, "Helvetica", 9)
    c.drawString(right_x - sig_line_w + (sig_line_w - sig_w) / 2, bottom_y + 5 * mm, sig_name)

    c.setFont("Helvetica-Oblique", 8)
    label = "Authorized Signature"
    label_w = stringWidth(label, "Helvetica-Oblique", 8)
    c.drawString(right_x - sig_line_w + (sig_line_w - label_w) / 2, bottom_y, label)

    # Stylized Shrithii signature mark remains crisp when printed.
    signature = c.beginPath()
    signature.moveTo(right_x - 42 * mm, bottom_y + 14 * mm)
    signature.curveTo(right_x - 39 * mm, bottom_y + 24 * mm, right_x - 30 * mm, bottom_y + 6 * mm, right_x - 34 * mm, bottom_y + 14 * mm)
    signature.curveTo(right_x - 38 * mm, bottom_y + 22 * mm, right_x - 25 * mm, bottom_y + 23 * mm, right_x - 25 * mm, bottom_y + 14 * mm)
    c.setStrokeColor(SKY)
    c.setLineWidth(1.8)
    c.drawPath(signature, stroke=1, fill=0)

    # QR scanner code sits between the certificate details and signature.
    qr = QrCodeWidget(f"{settings.FRONTEND_URL}/verify/{certificate_id}")
    qr.barWidth = 22 * mm
    qr.barHeight = 22 * mm
    drawing = Drawing(22 * mm, 22 * mm)
    drawing.add(qr)
    qr_x = (page_width - 22 * mm) / 2
    renderPDF.draw(drawing, c, qr_x, bottom_y - 1 * mm)
    c.setFillColor(SLATE)
    c.setFont("Helvetica", 7)
    c.drawCentredString(page_width / 2, bottom_y - 5 * mm, "Scan to verify")

    c.showPage()
    c.save()

    logger.info("Certificate PDF generated: %s", filepath)
    return str(filepath)
