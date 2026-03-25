"""PDF generation for Kundli birth chart and match reports."""
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable

_STYLES = getSampleStyleSheet()
_TITLE = ParagraphStyle("KTitle", parent=_STYLES["Heading1"], fontSize=20, spaceAfter=2, textColor=colors.HexColor("#8B4513"))
_SUBTITLE = ParagraphStyle("KSub", parent=_STYLES["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#555555"), spaceAfter=8)
_H2 = ParagraphStyle("KH2", parent=_STYLES["Heading2"], fontSize=12, spaceBefore=16, spaceAfter=6, textColor=colors.HexColor("#8B4513"))
_BODY = ParagraphStyle("KBody", parent=_STYLES["Normal"], fontSize=9, leading=13)
_SMALL = ParagraphStyle("KSmall", parent=_STYLES["Normal"], fontSize=7, leading=10, textColor=colors.HexColor("#999999"))
_DOSHA_PRESENT = ParagraphStyle("KDoshaP", parent=_BODY, textColor=colors.HexColor("#cc3333"))
_DOSHA_CLEAR = ParagraphStyle("KDoshaC", parent=_BODY, textColor=colors.HexColor("#338833"))

_HDR_BG = colors.HexColor("#f5ead0")
_ROW_ALT = colors.HexColor("#faf7f0")
_GRID_CLR = colors.HexColor("#dddddd")
_ACTIVE_BG = colors.HexColor("#e8f5e0")

PLANET_EN = {
    "Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars", "Budh": "Mercury",
    "Guru": "Jupiter", "Shukra": "Venus", "Shani": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu",
}

_HR = HRFlowable(width="100%", thickness=0.5, color=_GRID_CLR, spaceAfter=6, spaceBefore=6)


def _tbl_style(rows):
    """Build table style with alternating row colors."""
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), _HDR_BG),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, _GRID_CLR),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i in range(1, rows):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), _ROW_ALT))
    return TableStyle(style)


def generate_kundli_pdf(ctx: dict) -> bytes:
    """Generate a PDF for a birth chart from stored chart context."""
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm, leftMargin=18 * mm, rightMargin=18 * mm)
    story = []

    # Header
    story.append(Paragraph("Kundli: Vedic Birth Chart", _TITLE))
    birth = ctx.get("birth_dt", "")
    loc = ctx.get("location", "")
    lagna = ctx["houses"][0]
    info_parts = []
    if birth:
        info_parts.append(f"<b>Date:</b> {birth}")
    if loc:
        info_parts.append(f"<b>Place:</b> {loc}")
    info_parts.append(f"<b>Lagna (Ascendant):</b> {lagna['sign']} {lagna['degree']:.2f}")
    story.append(Paragraph(" &nbsp;&nbsp;|&nbsp;&nbsp; ".join(info_parts), _SUBTITLE))
    story.append(_HR)

    # Planets table
    story.append(Paragraph("Planetary Positions", _H2))
    data = [["Planet", "Sign", "Degree", "Nakshatra", "Pada", ""]]
    for p in ctx["planets"]:
        retro = "Retro" if p.get("retrograde") else ""
        data.append([f"{p['planet']} ({PLANET_EN.get(p['planet'], '')})", p["sign"], f"{p['degree']:.2f}", p["nakshatra"], str(p["pada"]), retro])
    t = Table(data, colWidths=[120, 70, 45, 90, 30, 35], hAlign="LEFT", style=_tbl_style(len(data)))
    story.append(t)

    # Houses table
    story.append(Paragraph("House Cusps", _H2))
    data = [["House", "Sign", "Degree"]]
    for h in ctx["houses"]:
        label = f"{h['house']}  (Ascendant)" if h["house"] == 1 else str(h["house"])
        data.append([label, h["sign"], f"{h['degree']:.2f}"])
    t = Table(data, colWidths=[100, 100, 60], hAlign="LEFT", style=_tbl_style(len(data)))
    story.append(t)

    # Yogas
    yogas = ctx.get("yogas", [])
    if yogas:
        story.append(Paragraph("Yogas (Planetary Combinations)", _H2))
        for y in yogas:
            story.append(Paragraph(f"<b>{y['name']}</b>: {y['desc']}", _BODY))
            story.append(Spacer(1, 3))

    # Doshas
    doshas = ctx.get("doshas", [])
    if doshas:
        story.append(Paragraph("Doshas", _H2))
        for d in doshas:
            style = _DOSHA_PRESENT if d["present"] else _DOSHA_CLEAR
            icon = "Present" if d["present"] else "Not present"
            story.append(Paragraph(f"<b>{d['name']}</b>: {icon}. {d['detail']}", style))
            story.append(Spacer(1, 3))

    # Dasha timeline
    story.append(Paragraph("Vimshottari Dasha (Planetary Periods)", _H2))
    data = [["Period Lord", "Start Date", "End Date", "Duration"]]
    now = datetime.now()
    active_rows = []
    for i, d in enumerate(ctx["dashas"]):
        data.append([f"{d['lord']} ({PLANET_EN.get(d['lord'], '')})", d["start"].strftime("%d %b %Y"), d["end"].strftime("%d %b %Y"), f"{d['years']} years"])
        if d["start"] <= now <= d["end"]:
            active_rows.append(i + 1)
    style = _tbl_style(len(data))
    for row in active_rows:
        style.add("BACKGROUND", (0, row), (-1, row), _ACTIVE_BG)
        style.add("FONT", (0, row), (-1, row), "Helvetica-Bold")
    t = Table(data, colWidths=[120, 80, 80, 60], hAlign="LEFT", style=style)
    story.append(t)

    # Footer
    story.append(Spacer(1, 20))
    story.append(_HR)
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y')} by Kundli. Calculations powered by Swiss Ephemeris.", _SMALL))

    doc.build(story)
    return buf.getvalue()


