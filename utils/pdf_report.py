"""
PDF report generator.

Uses ReportLab (pure Python, no system binaries) so this runs on any SME
laptop or cloud container. No headless-Chrome or weasyprint dependency.

Report structure is aligned to the TNFD LEAP phases plus the Nature Positive
state-of-nature pillars and a financial-materiality page. The first page is
narrative-first, because the TNFD consultation feedback explicitly asked for a
"story that a high-schooler can read."
"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    )
    _REPORTLAB_OK = True
except ImportError:  # pragma: no cover
    _REPORTLAB_OK = False


BRAND_GREEN = colors.HexColor("#1f8f5f") if _REPORTLAB_OK else None
BRAND_DEEP  = colors.HexColor("#0f5c3d") if _REPORTLAB_OK else None
INK         = colors.HexColor("#0f172a") if _REPORTLAB_OK else None
MUTE        = colors.HexColor("#64748b") if _REPORTLAB_OK else None
HAIRLINE    = colors.HexColor("#e2e8f0") if _REPORTLAB_OK else None


def _styles():
    ss = getSampleStyleSheet()
    base = ss["BodyText"]
    base.textColor = INK
    base.leading = 15
    return {
        "title": ParagraphStyle("Title", parent=ss["Title"], textColor=BRAND_DEEP, fontSize=24, leading=28, spaceAfter=8),
        "eyebrow": ParagraphStyle("Eyebrow", parent=base, textColor=BRAND_GREEN, fontSize=9, leading=11, spaceAfter=2, fontName="Helvetica-Bold"),
        "h2":    ParagraphStyle("H2", parent=ss["Heading2"], textColor=BRAND_DEEP, fontSize=16, leading=20, spaceBefore=14, spaceAfter=6),
        "h3":    ParagraphStyle("H3", parent=ss["Heading3"], textColor=INK, fontSize=13, leading=16, spaceBefore=10, spaceAfter=4),
        "body":  base,
        "lede":  ParagraphStyle("Lede", parent=base, fontSize=12.5, leading=18, spaceAfter=8, textColor=INK),
        "small": ParagraphStyle("Small", parent=base, fontSize=8.5, leading=11, textColor=MUTE),
    }


def _kv_table(rows: list[tuple[str, str]]) -> Table:
    t = Table([[k, v] for k, v in rows], colWidths=[5.2 * cm, 10.8 * cm])
    t.setStyle(TableStyle([
        ("FONT",       (0, 0), (-1, -1), "Helvetica", 10),
        ("TEXTCOLOR",  (0, 0), (0, -1),  MUTE),
        ("TEXTCOLOR",  (1, 0), (1, -1),  INK),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("BOX",        (0, 0), (-1, -1), 0.25, HAIRLINE),
        ("INNERGRID",  (0, 0), (-1, -1), 0.25, HAIRLINE),
        ("BACKGROUND", (0, 0), (0, -1),  colors.HexColor("#f8fafc")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    return t


def _matrix_table(title: str, rows: list[Any]) -> list:
    if not rows:
        return []
    data = [["Service / Pressure", "Rating", "Why it matters"]]
    for r in rows:
        data.append([r.service, r.rating, r.why])
    t = Table(data, colWidths=[4.6 * cm, 1.8 * cm, 9.6 * cm])
    t.setStyle(TableStyle([
        ("FONT",       (0, 0), (-1, 0),  "Helvetica-Bold", 10),
        ("TEXTCOLOR",  (0, 0), (-1, 0),  colors.white),
        ("BACKGROUND", (0, 0), (-1, 0),  BRAND_GREEN),
        ("FONT",       (0, 1), (-1, -1), "Helvetica", 9.5),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("GRID",       (0, 0), (-1, -1), 0.25, HAIRLINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("LEFTPADDING",  (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    return [Paragraph(title, _styles()["h3"]), Spacer(1, 4), t, Spacer(1, 8)]


def build_pdf_report(
    *,
    site_name: str,
    sector: str,
    story: dict,
    metrics: dict,
    financial: dict,
    risk: dict,
    tnfd_matrix: dict,
    nature_positive: list[dict],
    datasets: list[dict],
    watermark: str | None = None,
) -> BytesIO:
    """Return a BytesIO containing the PDF report."""
    if not _REPORTLAB_OK:  # pragma: no cover
        raise RuntimeError(
            "reportlab is required for PDF export. Add 'reportlab' to requirements.txt."
        )

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=1.8 * cm, bottomMargin=1.6 * cm,
        title=f"EagleNatureInsight report — {site_name}",
    )
    st = _styles()
    story_el: list = []

    # ---- Cover ----
    story_el += [
        Paragraph("EAGLENATUREINSIGHT · NATURE INTELLIGENCE REPORT", st["eyebrow"]),
        Paragraph(site_name, st["title"]),
        Paragraph(
            f"Sector: {sector} · Generated {datetime.now().strftime('%d %b %Y')} · "
            "TNFD LEAP-aligned · Nature Positive metric set",
            st["small"],
        ),
        Spacer(1, 10),
        Paragraph("In one sentence", st["eyebrow"]),
        Paragraph(story.get("headline", ""), st["lede"]),
        Spacer(1, 2),
        Paragraph(story.get("opener", ""), st["body"]),
    ]

    # ---- Bottom line (currency) ----
    story_el += [
        Spacer(1, 6),
        Paragraph("The bottom line", st["h2"]),
        Paragraph(story.get("bottom_line", ""), st["body"]),
        Spacer(1, 6),
        _kv_table([
            ("Assumed annual revenue", f"${financial.get('revenue_usd', 0):,.0f}"),
            ("Downside — nature risk", f"${financial.get('downside_usd', 0):,.0f}  ({financial.get('downside_pct', 0):.1f}% of revenue)"),
            ("Upside — nature opportunity", f"${financial.get('upside_usd', 0):,.0f}  ({financial.get('upside_pct', 0):.1f}% of revenue)"),
            ("Net position", f"${abs(financial.get('net_usd', 0)):,.0f} " + ("of risk" if financial.get('net_usd', 0) > 0 else "of upside")),
        ]),
    ]

    # ---- LEAP / Evaluate ----
    story_el += [PageBreak(), Paragraph("EVALUATE · Dependencies", st["eyebrow"]),
                 Paragraph("What nature gives you", st["h2"])]
    for d in story.get("dependencies", []):
        story_el.append(Paragraph("• " + d, st["body"]))

    story_el += _matrix_table("TNFD ecosystem-service dependencies", tnfd_matrix.get("dependencies", []))

    story_el += [Spacer(1, 8),
                 Paragraph("EVALUATE · Impacts", st["eyebrow"]),
                 Paragraph("What your business changes about nature", st["h2"])]
    for d in story.get("impacts", []):
        story_el.append(Paragraph("• " + d, st["body"]))
    story_el += _matrix_table("TNFD pressure categories", tnfd_matrix.get("impacts", []))

    # ---- Assess ----
    story_el += [PageBreak(),
                 Paragraph("ASSESS · Risks and opportunities", st["eyebrow"]),
                 Paragraph("Prioritised flags", st["h2"])]
    items = risk.get("structured", []) or []
    if items:
        data = [["Type", "Flag", "What to do"]]
        for it in items:
            data.append([it.get("kind", ""), it.get("title", ""), it.get("rec", "")])
        t = Table(data, colWidths=[2.4 * cm, 5.0 * cm, 8.6 * cm])
        t.setStyle(TableStyle([
            ("FONT",       (0, 0), (-1, 0), "Helvetica-Bold", 10),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_DEEP),
            ("FONT",       (0, 1), (-1, -1), "Helvetica", 9.5),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
            ("GRID",       (0, 0), (-1, -1), 0.25, HAIRLINE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("LEFTPADDING",  (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ]))
        story_el.append(t)

    # ---- Nature Positive pillars ----
    story_el += [PageBreak(),
                 Paragraph("NATURE POSITIVE · State-of-nature pillars", st["eyebrow"]),
                 Paragraph("Extent · Condition · Species · Sensitive places", st["h2"]),
                 Paragraph("We report the pillars defined by the Nature Positive Initiative (Jan 2025 draft). Each indicator is measured in a transparent unit of nature and paired with a plain-English explanation.", st["body"])]
    data = [["Pillar", "Indicator", "Value", "Plain meaning"]]
    for n in nature_positive:
        val = metrics.get(n.get("key", "")) if n.get("key") else "—"
        try:
            val_str = f"{float(val):.2f}" if isinstance(val, (int, float)) else str(val)
        except Exception:
            val_str = str(val)
        data.append([n.get("pillar", ""), n.get("indicator", ""), val_str, n.get("plain", "")])
    t = Table(data, colWidths=[3.2 * cm, 4.2 * cm, 2.4 * cm, 6.2 * cm])
    t.setStyle(TableStyle([
        ("FONT",       (0, 0), (-1, 0), "Helvetica-Bold", 10),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_GREEN),
        ("FONT",       (0, 1), (-1, -1), "Helvetica", 9),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("GRID",       (0, 0), (-1, -1), 0.25, HAIRLINE),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    story_el.append(t)

    # ---- Prepare / Next steps ----
    story_el += [PageBreak(),
                 Paragraph("PREPARE · Your next moves", st["eyebrow"]),
                 Paragraph("What to do in the next 30 / 90 / 365 days", st["h2"])]
    for rec in risk.get("recs", [])[:10]:
        story_el.append(Paragraph("• " + rec, st["body"]))

    # ---- Data sources / limitations ----
    story_el += [PageBreak(),
                 Paragraph("APPENDIX · Data sources & limitations", st["eyebrow"]),
                 Paragraph("Every figure above traces back here.", st["h2"]),
                 Paragraph("Simplifications, proxies and scope boundaries are disclosed for every layer. Report generated in full alignment with TNFD Recommendation D1 on transparency.", st["small"])]
    for ds in datasets:
        row = [
            Paragraph(f"<b>{ds.get('layer', '')}</b>  —  <font color='#64748b'>{ds.get('source', '')}</font>", st["body"]),
            Paragraph(
                f"Resolution: {ds.get('resolution', '—')} · "
                f"Cadence: {ds.get('update_cadence', '—')} · "
                f"Units: {ds.get('units_of_nature', '—')}",
                st["small"],
            ),
            Paragraph(f"<i>{ds.get('limits', '')}</i>", st["small"]),
            Spacer(1, 6),
        ]
        story_el.extend(row)

    # ---- Watermark / footer ----
    def _draw_footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTE)
        canvas.drawString(1.8 * cm, 1 * cm, "EagleNatureInsight · TNFD LEAP-aligned nature intelligence · Space Eagle Enterprise")
        canvas.drawRightString(19 * cm, 1 * cm, f"Page {_doc.page}")
        if watermark:
            canvas.saveState()
            canvas.setFillColor(colors.HexColor("#e2e8f0"))
            canvas.setFont("Helvetica-Bold", 56)
            canvas.translate(10.5 * cm, 14 * cm)
            canvas.rotate(35)
            canvas.drawCentredString(0, 0, watermark)
            canvas.restoreState()
        canvas.restoreState()

    doc.build(story_el, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    buf.seek(0)
    return buf
