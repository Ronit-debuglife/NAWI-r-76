"""
ReportLab Professional PDF Report Generator
Generates publication-quality OIML R-76 NAWI Verification Test Reports.
"""

import os
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas
from config import PDF_DIR
from r76_calculator import CLASS_NAMES


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render total page numbers
    along with running header and footer on every page.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 11 * inch - 26, "NAWI Test Report — OIML R-76 Metrological Evaluation")
            self.drawRightString(8.5 * inch - 36, 11 * inch - 26, f"Ref: {getattr(self, '_report_id', '')}")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 38, 8.5 * inch - 36, 38)
        
        self.drawString(36, 26, "Confidential — Conforming to OIML R-76-1 (2006) Requirements — NAWI System")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 36, 26, page_str)
        self.restoreState()


def build_pdf_report(report_data: Dict[str, Any], evaluation: Dict[str, Any]) -> str:
    """
    Builds a professional multi-page PDF report using ReportLab and returns the file path.
    """
    report_id = report_data.get("report_id", "R76-TEMP")
    file_name = f"NAWI_Report_{report_id}.pdf"
    file_path = os.path.join(PDF_DIR, file_name)

    # Document setup: standard letter, 0.5-inch margins for dense professional layout
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
    )
    h1_style = ParagraphStyle(
        "SecH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=4,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1E293B"),
    )
    cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
    )
    cell_header = ParagraphStyle(
        "TableHead",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )
    badge_pass = ParagraphStyle(
        "PassBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#047857"),
        alignment=1,
    )
    badge_fail = ParagraphStyle(
        "FailBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#B91C1C"),
        alignment=1,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#64748B"),
    )

    story = []

    # 1. Header Banner & Title Block
    instrument = report_data.get("instrument", {})
    environment = report_data.get("environment", {})
    standards = report_data.get("standards", {})
    cert_no = report_data.get("certificate_no", f"CERT-{report_id}")
    test_date = report_data.get("test_date", "")
    overall_status = evaluation.get("overall_status", "FAIL")
    is_in_service = report_data.get("is_in_service", False)
    test_type_str = "In-Service Verification" if is_in_service else "Initial Verification (Type Approval/New)"

    header_table_data = [
        [
            Paragraph("<b>OIML R-76 METROLOGY LABORATORY</b><br/><font size=7 color='#64748B'>NON-AUTOMATIC WEIGHING INSTRUMENT (NAWI) VERIFICATION</font>", title_style),
            Paragraph(
                f"<font size=8 color='#475569'><b>Report Ref:</b> {report_id}<br/>"
                f"<b>Cert No:</b> {cert_no}<br/>"
                f"<b>Date:</b> {test_date}<br/>"
                f"<b>Test Type:</b> {test_type_str}</font>",
                subtitle_style
            ),
        ]
    ]
    t_header = Table(header_table_data, colWidths=[5.0 * inch, 2.5 * inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=8, spaceBefore=4))

    # Overall Compliance Banner Box
    status_bg = colors.HexColor("#ECFDF5") if overall_status == "PASS" else colors.HexColor("#FEF2F2")
    status_border = colors.HexColor("#059669") if overall_status == "PASS" else colors.HexColor("#DC2626")
    status_text = f"<b>OVERALL METROLOGICAL RESULT: {overall_status}</b>"
    status_sub = "Instrument meets all tested requirements of OIML R-76-1." if overall_status == "PASS" else "Instrument has failed one or more mandatory OIML R-76-1 tolerances."

    status_table_data = [
        [
            Paragraph(status_text, badge_pass if overall_status == "PASS" else badge_fail),
            Paragraph(f"<font size=8><b>Standard:</b> OIML R-76-1:2006 (E)<br/><b>Turning Point Method:</b> {'Enabled (Small Weights)' if report_data.get('use_turning_point', True) else 'Direct Indication'}<br/>{status_sub}</font>", cell_style),
        ]
    ]
    t_status = Table(status_table_data, colWidths=[2.6 * inch, 4.9 * inch])
    t_status.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), status_bg),
        ('BOX', (0, 0), (-1, -1), 1.2, status_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_status)
    story.append(Spacer(1, 8))

    # 2. Section 1: Instrument & Metrological Identification Table
    story.append(Paragraph("1. NAWI & METROLOGICAL SPECIFICATIONS", h1_style))

    acc_class = instrument.get("accuracy_class", "III")
    acc_class_full = CLASS_NAMES.get(acc_class, acc_class)
    unit = instrument.get("unit", "kg")
    max_cap = instrument.get("max_capacity", 0.0)
    min_cap = instrument.get("min_capacity", 0.0)
    e_val = instrument.get("e", 0.0)
    d_val = instrument.get("d", e_val)
    n_div = evaluation.get("parameters", {}).get("n", 0)

    spec_data = [
        [
            Paragraph("<b>Manufacturer:</b>", cell_bold), Paragraph(str(instrument.get("manufacturer", "—")), cell_style),
            Paragraph("<b>Accuracy Class:</b>", cell_bold), Paragraph(acc_class_full, cell_bold),
        ],
        [
            Paragraph("<b>Model / Type:</b>", cell_bold), Paragraph(str(instrument.get("model", "—")), cell_style),
            Paragraph("<b>Max Capacity (Max):</b>", cell_bold), Paragraph(f"{max_cap} {unit}", cell_style),
        ],
        [
            Paragraph("<b>Serial Number:</b>", cell_bold), Paragraph(str(instrument.get("serial_no", "—")), cell_style),
            Paragraph("<b>Min Capacity (Min):</b>", cell_bold), Paragraph(f"{min_cap} {unit}", cell_style),
        ],
        [
            Paragraph("<b>Device Type:</b>", cell_bold), Paragraph(str(instrument.get("device_type", "Standard Electronic Platform")), cell_style),
            Paragraph("<b>Scale Interval (e):</b>", cell_bold), Paragraph(f"{e_val} {unit}", cell_style),
        ],
        [
            Paragraph("<b>Customer / Location:</b>", cell_bold), Paragraph(f"{report_data.get('customer_name', '—')} / {report_data.get('location', '—')}", cell_style),
            Paragraph("<b>Actual Interval (d):</b>", cell_bold), Paragraph(f"{d_val} {unit}", cell_style),
        ],
        [
            Paragraph("<b>Inspector / Verifier:</b>", cell_bold), Paragraph(str(report_data.get("inspector_name", "—")), cell_style),
            Paragraph("<b>Divisions n = Max/e:</b>", cell_bold), Paragraph(f"{n_div:,} divisions", cell_style),
        ],
    ]
    t_spec = Table(spec_data, colWidths=[1.5 * inch, 2.25 * inch, 1.5 * inch, 2.25 * inch])
    t_spec.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#F8FAFC")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_spec)
    story.append(Spacer(1, 6))

    # 3. Section 2: Environmental Conditions & Standards
    env_data = [
        [
            Paragraph("<b>Temperature:</b>", cell_bold), Paragraph(f"{environment.get('temp_c', 20.0)} °C", cell_style),
            Paragraph("<b>Humidity:</b>", cell_bold), Paragraph(f"{environment.get('humidity_pct', 50.0)} % RH", cell_style),
            Paragraph("<b>Pressure:</b>", cell_bold), Paragraph(f"{environment.get('pressure_hpa', 1013.25)} hPa", cell_style),
            Paragraph("<b>Weights Ref:</b>", cell_bold), Paragraph(f"{standards.get('standards_id', 'F1/F2')} ({standards.get('standards_cert', 'NABL/Traceable')})", cell_style),
        ]
    ]
    t_env = Table(env_data, colWidths=[0.9 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 1.0 * inch, 1.0 * inch, 1.4 * inch])
    t_env.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_env)
    story.append(Spacer(1, 8))

    # 4. Section 3: Summary of Tests Table
    story.append(Paragraph("2. SUMMARY OF METROLOGICAL EVALUATIONS (OIML R-76-1)", h1_style))
    summary_list = evaluation.get("summary", [])
    sum_data = [
        [Paragraph("OIML R-76 Clause / Evaluation Subject", cell_header), Paragraph("Requirement / Criterion", cell_header), Paragraph("Result", cell_header)]
    ]
    
    clause_notes = {
        "Instrument Metrological Limits (Table 3)": "divisions n within class range; Min capacity verified",
        "Zero Setting Accuracy (A.4.2)": "Zero error |E0| <= 0.25 e",
        "Tare Balancing & Net Weighing (A.4.6)": "Net indication corrected error <= MPE",
        "Weighing Performance & Hysteresis (A.4.4)": "Increasing & Decreasing load errors <= MPE",
        "Repeatability (A.4.10)": "Span delta (Imax - Imin) <= |MPE|",
        "Eccentricity (A.4.7)": "Errors at 5 load receptor positions <= MPE",
    }

    for item in summary_list:
        name = item.get("test", "")
        stat = item.get("status", "FAIL")
        note = clause_notes.get(name, "Conforming to OIML R-76-1")
        stat_markup = f"<font color='#059669'><b>PASS</b></font>" if stat == "PASS" else f"<font color='#DC2626'><b>{stat}</b></font>"
        sum_data.append([Paragraph(name, cell_bold), Paragraph(note, cell_style), Paragraph(stat_markup, cell_bold)])

    t_sum = Table(sum_data, colWidths=[3.2 * inch, 3.1 * inch, 1.2 * inch])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 10))

    # 5. Section 4: Detailed Test Results
    story.append(Paragraph("3. DETAILED METROLOGICAL TEST PROTOCOLS", h1_style))

    # 5.1 Zero & Tare Tests
    zero_eval = evaluation.get("zero_test", {})
    tare_eval = evaluation.get("tare_test", {})
    
    zero_tare_data = [
        [Paragraph("Test Description", cell_header), Paragraph("Nominal Load", cell_header), Paragraph("Indication", cell_header), Paragraph("Small Wt (ΔL)", cell_header), Paragraph("Error (Ec)", cell_header), Paragraph("MPE / Limit", cell_header), Paragraph("Status", cell_header)],
        [
            Paragraph("Zero Setting (A.4.2)", cell_bold),
            Paragraph(f"0.00 {unit}", cell_style),
            Paragraph(f"{zero_eval.get('zero_indication', 0.0)} {unit}", cell_style),
            Paragraph(f"{zero_eval.get('delta_l_zero', '—')} {unit}", cell_style),
            Paragraph(f"{zero_eval.get('e0', 0.0)} {unit}", cell_style),
            Paragraph(f"± {zero_eval.get('max_allowed_error', 0.0)} {unit} (0.25e)", cell_style),
            Paragraph(f"<b><font color='{'#059669' if zero_eval.get('passed') else '#DC2626'}'>{zero_eval.get('status', 'FAIL')}</font></b>", cell_style),
        ],
        [
            Paragraph("Tare Balancing (A.4.6)", cell_bold),
            Paragraph(f"{tare_eval.get('tare_load', 0.0)} {unit}", cell_style),
            Paragraph(f"{tare_eval.get('tare_indication', 0.0)} {unit}", cell_style),
            Paragraph(f"{tare_eval.get('delta_l_tare', '—')} {unit}", cell_style),
            Paragraph(f"{tare_eval.get('e_tare', 0.0)} {unit}", cell_style),
            Paragraph(f"± {round(0.25 * e_val, 4)} {unit}", cell_style),
            Paragraph(f"<b><font color='{'#059669' if tare_eval.get('tare_zero_passed') else '#DC2626'}'>{'PASS' if tare_eval.get('tare_zero_passed') else 'FAIL'}</font></b>", cell_style),
        ],
        [
            Paragraph("Tare Net Weighing (A.4.6)", cell_bold),
            Paragraph(f"Net: {tare_eval.get('net_test_load', 0.0)} {unit}", cell_style),
            Paragraph(f"{tare_eval.get('net_indication', 0.0)} {unit}", cell_style),
            Paragraph(f"{tare_eval.get('delta_l_net', '—')} {unit}", cell_style),
            Paragraph(f"{tare_eval.get('e_net_corr', 0.0)} {unit}", cell_style),
            Paragraph(f"± {tare_eval.get('mpe_net', 0.0)} {unit}", cell_style),
            Paragraph(f"<b><font color='{'#059669' if tare_eval.get('net_passed') else '#DC2626'}'>{'PASS' if tare_eval.get('net_passed') else 'FAIL'}</font></b>", cell_style),
        ],
    ]
    t_zt = Table(zero_tare_data, colWidths=[1.7 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 1.1 * inch, 0.7 * inch])
    t_zt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_zt)
    story.append(Spacer(1, 8))

    # 5.2 Eccentricity Test Table
    ecc_eval = evaluation.get("eccentricity_test", {})
    story.append(Paragraph(f"<b>Eccentricity Test (clause A.4.7) — Test Load: {ecc_eval.get('test_load', 0.0)} {unit} | MPE: ± {ecc_eval.get('mpe', 0.0)} {unit} | Max Diff: {ecc_eval.get('max_error_diff', 0.0)} {unit}</b>", cell_bold))
    story.append(Spacer(1, 2))

    ecc_data = [
        [Paragraph("Pos #", cell_header), Paragraph("Position Name / Description", cell_header), Paragraph("Indication", cell_header), Paragraph("Small Wt (ΔL)", cell_header), Paragraph("Error (E)", cell_header), Paragraph("Corrected (Ec)", cell_header), Paragraph("Status", cell_header)]
    ]
    for pt in ecc_eval.get("points", []):
        st = pt.get("status", "FAIL")
        color = "#059669" if pt.get("passed") else "#DC2626"
        ecc_data.append([
            Paragraph(str(pt.get("position_id")), cell_style),
            Paragraph(pt.get("position_name", ""), cell_style),
            Paragraph(f"{pt.get('indication')} {unit}", cell_style),
            Paragraph(f"{pt.get('delta_l', '—')} {unit}" if pt.get('delta_l') is not None else "—", cell_style),
            Paragraph(f"{pt.get('raw_error')} {unit}", cell_style),
            Paragraph(f"<b>{pt.get('corrected_error')} {unit}</b>", cell_style),
            Paragraph(f"<b><font color='{color}'>{st}</font></b>", cell_style),
        ])
    t_ecc = Table(ecc_data, colWidths=[0.6 * inch, 2.3 * inch, 1.1 * inch, 1.0 * inch, 0.9 * inch, 1.0 * inch, 0.6 * inch])
    t_ecc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_ecc)
    story.append(Spacer(1, 8))

    # 5.3 Repeatability Test Table
    rep_eval = evaluation.get("repeatability_test", {})
    story.append(Paragraph(f"<b>Repeatability Test (clause A.4.10) — Requirement: Δ = (I_max - I_min) ≤ |MPE|</b>", cell_bold))
    story.append(Spacer(1, 2))

    rep_data = [
        [Paragraph("Load Level", cell_header), Paragraph("Observed Indications (Runs 1..N)", cell_header), Paragraph("I_max", cell_header), Paragraph("I_min", cell_header), Paragraph("Spread (Δ)", cell_header), Paragraph("MPE", cell_header), Paragraph("Status", cell_header)]
    ]
    for s in rep_eval.get("series", []):
        r_str = ", ".join([f"{x:.4f}".rstrip("0").rstrip(".") for x in s.get("readings", [])])
        color = "#059669" if s.get("passed") else "#DC2626"
        rep_data.append([
            Paragraph(f"{s.get('load')} {unit}", cell_bold),
            Paragraph(r_str, cell_style),
            Paragraph(f"{s.get('i_max')} {unit}", cell_style),
            Paragraph(f"{s.get('i_min')} {unit}", cell_style),
            Paragraph(f"<b>{s.get('delta')} {unit}</b>", cell_style),
            Paragraph(f"± {s.get('mpe')} {unit}", cell_style),
            Paragraph(f"<b><font color='{color}'>{s.get('status')}</font></b>", cell_style),
        ])
    t_rep = Table(rep_data, colWidths=[1.1 * inch, 2.3 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.8 * inch, 0.6 * inch])
    t_rep.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_rep)
    story.append(Spacer(1, 8))

    # 5.4 Weighing Performance & Hysteresis Table
    weigh_eval = evaluation.get("weighing_test", {})
    story.append(Paragraph(f"<b>Weighing Performance Test (clause A.4.4) — Max Hysteresis: {weigh_eval.get('max_hysteresis', 0.0)} {unit}</b>", cell_bold))
    story.append(Spacer(1, 2))

    weigh_data = [
        [
            Paragraph("Load (L)", cell_header),
            Paragraph("I (Inc)", cell_header),
            Paragraph("Ec (Inc)", cell_header),
            Paragraph("I (Dec)", cell_header),
            Paragraph("Ec (Dec)", cell_header),
            Paragraph("Hysteresis", cell_header),
            Paragraph("MPE (±)", cell_header),
            Paragraph("Status", cell_header),
        ]
    ]

    for row in weigh_eval.get("rows", []):
        color = "#059669" if row.get("passed") else "#DC2626"
        i_dec_str = f"{row.get('i_dec')} {unit}" if row.get("i_dec") is not None else "—"
        ec_dec_str = f"{row.get('e_dec_corr')} {unit}" if row.get("e_dec_corr") is not None else "—"
        hyst_str = f"{row.get('hysteresis')} {unit}" if row.get("hysteresis") is not None else "—"

        weigh_data.append([
            Paragraph(f"{row.get('load')} {unit}", cell_bold),
            Paragraph(f"{row.get('i_inc')} {unit}", cell_style),
            Paragraph(f"<b>{row.get('e_inc_corr')}</b>", cell_style),
            Paragraph(i_dec_str, cell_style),
            Paragraph(f"<b>{ec_dec_str}</b>", cell_style),
            Paragraph(hyst_str, cell_style),
            Paragraph(f"± {row.get('mpe')} {unit}", cell_style),
            Paragraph(f"<b><font color='{color}'>{row.get('status')}</font></b>", cell_style),
        ])

    t_weigh = Table(weigh_data, colWidths=[1.1 * inch, 1.0 * inch, 0.9 * inch, 1.0 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.8 * inch])
    t_weigh.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_weigh)
    story.append(Spacer(1, 10))

    # 6. Signatures & Legal Metrology Disclaimer
    sig_block = [
        [
            Paragraph("<b>Tested / Verified By:</b><br/><br/><br/>____________________________________<br/>Technical Metrologist / Inspector", cell_style),
            Paragraph("<b>Approved / Authorized By:</b><br/><br/><br/>____________________________________<br/>Quality Manager / Signatory", cell_style),
            Paragraph(f"<b>Official Seal & Verification Date:</b><br/><br/><b>Date:</b> {test_date}<br/><b>Place:</b> {report_data.get('location', 'Metrology Center')}<br/><b>Ref:</b> {report_id}", cell_style),
        ]
    ]
    t_sig = Table(sig_block, colWidths=[2.5 * inch, 2.5 * inch, 2.5 * inch])
    t_sig.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    disclaimer_text = (
        "<b>METROLOGICAL NOTICE & STATUTORY DISCLAIMER:</b><br/>"
        "This verification test report was generated automatically by the NAWI Test Report Generation System based on "
        "computational evaluation of Non-Automatic Weighing Instruments conforming strictly to OIML R-76-1 (2006). "
        "This report is intended for college / academic prototyping, metrology software demonstrations, laboratory pre-compliance, "
        "and technical verification. Unless stamped, signed, and validated by an accredited legal metrology officer in "
        "accordance with national legislation, this report does not confer statutory legal metrology certification."
    )

    keep_elements = [
        KeepTogether([
            t_sig,
            Spacer(1, 6),
            Paragraph(disclaimer_text, disclaimer_style),
        ])
    ]
    story.extend(keep_elements)

    # Build the document
    def on_first_page(canvas_obj, doc_obj):
        canvas_obj._report_id = report_id

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=on_first_page)
    return file_path