def generate_match_pdf(result: dict, people: list) -> bytes:
    """Generate a PDF for Ashtakoota match result."""
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm, leftMargin=18 * mm, rightMargin=18 * mm)
    story = []

    story.append(Paragraph("Kundli Match: Ashtakoota Gun Milan", _TITLE))
    story.append(Paragraph(
        f"<b>{people[0]['name']}</b> ({people[0]['moon_sign']} / {people[0]['nakshatra']}) &nbsp; and &nbsp; "
        f"<b>{people[1]['name']}</b> ({people[1]['moon_sign']} / {people[1]['nakshatra']})", _SUBTITLE))
    story.append(_HR)

    # Score and verdict
    total = result["total"]
    if total >= 32:
        verdict = "Excellent match"
    elif total >= 24:
        verdict = "Good match, recommended"
    elif total >= 18:
        verdict = "Average, proceed with caution"
    else:
        verdict = "Not recommended"
    story.append(Paragraph(f"<b>Compatibility Score: {total} / {result['max']}</b> ({int(total / result['max'] * 100)}%)", _BODY))
    story.append(Paragraph(f"<b>Verdict:</b> {verdict}", _BODY))
    story.append(Spacer(1, 8))

    # Koota table
    story.append(Paragraph("Koota Breakdown", _H2))
    data = [["Koota", "What it measures", people[0]["name"], people[1]["name"], "Score"]]
    for k in result["kootas"]:
        data.append([k["name"], k["description"], k["boy"], k["girl"], f"{k['score']}/{k['max']}"])
    data.append(["Total", "", "", "", f"{result['total']}/{result['max']}"])
    style = _tbl_style(len(data))
    # Highlight zero scores in red
    for i, k in enumerate(result["kootas"], 1):
        if k["score"] == 0:
            style.add("TEXTCOLOR", (0, i), (-1, i), colors.HexColor("#cc3333"))
    # Bold total row
    style.add("FONT", (0, len(data) - 1), (-1, len(data) - 1), "Helvetica-Bold")
    style.add("BACKGROUND", (0, len(data) - 1), (-1, len(data) - 1), _HDR_BG)
    t = Table(data, colWidths=[55, 95, 65, 65, 40], hAlign="LEFT", style=style)
    story.append(t)

    # Doshas
    warnings = []
    nadi = result["kootas"][7]
    bhakoot = result["kootas"][6]
    if nadi["score"] == 0:
        warnings.append(f"<b>Nadi Dosha:</b> Both have {nadi['boy']} Nadi. Same Nadi may indicate health concerns in offspring.")
    if bhakoot["score"] == 0:
        warnings.append(f"<b>Bhakoot Dosha:</b> {bhakoot['boy']} and {bhakoot['girl']} are in an unfavorable axis. May indicate challenges in health or finances.")
    for p in people:
        if p.get("manglik"):
            warnings.append(f"<b>Manglik Dosha:</b> {p['name']} has Mars in House {p.get('mars_house')}.")
    if warnings:
        story.append(Paragraph("Doshas and Considerations", _H2))
        for w in warnings:
            story.append(Paragraph(w, _DOSHA_PRESENT))
            story.append(Spacer(1, 3))

    # Footer
    story.append(Spacer(1, 20))
    story.append(_HR)
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y')} by Kundli. Calculations powered by Swiss Ephemeris.", _SMALL))

    doc.build(story)
    return buf.getvalue()
