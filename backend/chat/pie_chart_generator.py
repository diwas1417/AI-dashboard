import os
import uuid
import math

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from django.conf import settings


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _distribute_y_positions(points, min_gap=0.12, lower=-1.20, upper=1.20):
    """
    Adjust y positions so labels on the same side do not overlap too much.
    Keeps labels closer to their natural position than before.
    """
    if not points:
        return points

    points = sorted(points, key=lambda item: item["y"])

    # Forward pass
    for i in range(1, len(points)):
        if points[i]["y"] - points[i - 1]["y"] < min_gap:
            points[i]["y"] = points[i - 1]["y"] + min_gap

    # Shift down if top overflow
    overflow = points[-1]["y"] - upper
    if overflow > 0:
        for item in points:
            item["y"] -= overflow

    # Backward pass
    for i in range(len(points) - 2, -1, -1):
        if points[i + 1]["y"] - points[i]["y"] < min_gap:
            points[i]["y"] = points[i + 1]["y"] - min_gap

    # Shift up if bottom overflow
    underflow = lower - points[0]["y"]
    if underflow > 0:
        for item in points:
            item["y"] += underflow

    return points


def generate_single_pie_chart(section_title, items):
    """
    Generate one pie chart with clean outside labels and short curved leader lines.
    Returns chart_url.
    """

    if not items:
        return None

    parsed_items = []

    for item in items:
        category = item.get("category")
        percentage = _safe_float(item.get("percentage"))

        if category and percentage is not None:
            if percentage.is_integer():
                pct_text = f"{int(percentage)}%"
            else:
                pct_text = f"{percentage}%"

            parsed_items.append(
                {
                    "category": category,
                    "percentage": percentage,
                    "label": f"{category}\n{pct_text}",
                }
            )

    if not parsed_items:
        return None

    values = [item["percentage"] for item in parsed_items]
    labels = [item["label"] for item in parsed_items]

    fig, ax = plt.subplots(figsize=(12, 8), facecolor="white")
    ax.set_facecolor("white")

    wedges, _ = ax.pie(
        values,
        labels=None,
        startangle=90,
        radius=1.0,
        wedgeprops={
            "linewidth": 1,
            "edgecolor": "white",
        },
    )

    ax.set_title(
        section_title,
        fontsize=18,
        fontweight="bold",
        pad=18,
    )

    ax.axis("equal")

    right_side = []
    left_side = []

    for wedge, label in zip(wedges, labels):
        angle = (wedge.theta1 + wedge.theta2) / 2.0
        angle_rad = math.radians(angle)

        x = math.cos(angle_rad)
        y = math.sin(angle_rad)

        point = {
            "label": label,
            "x": x,
            "y": y,
            "angle": angle,
        }

        if x >= 0:
            right_side.append(point)
        else:
            left_side.append(point)

    # Spread labels, but only a little
    right_side = _distribute_y_positions(
        right_side, min_gap=0.14, lower=-1.18, upper=1.18
    )
    left_side = _distribute_y_positions(
        left_side, min_gap=0.14, lower=-1.18, upper=1.18
    )

    for side_points, side in [(right_side, "right"), (left_side, "left")]:
        for point in side_points:
            x = point["x"]
            y = point["y"]
            label = point["label"]

            # Start point on wedge edge
            xy = (0.92 * x, 0.92 * y)

            # Keep text closer to the pie, not too far away
            radial_multiplier = 1.28
            x_text = radial_multiplier * x
            y_text = point["y"] * 1.10

            # Ensure some minimum horizontal spacing so labels do not touch the pie
            if side == "right":
                x_text = max(x_text, 1.18)
                ha = "left"
                curve_rad = 0.15
            else:
                x_text = min(x_text, -1.18)
                ha = "right"
                curve_rad = -0.15

            ax.annotate(
                label,
                xy=xy,
                xytext=(x_text, y_text),
                ha=ha,
                va="center",
                fontsize=12,
                fontweight="bold",
                arrowprops=dict(
                    arrowstyle="-",
                    color="gray",
                    lw=1.1,
                    shrinkA=0,
                    shrinkB=0,
                    connectionstyle=f"arc3,rad={curve_rad}",
                ),
            )

    # Tighter chart area like your preferred version
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.35, 1.35)

    charts_dir = os.path.join(settings.MEDIA_ROOT, "pie_charts")
    os.makedirs(charts_dir, exist_ok=True)

    filename = f"pie_chart_{uuid.uuid4().hex}.png"
    filepath = os.path.join(charts_dir, filename)

    plt.tight_layout()
    plt.savefig(filepath, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return f"{settings.MEDIA_URL}pie_charts/{filename}"


def has_valid_items(section):
    """
    Check whether the section has at least one valid chart item.
    """
    items = section.get("items", [])

    if not isinstance(items, list) or len(items) == 0:
        return False

    for item in items:
        category = item.get("category")
        percentage = _safe_float(item.get("percentage"))

        if category and percentage is not None:
            return True

    return False


def generate_all_pie_charts(data):
    charts = {}

    household = data.get("household_structure", {})
    education = data.get("education_by_qualification", {})
    occupation = data.get("employment_by_occupation", {})

    if has_valid_items(household):
        charts["household_structure_chart_url"] = generate_single_pie_chart(
            "Household Structure",
            household.get("items", []),
        )
    else:
        charts["household_structure_chart_url"] = None

    if has_valid_items(education):
        charts["education_by_qualification_chart_url"] = generate_single_pie_chart(
            "Education By Qualification",
            education.get("items", []),
        )
    else:
        charts["education_by_qualification_chart_url"] = None

    if has_valid_items(occupation):
        charts["employment_by_occupation_chart_url"] = generate_single_pie_chart(
            "Employment By Occupation",
            occupation.get("items", []),
        )
    else:
        charts["employment_by_occupation_chart_url"] = None

    return charts
