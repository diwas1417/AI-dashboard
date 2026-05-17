import os
import uuid

import fitz
from django.conf import settings

ABS_TEXT = "Statistics are provided by the Australian Bureau of Statistics"


def _media_url_to_path(media_url):
    """
    Convert /media/pie_charts/file.png into backend/media/pie_charts/file.png
    """

    if not media_url:
        return None

    relative_path = media_url.replace(settings.MEDIA_URL, "", 1)
    return os.path.join(settings.MEDIA_ROOT, relative_path)


def _find_abs_line_bottom_y(page):
    """
    Find the bottom Y coordinate of the ABS statistics line.
    This line appears immediately after the table.
    Everything below this line is the old image/card section.
    """

    matches = page.search_for(ABS_TEXT)

    if not matches:
        return None

    return max(rect.y1 for rect in matches)


def _cover_old_visual_area_below_abs_line(page, abs_bottom_y):
    """
    Cover only the old visual/card area below the ABS line.
    Keep the footer/date/page number untouched.
    """

    page_width = page.rect.width
    page_height = page.rect.height

    # Start just below the ABS line.
    cover_top = abs_bottom_y + 6

    # Stop above the footer so date/page number remain.
    # In this report, footer starts near the bottom around y=760+.
    cover_bottom = page_height - 70

    cover_rect = fitz.Rect(
        30,
        cover_top,
        page_width - 30,
        cover_bottom,
    )

    page.draw_rect(
        cover_rect,
        color=(1, 1, 1),
        fill=(1, 1, 1),
        overlay=True,
    )

    return cover_rect


def _insert_chart_into_visual_area(page, chart_path, visual_rect):
    """
    Insert pie chart into the cleared visual area.
    """

    if not chart_path or not os.path.exists(chart_path):
        return

    # Slight padding inside cleared area
    chart_rect = fitz.Rect(
        visual_rect.x0 + 10,
        visual_rect.y0 + 8,
        visual_rect.x1 - 10,
        visual_rect.y1 - 8,
    )

    page.insert_image(
        chart_rect,
        filename=chart_path,
        keep_proportion=True,
        overlay=True,
    )


def _replace_visual_section_after_abs_line(page, chart_path):
    """
    Main logic:
    - Find ABS line after table
    - Keep table and ABS line untouched
    - Clear only the visual/card section below it
    - Insert pie chart into that cleared space
    """

    abs_bottom_y = _find_abs_line_bottom_y(page)

    if abs_bottom_y is None:
        raise ValueError(
            "Could not find ABS statistics line on page. "
            "PDF layout may be different."
        )

    visual_rect = _cover_old_visual_area_below_abs_line(page, abs_bottom_y)
    _insert_chart_into_visual_area(page, chart_path, visual_rect)


def _renumber_footer_pages_after_deleted_page(doc, start_page_index):
    """
    Renumber only pages after a deleted page.

    Example:
    Original page 13 is deleted.
    Original page 14 becomes new page 13.
    So only pages from index 12 onward need footer update.

    start_page_index is zero-based.
    For new page 13, start_page_index = 12.
    """

    for index in range(start_page_index, len(doc)):
        page = doc[index]
        correct_page_number = index + 1
        new_page_text = f"Page {correct_page_number}"

        page_width = page.rect.width
        page_height = page.rect.height

        # Large clean footer area at bottom-right.
        # This fully removes old Page 14 / Page 15 etc.
        footer_page_rect = fitz.Rect(
            page_width - 120,
            page_height - 55,
            page_width - 15,
            page_height - 18,
        )

        page.draw_rect(
            footer_page_rect,
            color=(1, 1, 1),
            fill=(1, 1, 1),
            overlay=True,
        )

        # Write new page number in the same clean area.
        page.insert_text(
            (page_width - 70, page_height - 30),
            new_page_text,
            fontsize=7,
            fontname="helv",
            color=(0, 0, 0),
            overlay=True,
        )


def edit_suburb_statistics_pdf_with_pie_charts(pdf_file, charts):
    """
    Edit original suburb statistics PDF:
    - Page 8: replace Household Structure card/image area with pie chart
    - Page 11: replace Education card/image area with pie chart
    - Page 12: replace Occupation card/image area with pie chart
    - Page 13: remove occupation continuation page

    Important:
    The table is not touched.
    The ABS statistics line is not touched.
    The footer/date/page number is not touched.

    Page numbers below are zero-based:
    PDF page 8  = index 7
    PDF page 11 = index 10
    PDF page 12 = index 11
    PDF page 13 = index 12
    """

    edited_dir = os.path.join(settings.MEDIA_ROOT, "edited_pdfs")
    os.makedirs(edited_dir, exist_ok=True)

    filename = f"edited_suburb_statistics_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(edited_dir, filename)

    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")

    household_chart_path = _media_url_to_path(
        charts.get("household_structure_chart_url")
    )
    education_chart_path = _media_url_to_path(
        charts.get("education_by_qualification_chart_url")
    )
    occupation_chart_path = _media_url_to_path(
        charts.get("employment_by_occupation_chart_url")
    )

    # Page 8 - Household Structure
    if len(doc) > 7 and household_chart_path:
        _replace_visual_section_after_abs_line(
            doc[7],
            household_chart_path,
        )

    # Page 11 - Education By Qualification
    if len(doc) > 10 and education_chart_path:
        _replace_visual_section_after_abs_line(
            doc[10],
            education_chart_path,
        )

    # Page 12 - Employment By Occupation
    if len(doc) > 11 and occupation_chart_path:
        _replace_visual_section_after_abs_line(
            doc[11],
            occupation_chart_path,
        )

    # Remove page 13 because it only contains occupation continuation cards.
    # After the full occupation pie chart is inserted on page 12, this page is no longer needed.
    if len(doc) > 12:
        doc.delete_page(12)
    # After deleting page 13, visible footer page numbers need to be updated.
    # Example: old Page 14 becomes new Page 13.
    _renumber_footer_pages_after_deleted_page(doc, start_page_index=12)

    doc.save(output_path)
    doc.close()

    return f"{settings.MEDIA_URL}edited_pdfs/{filename}", output_path
