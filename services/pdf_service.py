import re
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def create_pdf(report_text):

    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    filename = (
        f"procurement_report_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    filepath = reports_dir / filename

    # =========================================================
    # DOCUMENT
    # =========================================================

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Energy Procurement Strategy Report",
        author="Energy Supply Chain AI System",
    )

    # =========================================================
    # STYLES
    # =========================================================

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    date_style = ParagraphStyle(
        "ReportDate",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        spaceAfter=18,
    )

    h1_style = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Heading1"],
        fontSize=15,
        leading=19,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-7,
        spaceAfter=4,
    )

    # =========================================================
    # HELPERS
    # =========================================================

    def escape_text(text):
        if text is None:
            return ""

        text = str(text)

        # Remove LaTeX formatting
        text = text.replace("$$", "")
        text = text.replace("$", "")
        text = text.replace(r"\text{", "")
        text = text.replace(r"\mathbf{", "")
        text = text.replace(r"\textbf{", "")
        text = text.replace(r"\times", "×")
        text = text.replace(r"\,", "")
        text = text.replace(r"\!", "")
        text = text.replace(r"\;", "")
        text = text.replace(r"\:", "")
        text = text.replace(r"\$", "$")

        # Remove remaining LaTeX closing braces
        text = text.replace("}", "")

        # Escape HTML characters for ReportLab
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")

        return text

    def markdown_to_reportlab(text):
        """
        Convert basic Markdown and simple LaTeX formatting
        into ReportLab-compatible text.
        """

        if text is None:
            return ""

        text = str(text)

        # =====================================================
        # CONVERT SIMPLE LATEX TO NORMAL TEXT
        # =====================================================

        # Remove display-math markers
        text = text.replace("$$", "")
        text = text.replace("$", "")

        # \text{barrels} -> barrels
        text = re.sub(
            r"\\text\{([^{}]*)\}",
            r"\1",
            text,
        )

        # \mathbf{120,000,000} -> 120,000,000
        text = re.sub(
            r"\\mathbf\{([^{}]*)\}",
            r"\1",
            text,
        )

        # \textbf{something} -> something
        text = re.sub(
            r"\\textbf\{([^{}]*)\}",
            r"\1",
            text,
        )

        # LaTeX multiplication
        text = text.replace(r"\times", "×")

        # Escaped dollar sign
        text = text.replace(r"\$", "$")

        # LaTeX spacing commands
        text = text.replace(r"\,", " ")
        text = text.replace(r"\;", " ")
        text = text.replace(r"\:", " ")
        text = text.replace(r"\ ", " ")

        # Remove remaining simple LaTeX commands
        text = re.sub(
            r"\\[a-zA-Z]+",
            "",
            text,
        )

        # =====================================================
        # ESCAPE REPORTLAB SPECIAL CHARACTERS
        # =====================================================

        text = escape_text(text)

        # =====================================================
        # MARKDOWN BOLD
        # =====================================================

        text = re.sub(
            r"\*\*(.+?)\*\*",
            r"<b>\1</b>",
            text,
        )

        # =====================================================
        # MARKDOWN ITALIC
        # =====================================================

        text = re.sub(
            r"(?<!\*)\*([^\*]+?)\*(?!\*)",
            r"<i>\1</i>",
            text,
        )

        # =====================================================
        # INLINE CODE
        # =====================================================

        text = re.sub(
            r"`([^`]+)`",
            r"<font name='Courier'>\1</font>",
            text,
        )

        return text

    def add_page_number(canvas, doc):
        canvas.saveState()

        canvas.setFont("Helvetica", 8)

        page_number = canvas.getPageNumber()

        canvas.drawCentredString(
            A4[0] / 2,
            10 * mm,
            f"Page {page_number}",
        )

        canvas.restoreState()

    # =========================================================
    # STORY
    # =========================================================

    story = []

    # Report title
    story.append(
        Paragraph(
            "Energy Procurement Strategy Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            datetime.now().strftime("%d %B %Y %H:%M"),
            date_style,
        )
    )

    # =========================================================
    # PARSE GEMINI REPORT
    # =========================================================

    lines = report_text.splitlines()

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        # -----------------------------------------------------
        # Empty line
        # -----------------------------------------------------

        if not line:
            story.append(Spacer(1, 4))
            i += 1
            continue

        # -----------------------------------------------------
        # Markdown horizontal rule
        # -----------------------------------------------------

        if re.match(r"^---+$", line):
            story.append(Spacer(1, 5))
            i += 1
            continue

        # -----------------------------------------------------
        # Markdown H1
        # -----------------------------------------------------

        if line.startswith("# ") and not line.startswith("## "):

            text = line[2:].strip()

            story.append(
                Paragraph(
                    markdown_to_reportlab(text),
                    h1_style,
                )
            )

            i += 1
            continue

        # -----------------------------------------------------
        # Markdown H2
        # -----------------------------------------------------

        if line.startswith("## "):

            text = line[3:].strip()

            story.append(
                Paragraph(
                    markdown_to_reportlab(text),
                    h1_style,
                )
            )

            i += 1
            continue

        # -----------------------------------------------------
        # Markdown H3
        # -----------------------------------------------------

        if line.startswith("### "):

            text = line[4:].strip()

            story.append(
                Paragraph(
                    markdown_to_reportlab(text),
                    h2_style,
                )
            )

            i += 1
            continue

        # -----------------------------------------------------
        # Bullet point
        # -----------------------------------------------------

        if line.startswith("* ") or line.startswith("- "):

            text = line[2:].strip()

            story.append(
                Paragraph(
                    "• " + markdown_to_reportlab(text),
                    bullet_style,
                )
            )

            i += 1
            continue

        # -----------------------------------------------------
        # Numbered list
        # -----------------------------------------------------

        if re.match(r"^\d+\.\s+", line):

            match = re.match(
                r"^(\d+)\.\s+(.*)",
                line,
            )

            if match:

                number = match.group(1)
                text = match.group(2)

                story.append(
                    Paragraph(
                        f"<b>{number}.</b> "
                        f"{markdown_to_reportlab(text)}",
                        body_style,
                    )
                )

                i += 1
                continue

        # -----------------------------------------------------
        # Markdown table
        # -----------------------------------------------------

        if line.startswith("|"):

            table_lines = []

            while (
                i < len(lines)
                and lines[i].strip().startswith("|")
            ):

                current = lines[i].strip()

                # Ignore Markdown separator row
                if not re.match(
                    r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$",
                    current,
                ):
                    table_lines.append(current)

                i += 1

            if table_lines:

                table_data = []

                for row in table_lines:

                    cells = [
                        cell.strip()
                        for cell in row.strip("|").split("|")
                    ]

                    table_data.append(cells)

                # Convert table cells to Paragraphs
                formatted_table = []

                for row_index, row in enumerate(table_data):

                    formatted_row = []

                    for cell in row:

                        cell_style = body_style

                        if row_index == 0:
                            cell_style = ParagraphStyle(
                                "TableHeader",
                                parent=body_style,
                                fontSize=8,
                                leading=10,
                            )

                        formatted_row.append(
                            Paragraph(
                                markdown_to_reportlab(cell),
                                cell_style,
                            )
                        )

                    formatted_table.append(formatted_row)

                # Calculate useful column width
                page_width = (
                    A4[0]
                    - doc.leftMargin
                    - doc.rightMargin
                )

                column_count = len(formatted_table[0])

                col_width = page_width / column_count

                table = Table(
                    formatted_table,
                    colWidths=[col_width] * column_count,
                    repeatRows=1,
                    hAlign="LEFT",
                )

                table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, 0),
                                colors.HexColor("#E8EEF7"),
                            ),
                            (
                                "TEXTCOLOR",
                                (0, 0),
                                (-1, 0),
                                colors.black,
                            ),
                            (
                                "FONTNAME",
                                (0, 0),
                                (-1, 0),
                                "Helvetica-Bold",
                            ),
                            (
                                "GRID",
                                (0, 0),
                                (-1, -1),
                                0.5,
                                colors.grey,
                            ),
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP",
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                        ]
                    )
                )

                story.append(Spacer(1, 6))
                story.append(table)
                story.append(Spacer(1, 8))

            continue

        # -----------------------------------------------------
        # Normal paragraph
        # -----------------------------------------------------

        story.append(
            Paragraph(
                markdown_to_reportlab(line),
                body_style,
            )
        )

        i += 1

    # =========================================================
    # BUILD PDF
    # =========================================================

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return str(filepath)