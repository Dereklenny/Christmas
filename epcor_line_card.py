#!/usr/bin/env python3
"""Generate a one-page EPCOR line card PDF."""

import glob
import os
from math import ceil
from typing import List

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    KeepInFrame,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def scale_to_box(img_path, box_w, box_h):
    """Return an RLImage scaled to fit inside ``box_w`` x ``box_h``."""
    try:
        with PILImage.open(img_path) as im:
            iw, ih = im.size
        ratio = min(box_w / float(iw), box_h / float(ih))
        width, height = max(1, iw * ratio), max(1, ih * ratio)
        return RLImage(img_path, width=width, height=height)
    except Exception:  # pragma: no cover - safety fallback
        return RLImage(img_path, width=box_w, height=box_h)


def logo_grid_5cols_even_sized(
    images,
    cols=5,
    max_rows=5,
    cell_w=1.45 * inch,
    cell_h=0.70 * inch,
    pad_x=6,
    pad_y=4,
):
    """Create a logo grid with a centred final row."""

    if not images:
        return None

    images = images[: cols * max_rows]
    total = len(images)
    rows = ceil(total / cols)

    data = []
    idx = 0
    for row_index in range(rows):
        remaining = total - idx
        take = min(cols, remaining)

        if row_index == rows - 1 and take < cols:
            left_pad = (cols - take) // 2
            right_pad = cols - take - left_pad
        else:
            left_pad = right_pad = 0

        row = []
        for _ in range(left_pad):
            row.append(Spacer(1, cell_h - 2 * pad_y))

        for _ in range(take):
            path = images[idx]
            idx += 1
            row.append(scale_to_box(path, cell_w - 2 * pad_x, cell_h - 2 * pad_y))

        for _ in range(right_pad):
            row.append(Spacer(1, cell_h - 2 * pad_y))

        data.append(row)

    table = Table(
        data,
        colWidths=[cell_w] * cols,
        hAlign="CENTER",
        spaceBefore=6,
        spaceAfter=6,
    )
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), pad_x),
                ("RIGHTPADDING", (0, 0), (-1, -1), pad_x),
                ("TOPPADDING", (0, 0), (-1, -1), pad_y),
                ("BOTTOMPADDING", (0, 0), (-1, -1), pad_y),
            ]
        )
    )
    return table


BASE_DIR = "/Users/alexwu/Downloads/LineCard"
LOGO_PATH = os.path.join(BASE_DIR, "EPCOR/logo with full name.png")
SHAREPOINT_IMG_DIR = os.path.join(BASE_DIR, "logos")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
OUTFILE = os.path.join(BASE_DIR, "EPCOR_Line_Card_OnePage.pdf")


def register_inter_fonts(fonts_dir: str):
    """Register Inter fonts when available, otherwise fall back to Helvetica."""

    regular = os.path.join(fonts_dir, "Inter-Regular.ttf")
    bold = os.path.join(fonts_dir, "Inter-Bold.ttf")

    if os.path.isfile(regular) and os.path.isfile(bold):
        pdfmetrics.registerFont(TTFont("Inter", regular))
        pdfmetrics.registerFont(TTFont("Inter-Bold", bold))
        return "Inter", "Inter-Bold"

    return "Helvetica", "Helvetica-Bold"


BASE_FONT, BOLD_FONT = register_inter_fonts(FONTS_DIR)

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="H1",
        parent=styles["Normal"],
        fontName=BOLD_FONT,
        fontSize=24,
        leading=28,
        spaceAfter=6,
        textColor=colors.HexColor("#0E1B2A"),
    )
)
styles.add(
    ParagraphStyle(
        name="H1Center",
        parent=styles["Normal"],
        fontName=BOLD_FONT,
        fontSize=24,
        leading=28,
        alignment=1,
        spaceAfter=6,
        textColor=colors.HexColor("#0E1B2A"),
    )
)
styles.add(
    ParagraphStyle(
        name="H2",
        parent=styles["Normal"],
        fontName=BOLD_FONT,
        fontSize=14,
        leading=18,
        spaceBefore=8,
        spaceAfter=5,
        textColor=colors.HexColor("#1F2937"),
    )
)
styles.add(
    ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontName=BASE_FONT,
        fontSize=11,
        leading=14.5,
        spaceAfter=2,
        textColor=colors.HexColor("#111827"),
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["Normal"],
        fontName=BASE_FONT,
        fontSize=9.2,
        leading=12,
        textColor=colors.HexColor("#374151"),
    )
)
styles.add(
    ParagraphStyle(
        name="Footer",
        parent=styles["Normal"],
        alignment=1,
        fontName=BASE_FONT,
        fontSize=9.6,
        leading=12,
        textColor=colors.HexColor("#374151"),
    )
)

