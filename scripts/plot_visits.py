#!/usr/bin/env python3
"""Maintain repository visit data and render a README-friendly SVG chart.

With ``--ingest views.json`` this merges GitHub's traffic/views API payload into
``assets/visits.csv``. With no arguments it renders ``assets/visits.svg`` from
that CSV. The GitHub API only exposes a rolling window, so the CSV keeps older
history.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "assets", "visits.csv")
SVG_PATH = os.path.join(ROOT, "assets", "visits.svg")

BG = "#0f1117"
PANEL = "#171b24"
GRID = "#2b3242"
GRASS = "#7dB84a"
GRASS_DARK = "#5d9c3c"
INK = "#c9d4e3"
SUB = "#7e8aa0"


def _read_csv():
    rows = []
    if not os.path.exists(CSV_PATH):
        return rows
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                day = datetime.strptime(row["date"], "%Y-%m-%d").date()
                views = int(row.get("views", 0) or 0)
                uniques = int(row.get("uniques", 0) or 0)
            except (KeyError, ValueError):
                continue
            rows.append((day, views, uniques))
    rows.sort(key=lambda item: item[0])
    return rows


def _write_csv(rows):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", "views", "uniques"])
        for day, views, uniques in rows:
            writer.writerow([day.isoformat(), views, uniques])


def ingest(payload_path):
    with open(payload_path, encoding="utf-8") as fh:
        payload = json.load(fh)
    by_day = {day: (views, uniques) for day, views, uniques in _read_csv()}
    for item in payload.get("views", []):
        try:
            day = datetime.strptime(item.get("timestamp", "")[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        views = int(item.get("count", 0) or 0)
        uniques = int(item.get("uniques", 0) or 0)
        if day in by_day:
            views = max(views, by_day[day][0])
            uniques = max(uniques, by_day[day][1])
        by_day[day] = (views, uniques)
    _write_csv([(day, views, uniques) for day, (views, uniques) in sorted(by_day.items())])


def _fmt_day(day):
    return day.strftime("%b %d")


def _points(series, x_for, y_for):
    return " ".join(
        ("M" if idx == 0 else "L") + f"{x_for(idx):.1f},{y_for(value):.1f}"
        for idx, value in enumerate(series)
    )


def render():
    rows = _read_csv()
    if not rows:
        today = date.today()
        rows = [(today - timedelta(days=1), 0, 0), (today, 0, 0)]

    width, height = 860, 360
    ml, mr, mt, mb = 56, 24, 64, 56
    plot_w, plot_h = width - ml - mr, height - mt - mb

    days = [row[0] for row in rows]
    views = [row[1] for row in rows]
    uniques = [row[2] for row in rows]
    total_views = sum(views)
    total_uniques = sum(uniques)
    vmax = max(max(views), max(uniques), 1)
    step = 1
    while vmax / step > 5:
        step *= 2 if str(step)[0] not in ("2", "5") else 5
    ymax = (vmax // step + 1) * step

    def x_for(idx):
        return ml + (plot_w / 2 if len(rows) == 1 else plot_w * idx / (len(rows) - 1))

    def y_for(value):
        return mt + plot_h * (1 - value / ymax)

    label_every = max(1, len(rows) // 8)
    xticks = [idx for idx in range(len(rows)) if idx % label_every == 0 or idx == len(rows) - 1]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Courier New,monospace" '
        'role="img" aria-label="MinecrafTeX repository visits over time">',
        f'<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>',
        f'<rect x="{ml}" y="{mt}" width="{plot_w}" height="{plot_h}" fill="{PANEL}"/>',
        f'<text x="{ml}" y="30" fill="{INK}" font-size="20" font-weight="bold">MinecrafTeX Repository Visits</text>',
        f'<text x="{ml}" y="50" fill="{SUB}" font-size="13">daily page views &#183; total {total_views} views / {total_uniques} unique visitors</text>',
    ]

    for tick in range(5):
        value = ymax * tick / 4
        yy = y_for(value)
        parts.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml + plot_w}" y2="{yy:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{ml - 8}" y="{yy + 4:.1f}" fill="{SUB}" font-size="11" text-anchor="end">{int(round(value))}</text>')

    for idx in xticks:
        parts.append(f'<text x="{x_for(idx):.1f}" y="{mt + plot_h + 20:.1f}" fill="{SUB}" font-size="11" text-anchor="middle">{_fmt_day(days[idx])}</text>')

    area = (
        f'M{x_for(0):.1f},{y_for(0):.1f} '
        + " ".join(f'L{x_for(idx):.1f},{y_for(value):.1f}' for idx, value in enumerate(views))
        + f' L{x_for(len(rows) - 1):.1f},{y_for(0):.1f} Z'
    )
    parts.append(f'<path d="{area}" fill="{GRASS}" fill-opacity="0.16"/>')
    parts.append(f'<path d="{_points(uniques, x_for, y_for)}" fill="none" stroke="{GRASS_DARK}" stroke-width="2" stroke-dasharray="4 4" stroke-linejoin="miter" stroke-linecap="square"/>')
    parts.append(f'<path d="{_points(views, x_for, y_for)}" fill="none" stroke="{GRASS}" stroke-width="3" stroke-linejoin="miter" stroke-linecap="square"/>')

    for idx, value in enumerate(views):
        parts.append(f'<rect x="{x_for(idx) - 3:.1f}" y="{y_for(value) - 3:.1f}" width="6" height="6" fill="{GRASS}"/>')

    legend_x, legend_y = ml + plot_w - 220, mt + 14
    parts.append(f'<rect x="{legend_x}" y="{legend_y - 9}" width="14" height="6" fill="{GRASS}"/>')
    parts.append(f'<text x="{legend_x + 20}" y="{legend_y}" fill="{INK}" font-size="12">views</text>')
    parts.append(f'<rect x="{legend_x + 90}" y="{legend_y - 9}" width="14" height="6" fill="{GRASS_DARK}"/>')
    parts.append(f'<text x="{legend_x + 110}" y="{legend_y}" fill="{INK}" font-size="12">unique</text>')
    parts.append(f'<text x="{ml + plot_w}" y="{height - 14}" fill="{SUB}" font-size="10" text-anchor="end">updated {date.today().isoformat()}</text>')
    parts.append("</svg>")

    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ingest", metavar="VIEWS_JSON", help="GitHub traffic/views JSON to merge before rendering")
    args = parser.parse_args()
    if args.ingest:
        ingest(args.ingest)
    render()


if __name__ == "__main__":
    main()
