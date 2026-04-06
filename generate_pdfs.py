"""
Generate mock printed PDFs and their ground truth files for OCR benchmarking.
Creates:
  - test_documents/printed/en_payroll_register.pdf
  - test_documents/printed/es_factura.pdf
  - test_documents/printed/fr_rapport_medical.pdf
  - ground_truth/ for each
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os

OUT_DIR = "test_documents/printed"
GT_DIR = "ground_truth"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(GT_DIR, exist_ok=True)

styles = getSampleStyleSheet()

# ─── English Payroll Register ───────────────────────────────────────────────

def make_en_payroll():
    pdf_path = os.path.join(OUT_DIR, "en_payroll_register.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)

    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, spaceAfter=12)
    subtitle_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10, spaceAfter=6)
    normal = styles["Normal"]

    elements = []
    elements.append(Paragraph("ACME Corporation", title_style))
    elements.append(Paragraph("Payroll Register — March 2026", subtitle_style))
    elements.append(Paragraph("Department: Engineering | Pay Period: 03/01/2026 – 03/31/2026", subtitle_style))
    elements.append(Spacer(1, 0.2 * inch))

    header = ["Employee ID", "Name", "Hours", "Rate ($)", "Gross Pay ($)", "Tax ($)", "Net Pay ($)"]
    data = [
        header,
        ["ENG-1001", "Alice Johnson", "160", "45.00", "7,200.00", "1,440.00", "5,760.00"],
        ["ENG-1002", "Bob Martinez", "168", "52.50", "8,820.00", "1,764.00", "7,056.00"],
        ["ENG-1003", "Carol Zhang", "152", "48.75", "7,410.00", "1,482.00", "5,928.00"],
        ["ENG-1004", "David Okafor", "160", "55.00", "8,800.00", "1,760.00", "7,040.00"],
        ["ENG-1005", "Elena Petrov", "144", "47.25", "6,804.00", "1,360.80", "5,443.20"],
        ["ENG-1006", "Frank Nguyen", "160", "50.00", "8,000.00", "1,600.00", "6,400.00"],
        ["ENG-1007", "Grace Kim", "176", "51.00", "8,976.00", "1,795.20", "7,180.80"],
        ["ENG-1008", "Henry Davis", "160", "46.50", "7,440.00", "1,488.00", "5,952.00"],
        ["", "TOTALS", "1,280", "", "63,450.00", "12,690.00", "50,760.00"],
    ]

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecf0f1")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Approved by: Sarah Thompson, VP Finance", normal))
    elements.append(Paragraph("Date: April 1, 2026", normal))

    doc.build(elements)

    # Ground truth
    gt_lines = [
        "ACME Corporation",
        "Payroll Register — March 2026",  # note: reportlab may render the em-dash differently
        "Department: Engineering | Pay Period: 03/01/2026 – 03/31/2026",
        "",
        "Employee ID | Name | Hours | Rate ($) | Gross Pay ($) | Tax ($) | Net Pay ($)",
        "ENG-1001 | Alice Johnson | 160 | 45.00 | 7,200.00 | 1,440.00 | 5,760.00",
        "ENG-1002 | Bob Martinez | 168 | 52.50 | 8,820.00 | 1,764.00 | 7,056.00",
        "ENG-1003 | Carol Zhang | 152 | 48.75 | 7,410.00 | 1,482.00 | 5,928.00",
        "ENG-1004 | David Okafor | 160 | 55.00 | 8,800.00 | 1,760.00 | 7,040.00",
        "ENG-1005 | Elena Petrov | 144 | 47.25 | 6,804.00 | 1,360.80 | 5,443.20",
        "ENG-1006 | Frank Nguyen | 160 | 50.00 | 8,000.00 | 1,600.00 | 6,400.00",
        "ENG-1007 | Grace Kim | 176 | 51.00 | 8,976.00 | 1,795.20 | 7,180.80",
        "ENG-1008 | Henry Davis | 160 | 46.50 | 7,440.00 | 1,488.00 | 5,952.00",
        "TOTALS | 1,280 | | 63,450.00 | 12,690.00 | 50,760.00",
        "",
        "Approved by: Sarah Thompson, VP Finance",
        "Date: April 1, 2026",
    ]
    with open(os.path.join(GT_DIR, "en_payroll_register.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(gt_lines))

    print(f"  ✓ {pdf_path}")


# ─── Spanish Invoice (Factura) ──────────────────────────────────────────────

def make_es_factura():
    pdf_path = os.path.join(OUT_DIR, "es_factura.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)

    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=20, spaceAfter=6)
    bold_style = ParagraphStyle("B", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold")
    normal = ParagraphStyle("N", parent=styles["Normal"], fontSize=10)

    elements = []
    elements.append(Paragraph("FACTURA", title_style))
    elements.append(Paragraph("Número de Factura: FAC-2026-04821", bold_style))
    elements.append(Paragraph("Fecha de Emisión: 15 de marzo de 2026", normal))
    elements.append(Paragraph("Fecha de Vencimiento: 14 de abril de 2026", normal))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(HRFlowable(width="100%", color=colors.grey))
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph("Emisor: Soluciones Tecnológicas del Norte S.A. de C.V.", bold_style))
    elements.append(Paragraph("RFC: STN-050312-AB7", normal))
    elements.append(Paragraph("Dirección: Av. Revolución 1425, Col. Centro, Monterrey, N.L., C.P. 64000", normal))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph("Cliente: Importadora García Hermanos S.A.", bold_style))
    elements.append(Paragraph("RFC: IGH-980723-QR5", normal))
    elements.append(Paragraph("Dirección: Calle 5 de Mayo 302, Col. Juárez, Ciudad de México, C.P. 06600", normal))
    elements.append(Spacer(1, 0.2 * inch))

    header = ["Código", "Descripción", "Cantidad", "Precio Unit. (MXN)", "Importe (MXN)"]
    data = [
        header,
        ["SRV-001", "Consultoría en infraestructura de TI", "40 hrs", "$1,250.00", "$50,000.00"],
        ["SRV-002", "Desarrollo de aplicación móvil", "120 hrs", "$950.00", "$114,000.00"],
        ["LIC-010", "Licencia anual de software ERP", "5", "$8,500.00", "$42,500.00"],
        ["HW-055", "Servidor Dell PowerEdge R750", "2", "$45,000.00", "$90,000.00"],
    ]

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.15 * inch))

    summary = [
        ["", "", "Subtotal:", "$296,500.00"],
        ["", "", "IVA (16%):", "$47,440.00"],
        ["", "", "Total:", "$343,940.00"],
    ]
    st = Table(summary, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    st.setStyle(TableStyle([
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (2, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LINEABOVE", (2, 2), (-1, 2), 1, colors.black),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Método de Pago: Transferencia bancaria", normal))
    elements.append(Paragraph("Banco: BBVA México | Cuenta: 0123456789 | CLABE: 012345678901234567", normal))

    doc.build(elements)

    gt_lines = [
        "FACTURA",
        "Número de Factura: FAC-2026-04821",
        "Fecha de Emisión: 15 de marzo de 2026",
        "Fecha de Vencimiento: 14 de abril de 2026",
        "",
        "Emisor: Soluciones Tecnológicas del Norte S.A. de C.V.",
        "RFC: STN-050312-AB7",
        "Dirección: Av. Revolución 1425, Col. Centro, Monterrey, N.L., C.P. 64000",
        "",
        "Cliente: Importadora García Hermanos S.A.",
        "RFC: IGH-980723-QR5",
        "Dirección: Calle 5 de Mayo 302, Col. Juárez, Ciudad de México, C.P. 06600",
        "",
        "Código | Descripción | Cantidad | Precio Unit. (MXN) | Importe (MXN)",
        "SRV-001 | Consultoría en infraestructura de TI | 40 hrs | $1,250.00 | $50,000.00",
        "SRV-002 | Desarrollo de aplicación móvil | 120 hrs | $950.00 | $114,000.00",
        "LIC-010 | Licencia anual de software ERP | 5 | $8,500.00 | $42,500.00",
        "HW-055 | Servidor Dell PowerEdge R750 | 2 | $45,000.00 | $90,000.00",
        "",
        "Subtotal: $296,500.00",
        "IVA (16%): $47,440.00",
        "Total: $343,940.00",
        "",
        "Método de Pago: Transferencia bancaria",
        "Banco: BBVA México | Cuenta: 0123456789 | CLABE: 012345678901234567",
    ]
    with open(os.path.join(GT_DIR, "es_factura.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(gt_lines))

    print(f"  ✓ {pdf_path}")


# ─── French Medical Report ──────────────────────────────────────────────────

def make_fr_rapport_medical():
    pdf_path = os.path.join(OUT_DIR, "fr_rapport_medical.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)

    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=18, spaceAfter=6)
    bold_style = ParagraphStyle("B", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold")
    normal = ParagraphStyle("N", parent=styles["Normal"], fontSize=10, leading=14)

    elements = []
    elements.append(Paragraph("RAPPORT D'ANALYSES MÉDICALES", title_style))
    elements.append(Paragraph("Laboratoire BioSanté — Paris", bold_style))
    elements.append(Paragraph("N° de dossier : LAB-2026-77412", normal))
    elements.append(Paragraph("Date du prélèvement : 10 mars 2026", normal))
    elements.append(Paragraph("Date du rapport : 12 mars 2026", normal))
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph("Patient : Jean-Pierre Lefèvre", bold_style))
    elements.append(Paragraph("Date de naissance : 08/05/1974 | Sexe : Masculin", normal))
    elements.append(Paragraph("Médecin prescripteur : Dr. Marie-Claire Dubois", normal))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("RÉSULTATS — Bilan Sanguin Complet", bold_style))
    elements.append(Spacer(1, 0.1 * inch))

    header = ["Analyse", "Résultat", "Unité", "Valeurs de Référence"]
    data = [
        header,
        ["Hémoglobine", "14.2", "g/dL", "13.0 – 17.5"],
        ["Hématocrite", "42.8", "%", "38.0 – 50.0"],
        ["Globules blancs", "7,200", "/mm³", "4,000 – 10,000"],
        ["Plaquettes", "245,000", "/mm³", "150,000 – 400,000"],
        ["Glycémie à jeun", "5.8", "mmol/L", "3.9 – 5.5"],
        ["Cholestérol total", "6.1", "mmol/L", "< 5.2"],
        ["HDL Cholestérol", "1.3", "mmol/L", "> 1.0"],
        ["LDL Cholestérol", "4.2", "mmol/L", "< 3.4"],
        ["Triglycérides", "1.9", "mmol/L", "< 1.7"],
        ["Créatinine", "88", "µmol/L", "62 – 106"],
        ["TSH", "2.45", "mUI/L", "0.27 – 4.20"],
    ]

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2980b9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (2, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#fdebd0")),
        ("BACKGROUND", (0, 6), (-1, 6), colors.HexColor("#fdebd0")),
        ("BACKGROUND", (0, 8), (-1, 8), colors.HexColor("#fdebd0")),
        ("BACKGROUND", (0, 9), (-1, 9), colors.HexColor("#fdebd0")),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "Commentaire : La glycémie à jeun est légèrement élevée (pré-diabète). "
        "Le cholestérol total et le LDL sont au-dessus des valeurs recommandées. "
        "Un contrôle dans 3 mois est conseillé avec régime alimentaire adapté.",
        normal
    ))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Biologiste responsable : Dr. Antoine Moreau", bold_style))
    elements.append(Paragraph("Signature : _______________________", normal))

    doc.build(elements)

    gt_lines = [
        "RAPPORT D'ANALYSES MÉDICALES",
        "Laboratoire BioSanté — Paris",
        "N° de dossier : LAB-2026-77412",
        "Date du prélèvement : 10 mars 2026",
        "Date du rapport : 12 mars 2026",
        "",
        "Patient : Jean-Pierre Lefèvre",
        "Date de naissance : 08/05/1974 | Sexe : Masculin",
        "Médecin prescripteur : Dr. Marie-Claire Dubois",
        "",
        "RÉSULTATS — Bilan Sanguin Complet",
        "",
        "Analyse | Résultat | Unité | Valeurs de Référence",
        "Hémoglobine | 14.2 | g/dL | 13.0 – 17.5",
        "Hématocrite | 42.8 | % | 38.0 – 50.0",
        "Globules blancs | 7,200 | /mm³ | 4,000 – 10,000",
        "Plaquettes | 245,000 | /mm³ | 150,000 – 400,000",
        "Glycémie à jeun | 5.8 | mmol/L | 3.9 – 5.5",
        "Cholestérol total | 6.1 | mmol/L | < 5.2",
        "HDL Cholestérol | 1.3 | mmol/L | > 1.0",
        "LDL Cholestérol | 4.2 | mmol/L | < 3.4",
        "Triglycérides | 1.9 | mmol/L | < 1.7",
        "Créatinine | 88 | µmol/L | 62 – 106",
        "TSH | 2.45 | mUI/L | 0.27 – 4.20",
        "",
        "Commentaire : La glycémie à jeun est légèrement élevée (pré-diabète). "
        "Le cholestérol total et le LDL sont au-dessus des valeurs recommandées. "
        "Un contrôle dans 3 mois est conseillé avec régime alimentaire adapté.",
        "",
        "Biologiste responsable : Dr. Antoine Moreau",
        "Signature : _______________________",
    ]
    with open(os.path.join(GT_DIR, "fr_rapport_medical.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(gt_lines))

    print(f"  ✓ {pdf_path}")


if __name__ == "__main__":
    print("Generating printed PDFs...")
    make_en_payroll()
    make_es_factura()
    make_fr_rapport_medical()
    print("Done! 3 PDFs + 3 ground truth files created.")
