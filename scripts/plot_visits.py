#!/usr/bin/env python3
"""Maintain a visits dataset and render a pixel-styled SVG line chart.

Two responsibilities:

1. ``--ingest views.json`` merges a GitHub Traffic *views* API payload into the
   running CSV at ``assets/visits.csv`` (keyed by day; the API only exposes a
   rolling 14-day window, so we accumulate history ourselves).
2. With no ``--ingest`` it simply (re)renders ``assets/visits.svg`` from the CSV.

The chart is intentionally drawn as raw SVG (no matplotlib dependency) so it
runs anywhere and keeps the blocky MinecrafTeX look.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "assets", "visits.csv")
SVG_PATH = os.path.join(ROOT, "assets", "visits.svg")

# Minecraft-ish palette.
BG = "#0f1117"
PANEL = "#171b24"
GRID = "#2b3242"
GRASS = "#7dB84a"
GRASS_DARK = "#5d9c3c"
AREA = "#7dB84a"  # drawn with fill-opacity for cross-renderer support
INK = "#c9d4e3"
SUB = "#7e8aa0"


def _read_csv():
    rows = []
    if not os.path.exists(CSV_PATH):
        return rows
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                d = datetime.strptime(r["date"], "%Y-%m-%d").date()
            except (KeyError, ValueError):
                continue
            views = int(r.get("views", 0) or 0)
            uniques = int(r.get("uniques", 0) or 0)
            rows.append((d, views, uniques))
    rows.sort(key=lambda x: x[0])
    return rows


def _write_csv(rows):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "views", "uniques"])
        for d, v, u in rows:
            w.writerow([d.isoformat(), v, u])


def ingest(payload_path):
    with open(payload_path, encoding="utf-8") as fh:
        data = json.load(fh)
    by_day = {d: (v, u) for d, v, u in _read_csv()}
    for item in data.get("views", []):
        ts = item.get("timestamp", "")
        try:
            d = datetime.strptime(ts[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        # The API value for a day is authoritative; keep the larger seen count.
        v, u = int(item.get("count", 0)), int(item.get("uniques", 0))
        if d in by_day:
            v = max(v, by_day[d][0])
            u = max(u, by_day[d][1])
        by_day[d] = (v, u)
    rows = [(d, vu[0], vu[1]) for d, vu in sorted(by_day.items())]
    _write_csv(rows)


def _fmt_day(d):
    return d.strftime("%b %d")


def render():
    rows = _read_csv()
    # Ensure we always have at least a baseline so the README never looks broken.
    if not rows:
        today = date.today()
        rows = [(today - timedelta(days=1), 0, 0), (today, 0, 0)]

    W, H = 860, 360
    ml, mr, mt, mb = 56, 24, 64, 56  # margins
    pw, ph = W - ml - mr, H - mt - mb

    days = [r[0] for r in rows]
    views = [r[1] for r in rows]
    uniques = [r[2] for r in rows]
    total_views = sum(views)
    total_uniques = sum(uniques)
    vmax = max(max(views), max(uniques), 1)
    # Round the axis up to a friendly step.
    step = 1
    while vmax / step > 5:
        lead = str(step)[0]
        step *= 5 if lead in ("2", "5") else 2
    ymax = (vmax // step + 1) * step

    n = len(rows)

    def x(i):
        if n == 1:
            return ml + pw / 2
        return ml + pw * i / (n - 1)

    def y(val):
        return mt + ph * (1 - val / ymax)

    def path_for(series):
        return " ".join(
            ("M" if i == 0 else "L") + f"{x(i):.1f},{y(v):.1f}"
            for i, v in enumerate(series)
        )

    # X tick selection (avoid clutter): at most ~8 labels.
    label_every = max(1, n // 8)
    xticks = [i for i in range(n) if i % label_every == 0 or i == n - 1]

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="\'Courier New\',monospace" '
        f'role="img" aria-label="MinecrafTeX repository visits over time">'
    )
    parts.append(f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>')
    parts.append(
        f'<rect x="{ml}" y="{mt}" width="{pw}" height="{ph}" fill="{PANEL}"/>'
    )

    # Title + totals.
    parts.append(
        f'<text x="{ml}" y="30" fill="{INK}" font-size="20" '
        f'font-weight="bold">MinecrafTeX \u2014 Repository Visits</text>'
    )
    parts.append(
        f'<text x="{ml}" y="50" fill="{SUB}" font-size="13">'
        f'daily page views &#183; total {total_views} views / '
        f'{total_uniques} unique visitors</text>'
    )

    # Horizontal grid + y labels.
    yticks = 4
    for t in range(yticks + 1):
        val = ymax * t / yticks
        yy = y(val)
        parts.append(
            f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+pw}" y2="{yy:.1f}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{ml-8}" y="{yy+4:.1f}" fill="{SUB}" font-size="11" '
            f'text-anchor="end">{int(round(val))}</text>'
        )

    # X labels.
    for i in xticks:
        xx = x(i)
        parts.append(
            f'<text x="{xx:.1f}" y="{mt+ph+20:.1f}" fill="{SUB}" '
            f'font-size="11" text-anchor="middle">{_fmt_day(days[i])}</text>'
        )

    # Area under the views line.
    area = (
        f'M{x(0):.1f},{y(0):.1f} '
        + " ".join(f'L{x(i):.1f},{y(v):.1f}' for i, v in enumerate(views))
        + f' L{x(n-1):.1f},{y(0):.1f} Z'
    )
    parts.append(f'<path d="{area}" fill="{AREA}" fill-opacity="0.16"/>')

    # Unique visitors line (thin, dashed, dark).
    parts.append(
        f'<path d="{path_for(uniques)}" fill="none" stroke="{GRASS_DARK}" '
        f'stroke-width="2" stroke-dasharray="4 4" '
        f'stroke-linejoin="miter" stroke-linecap="square"/>'
    )
    # Views line (bold, blocky joins).
    parts.append(
        f'<path d="{path_for(views)}" fill="none" stroke="{GRASS}" '
        f'stroke-width="3" stroke-linejoin="miter" stroke-linecap="square"/>'
    )

    # Blocky pixel markers on the views line.
    for i, v in enumerate(views):
        parts.append(
            f'<rect x="{x(i)-3:.1f}" y="{y(v)-3:.1f}" width="6" height="6" '
            f'fill="{GRASS}"/>'
        )

    # Legend.
    lx, ly = ml + pw - 220, mt + 14
    parts.append(f'<rect x="{lx}" y="{ly-9}" width="14" height="6" fill="{GRASS}"/>')
    parts.append(
        f'<text x="{lx+20}" y="{ly}" fill="{INK}" font-size="12">views</text>'
    )
    parts.append(
        f'<rect x="{lx+90}" y="{ly-9}" width="14" height="6" fill="{GRASS_DARK}"/>'
    )
    parts.append(
        f'<text x="{lx+110}" y="{ly}" fill="{INK}" font-size="12">unique</text>'
    )

    updated = date.today().isoformat()
    parts.append(
        f'<text x="{ml+pw}" y="{H-14}" fill="{SUB}" font-size="10" '
        f'text-anchor="end">updated {updated}</text>'
    )

    parts.append("</svg>")

    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ingest", metavar="VIEWS_JSON",
                    help="GitHub traffic/views JSON to merge before rendering")
    args = ap.parse_args()
    if args.ingest:
        ingest(args.ingest)
    render()


if __name__ == "__main__":
    main()
