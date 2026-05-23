import os
import uuid
import numpy as np

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgb
from django.conf import settings

# Smooth continuous score gradient
SCORE_CMAP = LinearSegmentedColormap.from_list(
    "score_gradient",
    [
        "#D7191C",  # red
        "#F07C19",  # orange
        "#F4D21F",  # yellow
        "#8BC34A",  # light green
        "#168A3A",  # dark green
    ],
)

SCORE_NORM = Normalize(vmin=0, vmax=10)


def score_to_color(score):
    """
    Returns a smooth colour based on score from 0 to 10.
    """
    return SCORE_CMAP(SCORE_NORM(score))


def lighten_color(color, amount=0.35):
    """
    Lighten an RGBA or RGB colour by blending toward white.
    amount = 0 means original colour
    amount = 1 means fully white
    """
    r, g, b = to_rgb(color)
    r = r + (1 - r) * amount
    g = g + (1 - g) * amount
    b = b + (1 - b) * amount
    return (r, g, b)


def draw_gradient_rect(ax, x, y, w, h, left_color, right_color, zorder=1):
    """
    Draw a horizontal gradient rectangle.
    """
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list("custom_grad", [left_color, right_color])

    ax.imshow(
        gradient,
        extent=(x, x + w, y, y + h),
        origin="lower",
        cmap=cmap,
        aspect="auto",
        zorder=zorder,
    )


def get_summary_text(total_score):
    if total_score >= 90:
        return "Outstanding suburb with excellent amenity strength"
    if total_score >= 80:
        return "Very strong suburb with broad amenity advantages"
    if total_score >= 70:
        return "Strong family-oriented suburb with growing infrastructure"
    if total_score >= 55:
        return "Moderate suburb with acceptable amenity access"
    if total_score >= 40:
        return "Below average suburb with some amenity gaps"
    return "Weak suburb with limited amenity access"


def shorten_reason(reason):
    if " because " in reason:
        reason = reason.split(" because ", 1)[1]

    reason = reason.replace("approximately ", "")
    reason = reason.replace("option(s)", "options")
    reason = reason.replace("store(s)", "stores")

    if len(reason) > 90:
        return reason[:87].rstrip() + "..."
    return reason


def split_reason_text(reason, max_line_len=42):
    if len(reason) <= max_line_len:
        return reason

    words = reason.split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        if len(test) <= max_line_len:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return "\n".join(lines[:2])


def generate_amenity_heatmap(address, category_results, total_score, interpretation):
    output_dir = os.path.join(settings.MEDIA_ROOT, "amenity_heatmaps")
    os.makedirs(output_dir, exist_ok=True)

    filename = f"amenity_heatmap_{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, filename)

    fig, ax = plt.subplots(figsize=(8, 11))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    navy = "#002B55"
    navy_dark = "#001F3F"
    light_row = "#F3F4F7"
    white = "#FFFFFF"
    text_dark = "#071A33"

    # Background
    ax.add_patch(Rectangle((0, 0), 100, 100, facecolor=navy_dark, edgecolor="none"))

    # Header
    draw_gradient_rect(ax, 0, 92, 100, 8, "#00386E", "#001F3F")
    ax.text(
        50,
        96,
        "Suburb Amenity Ratings",
        ha="center",
        va="center",
        fontsize=22,
        fontweight="bold",
        color=white,
    )

    ax.text(
        50,
        91,
        address,
        ha="center",
        va="center",
        fontsize=9,
        color=white,
        alpha=0.95,
    )

    # Table layout
    top_y = 88
    row_height = 7.3
    category_w = 31
    score_w = 13
    reason_w = 56

    for index, item in enumerate(category_results):
        y = top_y - ((index + 1) * row_height)

        category = item["category"]
        score = item["score"]
        reason = split_reason_text(shorten_reason(item["reason"]))

        base_color = score_to_color(score)
        lighter_color = lighten_color(base_color, 0.35)

        # Category cell
        draw_gradient_rect(
            ax, 0, y, category_w, row_height - 0.6, "#003B73", "#002B55", zorder=1
        )
        ax.add_patch(
            Rectangle(
                (0, y),
                category_w,
                row_height - 0.6,
                fill=False,
                edgecolor=white,
                linewidth=1.2,
                zorder=3,
            )
        )

        # Score cell with smooth fade
        draw_gradient_rect(
            ax,
            category_w,
            y,
            score_w,
            row_height - 0.6,
            base_color,
            lighter_color,
            zorder=1,
        )
        ax.add_patch(
            Rectangle(
                (category_w, y),
                score_w,
                row_height - 0.6,
                fill=False,
                edgecolor=white,
                linewidth=1.2,
                zorder=3,
            )
        )

        # Reason cell
        ax.add_patch(
            Rectangle(
                (category_w + score_w, y),
                reason_w,
                row_height - 0.6,
                facecolor=light_row,
                edgecolor=white,
                linewidth=1.2,
                zorder=1,
            )
        )

        # Texts
        ax.text(
            3,
            y + row_height / 2,
            category,
            ha="left",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=white,
            zorder=4,
        )

        ax.text(
            category_w + score_w / 2,
            y + row_height / 2,
            str(score),
            ha="center",
            va="center",
            fontsize=22,
            fontweight="bold",
            color=text_dark,
            zorder=4,
        )

        ax.text(
            category_w + score_w + 3,
            y + row_height / 2,
            reason,
            ha="left",
            va="center",
            fontsize=10.5,
            color=text_dark,
            linespacing=1.25,
            zorder=4,
        )

    # Total score footer
    footer_y = 9.5
    draw_gradient_rect(ax, 0, footer_y, 100, 8, "#D7191C", "#002B55", zorder=1)

    ax.text(
        42,
        footer_y + 4.3,
        "TOTAL SCORE:",
        ha="right",
        va="center",
        fontsize=16,
        fontweight="bold",
        color=white,
        zorder=4,
    )

    ax.text(
        45,
        footer_y + 4.3,
        str(total_score),
        ha="left",
        va="center",
        fontsize=27,
        fontweight="bold",
        color=white,
        zorder=4,
    )

    # Thin score scale strip
    strip_y = footer_y - 2.0
    gradient = np.linspace(0, 1, 500)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(
        gradient,
        extent=(0, 100, strip_y, strip_y + 1.2),
        origin="lower",
        cmap=SCORE_CMAP,
        aspect="auto",
        zorder=1,
    )

    # Bottom summary
    summary_text = get_summary_text(total_score)

    ax.text(
        50,
        4.9,
        summary_text,
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        fontstyle="italic",
        color=white,
        wrap=True,
        zorder=4,
    )

    ax.text(
        50,
        2.4,
        f"Overall rating: {interpretation}",
        ha="center",
        va="center",
        fontsize=10,
        color=white,
        alpha=0.9,
        zorder=4,
    )

    plt.savefig(output_path, dpi=220, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)

    media_url = settings.MEDIA_URL.rstrip("/")
    return f"{media_url}/amenity_heatmaps/{filename}"
