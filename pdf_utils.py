"""
PDF generation utilities for medical conversation summaries.
"""

from io import BytesIO
from typing import Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_medical_pdf(
    patient_data: Dict[str, Any],
    summary: str,
    transcript: str
) -> BytesIO:
    """
    Generate a professional PDF report with patient data, summary, and transcript.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        leftMargin=2*cm, 
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=20,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    story = []
    
    # Title
    story.append(Paragraph("Medizinische Gesprächszusammenfassung", title_style))
    story.append(Spacer(1, 12))
    
    # Date
    story.append(Paragraph(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 12))
    
    # Patient Information
    story.append(Paragraph("Patientendaten", heading_style))
    
    # Prepare patient data table
    patient_info = []
    
    # Name
    name = f"{patient_data.get('vorname', '')} {patient_data.get('nachname', '')}".strip()
    if name:
        patient_info.append(['Name:', name])
    
    # Geburtsdatum
    geb = patient_data.get('geburtsdatum', '')
    if geb:
        if hasattr(geb, 'strftime'):
            geb = geb.strftime('%d.%m.%Y')
        patient_info.append(['Geburtsdatum:', str(geb)])
    
    # Geschlecht
    if patient_data.get('geschlecht'):
        patient_info.append(['Geschlecht:', patient_data.get('geschlecht')])
    
    # Größe
    if patient_data.get('groesse'):
        patient_info.append(['Größe:', f"{patient_data.get('groesse')} cm"])
    
    # Gewicht
    if patient_data.get('gewicht'):
        patient_info.append(['Gewicht:', f"{patient_data.get('gewicht')} kg"])
    
    # Therapiebeginn
    tb = patient_data.get('therapiebeginn', '')
    if tb:
        if hasattr(tb, 'strftime'):
            tb = tb.strftime('%d.%m.%Y')
        patient_info.append(['Therapiebeginn:', str(tb)])
    
    # Dauer
    if patient_data.get('dauer'):
        patient_info.append(['Dauer:', f"{patient_data.get('dauer')} Monate"])
    
    # TW besprochen
    if patient_data.get('tw_besprochen'):
        patient_info.append(['TW besprochen:', patient_data.get('tw_besprochen')])
    
    # Allergie
    if patient_data.get('allergie'):
        patient_info.append(['Allergien:', patient_data.get('allergie')])
    
    # Diagnosen
    if patient_data.get('diagnosen'):
        patient_info.append(['Diagnosen:', patient_data.get('diagnosen')])
    
    # Kontrolltermine
    kontroll = []
    if patient_data.get('kontrolltermin_4'):
        kontroll.append("4 Wochen")
    if patient_data.get('kontrolltermin_12'):
        kontroll.append("12 Wochen")
    if kontroll:
        patient_info.append(['Kontrolltermine:', ", ".join(kontroll)])
    
    if patient_data.get('kontrolltermin_kommentar'):
        patient_info.append(['Kommentar:', patient_data.get('kontrolltermin_kommentar')])
    
    if patient_info:
        table = Table(patient_info, colWidths=[4*cm, 12*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1'))
        ]))
        story.append(table)
    else:
        story.append(Paragraph("Keine Patientendaten vorhanden", normal_style))
    
    story.append(Spacer(1, 20))
    
    # Summary
    story.append(Paragraph("Zusammenfassung", heading_style))
    summary_paragraphs = summary.split('\n')
    for para in summary_paragraphs:
        if para.strip():
            story.append(Paragraph(para, normal_style))
            story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 20))
    
    # Transcript (on new page)
    story.append(PageBreak())
    story.append(Paragraph("Vollständiges Transkript", heading_style))
    transcript_paragraphs = transcript.split('\n')
    for para in transcript_paragraphs:
        if para.strip():
            story.append(Paragraph(para, normal_style))
            story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