COMPANY_INTRO = (
    "EPCOR Building Supply is a leading Canadian manufacturer and distributor of concrete "
    "form hardware, accessories, and building-envelope solutions. We specialize in Division "
    "3 (Concrete) and Division 7 (Thermal & Moisture Protection), pairing trusted global "
    "brands with in-house manufacturing and technical support. With deep inventory and "
    "next-day delivery in many regions, EPCOR delivers reliable materials, informed service, "
    "and project-ready solutions."
)

DIV3_POINTS = [
    "Forming hardware & accessories (ties, wedges, stakes, release agents)",
    "Concrete repair & grouts (mortars, epoxies, bonding agents)",
    "Admixtures & chemicals (retarders, accelerators, superplasticizers)",
    "Curing & sealing compounds; surface sealers",
    "Reinforcement accessories (rebar ties, chairs, dowels)",
]

DIV7_POINTS = [
    "Waterproofing membranes (sheet & fluid-applied)",
    "Air & vapor barrier systems; flashing",
    "Sealants & joint fillers",
    "Expansion joints & waterstops",
    "Insulation & winter protection (spray foam, curing blankets, tarps)",
]


def bullets(style, items):
    """Render bullet paragraphs for ``items`` using the provided style."""

    return [Paragraph("• " + text, style) for text in items]


def find_images(root_dir: str, limit=25) -> List[str]:
    """Discover unique PNG/JPG images under ``root_dir`` up to ``limit`` entries."""

    root_dir = os.path.abspath(os.path.expanduser(root_dir))
    if not os.path.isdir(root_dir):
        return []

    matches = []
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        matches.extend(glob.glob(os.path.join(root_dir, "**", ext), recursive=True))

    seen = set()
    unique = []
    for file_path in sorted(matches):
        name = os.path.basename(file_path).lower()
        if name not in seen:
            seen.add(name)
            unique.append(file_path)

    return unique[:limit]


def scaled_logo(path: str, target_w=4.2 * inch, max_h=1.5 * inch) -> RLImage:
    """Scale the header logo without stretching."""

    with PILImage.open(path) as image:
        width, height = image.size
    ratio = min(target_w / float(width), max_h / float(height))
    return RLImage(path, width=width * ratio, height=height * ratio)


def main():
    doc = SimpleDocTemplate(
        OUTFILE,
        pagesize=letter,
        leftMargin=30,
        rightMargin=30,
        topMargin=26,
        bottomMargin=26,
    )
    story = []

    if LOGO_PATH and os.path.isfile(LOGO_PATH):
        try:
            story.append(scaled_logo(LOGO_PATH, target_w=4.2 * inch, max_h=1.5 * inch))
            story.append(Spacer(1, 6))
        except Exception as exc:  # pragma: no cover - safety fallback
            print("[header] logo resize failed:", exc)
            story.append(Paragraph("EPCOR Building Supply", styles["H1"]))
    else:
        story.append(Paragraph("EPCOR Building Supply", styles["H1"]))

    story.append(Paragraph("Concrete & Moisture Protection", styles["H1Center"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1f2937")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(COMPANY_INTRO, styles["Body"]))
    story.append(Spacer(1, 10))

    usable_width = letter[0] - (doc.leftMargin + doc.rightMargin)
    left_col = [Paragraph("Division 3 — Concrete", styles["H2"])] + bullets(
        styles["Body"], DIV3_POINTS
    )
    right_col = [Paragraph("Division 7 — Thermal & Moisture Protection", styles["H2"])] + bullets(
        styles["Body"], DIV7_POINTS
    )

    cols_table = Table([[left_col, right_col]], colWidths=[usable_width / 2, usable_width / 2])
    cols_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(cols_table)
    story.append(Spacer(1, 8))

    logos = find_images(SHAREPOINT_IMG_DIR, limit=25)
    story.append(Paragraph("Featured Brand Partners", styles["H2"]))

    grid = logo_grid_5cols_even_sized(
        logos,
        cols=5,
        max_rows=5,
        cell_w=1.45 * inch,
        cell_h=0.70 * inch,
        pad_x=6,
        pad_y=4,
    )
    if grid:
        usable_width = letter[0] - (doc.leftMargin + doc.rightMargin)
        wrapped_grid = KeepInFrame(
            width=usable_width,
            height=5.0 * inch,
            content=[grid],
            mode="shrink",
        )
        story.append(wrapped_grid)
    else:
        story.append(
            Paragraph(f"No logos found in: {SHAREPOINT_IMG_DIR}", styles["Small"])
        )

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 2))
    story.append(
        Paragraph(
            "www.epcorsupply.com   •   epcor_info@epcorsupply.com  •  (647) 674-7682",
            styles["Footer"],
        )
    )

    doc.build(story)
    print(f"\nBuilt {OUTFILE}")
    print(
        f"Fonts used: {BASE_FONT}/{BOLD_FONT} (custom={'yes' if BASE_FONT != 'Helvetica' else 'no'})"
    )
    print(
        f"Logo path: {LOGO_PATH}  |  Logos in grid: {len(logos)} from {SHAREPOINT_IMG_DIR}"
    )


if __name__ == "__main__":
    main()

