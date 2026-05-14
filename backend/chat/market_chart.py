import os
import re
import uuid

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from django.conf import settings


def clean_currency(value):
    if not value or value == "Not verified":
        return None

    digits = re.sub(r"[^\d]", "", str(value))
    return int(digits) if digits else None


def extract_year(period):
    match = re.search(r"(20\d{2})", str(period))
    return int(match.group(1)) if match else None


def calculate_period_growth(start, end):
    if not start or not end:
        return "Not verified"

    return round(((end - start) / start) * 100, 1)


def calculate_annual_growth(start, end, years):
    if not start or not end or years <= 0:
        return "Not verified"

    return round((((end / start) ** (1 / years)) - 1) * 100, 1)


def format_y_axis(value, position):
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${int(value / 1000)}k"


def get_label_style(year):
    """
    Returns manual placement for each year.
    direction:
        1  = above point
       -1  = below point
    """
    manual_positions = {
        2010: -1,
        2011: -1,
        2012: 1,
        2013: 1,
        2014: 1,
        2015: 1,
        2016: 1,
        2017: 1,
        2018: 1,
        2019: 1,
        2020: 1,
        2021: 1,
        2022: -1,
        2023: 1,
        2024: -1,
        2025: 1,
        2026: 1,
    }
    return manual_positions.get(year, 1)


def generate_market_trend_chart(data):
    pre = data.get("pre_covid_table", [])
    post = data.get("post_covid_table", [])
    combined = pre + post

    pairs = []

    for row in combined:
        year = extract_year(row.get("Period"))
        median = clean_currency(row.get("Median Value"))

        if year and median:
            pairs.append((year, median))

    pairs = sorted(pairs, key=lambda item: item[0])

    if not pairs:
        return None, {
            "pre_covid_period_growth": "Not verified",
            "pre_covid_annual_growth": "Not verified",
            "post_covid_period_growth": "Not verified",
            "post_covid_annual_growth": "Not verified",
        }

    years = [item[0] for item in pairs]
    medians = [item[1] for item in pairs]

    pre_pairs = sorted(
        [
            (extract_year(row.get("Period")), clean_currency(row.get("Median Value")))
            for row in pre
        ],
        key=lambda item: item[0] or 0,
    )
    pre_pairs = [(year, value) for year, value in pre_pairs if year and value]

    post_pairs = sorted(
        [
            (extract_year(row.get("Period")), clean_currency(row.get("Median Value")))
            for row in post
        ],
        key=lambda item: item[0] or 0,
    )
    post_pairs = [(year, value) for year, value in post_pairs if year and value]

    growth_summary = {
        "pre_covid_period_growth": "Not verified",
        "pre_covid_annual_growth": "Not verified",
        "post_covid_period_growth": "Not verified",
        "post_covid_annual_growth": "Not verified",
    }

    if len(pre_pairs) >= 2:
        start_year, start_value = pre_pairs[0]
        end_year, end_value = pre_pairs[-1]

        growth_summary["pre_covid_period_growth"] = calculate_period_growth(
            start_value,
            end_value,
        )
        growth_summary["pre_covid_annual_growth"] = calculate_annual_growth(
            start_value,
            end_value,
            end_year - start_year,
        )

    if len(post_pairs) >= 2:
        start_year, start_value = post_pairs[0]
        end_year, end_value = post_pairs[-1]

        growth_summary["post_covid_period_growth"] = calculate_period_growth(
            start_value,
            end_value,
        )
        growth_summary["post_covid_annual_growth"] = calculate_annual_growth(
            start_value,
            end_value,
            end_year - start_year,
        )

    blue = "#2c78a8"

    fig, ax = plt.subplots(figsize=(16, 9))

    ax.plot(
        years,
        medians,
        marker="o",
        linewidth=2.2,
        markersize=6,
        color=blue,
        zorder=2,
    )

    max_value = max(medians)
    min_value = min(medians)
    value_range = max_value - min_value if max_value != min_value else max_value

    # More spacing so text sits away from line
    label_offset = value_range * 0.055

    # Value labels with white background so line stays behind text
    for year, median in zip(years, medians):
        direction = get_label_style(year)

        if direction == 1:
            y_position = median + label_offset
            va = "bottom"
        else:
            y_position = median - label_offset
            va = "top"

        ax.text(
            year,
            y_position,
            f"${median:,.0f}",
            ha="center",
            va=va,
            fontsize=9,
            color="black",
            zorder=5,
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                alpha=0.92,
                pad=1.4,
            ),
        )

    ax.axvline(
        x=2019.5,
        linestyle="--",
        linewidth=1.5,
        color="black",
        zorder=1,
    )

    ax.set_title(
        "Long Term House Price Trend: Pre-COVID vs COVID/Post-COVID",
        fontsize=19,
        fontweight="bold",
        pad=20,
    )

    suburb = data.get("suburb_or_postcode", "Not verified")
    report_type = data.get("report_type", "Houses Only")

    fig.suptitle(
        f"{suburb} | {report_type} | Median House Value",
        fontsize=12,
        y=0.955,
    )

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Median Value (AUD)", fontsize=15)

    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.35)
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=0)
    ax.yaxis.set_major_formatter(FuncFormatter(format_y_axis))

    # Fixed lower bound to match clean look
    lower_bound = 300000
    upper_bound = max_value + (value_range * 0.30)
    ax.set_ylim(lower_bound, upper_bound)

    ymin, ymax = ax.get_ylim()

    # Section headings
    heading_y = ymax - ((ymax - ymin) * 0.08)

    ax.text(
        2014.5,
        heading_y,
        "Pre-COVID (2010-2019)",
        ha="center",
        fontsize=17,
        fontweight="bold",
        color=blue,
    )

    ax.text(
        2023,
        heading_y,
        "COVID/Post-COVID (2020-2026)",
        ha="center",
        fontsize=17,
        fontweight="bold",
        color=blue,
    )

    # Growth summary boxes
    if growth_summary["pre_covid_period_growth"] != "Not verified":
        ax.text(
            2014.0,
            ymin + ((ymax - ymin) * 0.77),
            f"Period Growth: {growth_summary['pre_covid_period_growth']}%\n"
            f"Annual Growth: {growth_summary['pre_covid_annual_growth']}% p.a.",
            fontsize=10.5,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.4",
                facecolor="white",
                edgecolor="black",
                alpha=0.95,
            ),
            zorder=4,
        )

    if growth_summary["post_covid_period_growth"] != "Not verified":
        ax.text(
            2023.2,
            ymin + ((ymax - ymin) * 0.50),
            f"Period Growth: {growth_summary['post_covid_period_growth']}%\n"
            f"Annual Growth: {growth_summary['post_covid_annual_growth']}% p.a.",
            fontsize=10.5,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.4",
                facecolor="white",
                edgecolor="black",
                alpha=0.95,
            ),
            zorder=4,
        )

    fig.text(
        0.5,
        0.025,
        "Source: Long Term Market Trends, CMA Report",
        ha="center",
        fontsize=11,
    )

    charts_dir = os.path.join(settings.MEDIA_ROOT, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    filename = f"market_trend_{uuid.uuid4().hex}.png"
    filepath = os.path.join(charts_dir, filename)

    plt.tight_layout(rect=[0.04, 0.07, 0.98, 0.93])
    plt.savefig(filepath, dpi=200)
    plt.close(fig)

    chart_url = f"{settings.MEDIA_URL}charts/{filename}"

    return chart_url, growth_summary
