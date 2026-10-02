"""
Figures for the post, rendered from the model (sim.py), inputs.csv and campus.csv.

    python charts.py   -> figures/fig0_identity.png, fig1_power.png, fig2a_growth.png,
                          fig2b_share.png, fig3_campus_gap.png

Style: light surface, 2px lines, markers with a surface ring, hairline gridlines,
ink-colored text, one legend plus selective direct end labels. Series keep the same
color in every figure: wanted path = blue; grid as-is = orange;
all-out on-site = green (solid); all-out plus orbital = green (dashed).
Type is sized for Medium's ~700 px column: titles 12.5 pt, axis text 10 pt, notes >= 9 pt.
"""
import csv
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["text.parse_math"] = False
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path

from sim import HERE, YEARS, load_inputs, load_supply, run

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#6b6a65"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BOX = "#f0efec"
BLUE = "#2a78d6"     # wanted path
ORANGE = "#eb6834"   # grid as-is
GREEN = "#0f9d78"    # all-out on-site (solid) and all-out plus orbital (dashed); validated with the dataviz palette script
FONT = {"family": "DejaVu Sans"}
FIG_DIR = os.path.join(HERE, "figures")
SOURCE_LINE = ("Model and inputs at github.com/devang1304/linear-watts-exponential-compute (Epoch AI, EIA, LBNL, Goldman Sachs, "
               "GE Vernova, SpaceX filings). As of Oct 1, 2026.")
T_TITLE, T_SUB, T_AX, T_NOTE, T_FOOT = 12.5, 10, 10, 9.5, 8


def style(ax, ylabel):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["bottom"].set_linewidth(1)
    ax.grid(axis="y", color=GRID, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", colors=MUTED, labelsize=T_AX, length=0)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_color(INK2)
    ax.set_ylabel(ylabel, color=INK2, fontsize=T_AX)


def line(ax, xs, ys, color, label, dashed=False, z=3):
    ax.plot(xs, ys, color=color, linewidth=2, linestyle="--" if dashed else "-",
            solid_joinstyle="round", solid_capstyle="round", label=label, zorder=z)
    ax.plot(xs, ys, linestyle="none", marker="o", markersize=6, markerfacecolor=color,
            markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=z + 1)


def end_label(ax, x, y, text, dy=0, size=T_NOTE):
    ax.annotate(text, (x, y), xytext=(6, dy), textcoords="offset points", va="center",
                fontsize=size, color=INK2, annotation_clip=False)


def title(fig, headline, sub, wrap=70, height=4.8):
    fig.text(0.02, 1 - 0.12 / height, textwrap.fill(headline, wrap), fontsize=T_TITLE, color=INK, fontweight="semibold",
             va="top", linespacing=1.3)
    if sub:
        fig.text(0.02, 1 - 0.62 / height, textwrap.fill(sub, 108), fontsize=T_SUB, color=INK2, va="top", linespacing=1.3)
    fig.text(0.02, 0.055 / height, textwrap.fill(SOURCE_LINE, 118), fontsize=T_FOOT, color=MUTED, va="bottom")


# ---------------------------------------------------------------- Figure 0: the identity
def fig0_identity(inp, supply):
    fig = plt.figure(figsize=(8, 3.5), dpi=200, facecolor=SURFACE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    adds = [supply.get(y, {}).get("grid_as_is_gw", 0.0) for y in YEARS[1:]]
    eff = inp["hw_eff_growth"] * inp["alg_eff_growth"]
    boxes = [
        ("Power connected", "gigawatts connectable to AI sites",
         f"+{min(adds):.0f} to {max(adds):.0f} GW", "a year, linear", BOX, INK),
        ("Hardware efficiency", "operations per watt",
         f"× {inp['hw_eff_growth']:.1f}", "a year, compounding", BOX, INK),
        ("Algorithmic efficiency", "capability per operation",
         f"× {inp['alg_eff_growth']:.1f}", "a year, compounding", BOX, INK),
        ("Computing delivered", "capability-adjusted",
         "× 4.5 to 5.9", "a year, exponential", BLUE, "#ffffff"),
    ]
    xs = [3, 27, 51, 77]
    w, h, y0 = 21, 42, 25
    for (head, desc, rate, kind, fill, ink), x in zip(boxes, xs):
        ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0,rounding_size=2.5",
                                    facecolor=fill, edgecolor="none"))
        ax.text(x + w / 2, y0 + h - 8, head, ha="center", va="center", fontsize=9.5, color=ink, fontweight="semibold")
        ax.text(x + w / 2, y0 + h - 17, textwrap.fill(desc, 22), ha="center", va="center", fontsize=8.5,
                color=ink if fill == BLUE else INK2, linespacing=1.25)
        ax.text(x + w / 2, y0 + 14, rate, ha="center", va="center", fontsize=11, color=ink, fontweight="semibold")
        ax.text(x + w / 2, y0 + 5.5, kind, ha="center", va="center", fontsize=9, fontweight="semibold",
                color=ink if fill == BLUE else INK2)
    for x, sym in ((25.0, "×"), (49.0, "×"), (75.0, "=")):
        ax.text(x, y0 + h / 2, sym, ha="center", va="center", fontsize=17, color=INK)
    # bracket under the two efficiency terms
    ax.plot([27.5, 71.5], [y0 - 4, y0 - 4], color=AXIS, linewidth=1)
    ax.plot([27.5, 27.5], [y0 - 4, y0 - 1.5], color=AXIS, linewidth=1)
    ax.plot([71.5, 71.5], [y0 - 4, y0 - 1.5], color=AXIS, linewidth=1)
    ax.text(49.5, y0 - 9.5, f"together they give × {eff:.1f} more computing per watt every year", ha="center", va="center",
            fontsize=9.5, color=INK2)
    fig.text(0.02, 0.955, "Only one of the three terms depends on the grid", fontsize=T_TITLE, color=INK,
             fontweight="semibold", va="top")
    fig.text(0.02, 0.86, textwrap.fill("Base-case rates, 2025 to 2035. Power additions are the grid-as-is path; the two "
             "efficiency terms have compounded for years.", 100), fontsize=T_SUB, color=INK2, va="top", linespacing=1.3)
    fig.text(0.02, 0.03, textwrap.fill("Efficiency rates from Epoch AI (operations per watt doubling about every 2 years; compute "
             "for fixed performance halving about every 8 months).", 118), fontsize=T_FOOT, color=MUTED, va="bottom")
    fig.savefig(os.path.join(FIG_DIR, "fig0_identity.png"), facecolor=SURFACE)
    plt.close(fig)


# ---------------------------------------------------------------- Figure 1: power
def fig1_power(rows):
    last = 2032
    xs = [r["year"] for r in rows if r["year"] <= last]
    pick = lambda k: [r[k] for r in rows if r["year"] <= last]
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200, facecolor=SURFACE)
    fig.subplots_adjust(left=0.085, right=0.80, top=0.80, bottom=0.14)
    style(ax, "Gigawatts (GW)")
    line(ax, xs, pick("supply_grid_gw"), ORANGE, "Grid as-is")
    line(ax, xs, pick("supply_terrestrial_gw"), GREEN, "All-out (grid plus on-site generation)")
    line(ax, xs, pick("supply_terrestrial_plus_space_gw"), GREEN, "All-out plus orbital (launch-limited)", dashed=True)
    line(ax, xs, pick("demand_gw"), BLUE, "Wanted path (1.5x a year)", z=5)
    for k, lab, dy in (("demand_gw", "Wanted", 0), ("supply_terrestrial_plus_space_gw", "All-out + orbital", 7),
                       ("supply_terrestrial_gw", "All-out", -7), ("supply_grid_gw", "Grid as-is", 0)):
        y = pick(k)[-1]
        end_label(ax, xs[-1], y, f"{lab} {y:,.0f} GW", dy)
    for key, lab, ypos, ha, dx in (("supply_grid_gw", "on today's grid", 5, "left", 0.08),
                                   ("supply_terrestrial_gw", "with all-out power", 42, "left", 0.08)):
        for r in rows:
            if r["demand_gw"] > r[key]:
                ax.axvline(r["year"], color=AXIS, linewidth=1, zorder=1)
                ax.text(r["year"] + dx, ypos, f"In {r['year']}, {r['demand_gw']:.0f} GW wanted and\n{r[key]:.0f} GW available {lab}",
                        fontsize=T_NOTE, color=INK2, va="bottom", ha=ha, linespacing=1.25)
                break
    ax.set_xticks(xs)
    ax.set_xlim(xs[0] - 0.3, xs[-1] + 0.3)
    ax.set_ylim(0, 300)
    ax.set_yticks([0, 100, 200, 300])
    ax.legend(loc="upper left", frameon=False, fontsize=T_NOTE, labelcolor=INK2, handlelength=2.2)
    title(fig, "Power runs short in 2029 on today's grid, and in 2031 even with generators on site",
          "Gigawatts of US AI data-center power, 2025 to 2032. One gigawatt is roughly the draw of 750,000 US homes.")
    fig.savefig(os.path.join(FIG_DIR, "fig1_power.png"), facecolor=SURFACE)
    plt.close(fig)


# ---------------------------------------------------------------- Figure 2: compute (two images)
def input_ranges():
    """low/high columns of inputs.csv, by name."""
    out = {}
    with open(os.path.join(HERE, "inputs.csv"), newline="") as f:
        for r in csv.DictReader(f):
            if r["low"] and r["high"]:
                out[r["name"]] = (float(r["low"]), float(r["high"]))
    return out


def fig2_compute(rows, inp, supply):
    xs = [r["year"] for r in rows][1:]                       # 2026..2035
    paths = (("compute_unconstrained", BLUE, False, "Wanted path (power 1.5x a year)"),
             ("compute_grid", ORANGE, False, "Grid as-is"),
             ("compute_terrestrial", GREEN, False, "All-out on-site power"),
             ("compute_space", GREEN, True, "All-out plus orbital (launch-limited)"))
    growth = {k: [rows[i][k] / rows[i - 1][k] for i in range(1, len(rows))] for k, *_ in paths}
    share = {k: [100 * rows[i][k] / rows[i]["compute_unconstrained"] for i in range(1, len(rows))] for k, *_ in paths}
    rng = input_ranges()
    g = inp["demand_growth"]
    eff_lo = g * rng["hw_eff_growth"][0] * rng["alg_eff_growth"][0]
    eff_hi = g * rng["hw_eff_growth"][1] * rng["alg_eff_growth"][1]
    x0, x1 = xs[0] - 0.4, xs[-1] + 0.4
    r35 = rows[-1]
    # first year the grid path grows slower than the wanted path; None if it never binds
    bind = next((x for x, gv in zip(xs, growth["compute_grid"]) if gv < growth["compute_unconstrained"][0] - 1e-9), None)

    # --- 2a: growth multiple per year
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200, facecolor=SURFACE)
    fig.subplots_adjust(left=0.085, right=0.80, top=0.80, bottom=0.14)
    style(ax, "Computing, as a multiple of the year before")
    for k, c, d, lab in paths[:3]:
        line(ax, xs, growth[k], c, lab, dashed=d)
    end_label(ax, xs[-1], growth["compute_unconstrained"][-1], f"{growth['compute_unconstrained'][-1]:.1f}x every year", 0)
    end_label(ax, xs[-1], growth["compute_grid"][-1], f"{growth['compute_grid'][-1]:.1f}x (both)", -2)
    if bind is not None:
        ax.vlines(bind, 0, 6.3, color=AXIS, linewidth=1, zorder=1)
        ax.text(bind + 0.08, 0.35, f"Today's grid binds in {bind}", fontsize=T_NOTE, color=INK2, va="bottom")
    if bind is not None and bind < xs[-1]:
        avg_post = (rows[-1]["compute_grid"] / rows[xs.index(bind) + 1]["compute_grid"]) ** (1 / (xs[-1] - bind))
        ax.text(bind + 0.12, 3.8, f"average {avg_post:.1f}x a year once the grid binds, {bind} to {xs[-1]}",
                fontsize=T_NOTE, color=ORANGE, va="top", ha="left")
    ax.text(x0 + 0.15, 1.12, "1x would mean no growth", fontsize=T_NOTE, color=MUTED, va="bottom")
    # efficiency range as a whisker at the left edge, label beside it
    wx = x0 + 0.12
    ax.plot([wx, wx], [eff_lo, eff_hi], color=MUTED, linewidth=1.2, clip_on=False)
    for yv in (eff_lo, eff_hi):
        ax.plot([wx - 0.07, wx + 0.07], [yv, yv], color=MUTED, linewidth=1.2, clip_on=False)
    ax.text(wx + 0.2, 7.97, textwrap.fill(f"At the low or high end of the efficiency ranges, the wanted line sits at "
            f"{eff_lo:.1f}x to {eff_hi:.1f}x, and every line scales with it", 31),
            fontsize=9, color=MUTED, va="top", ha="left", linespacing=1.25)
    ax.set_xticks(xs)
    ax.set_xlim(x0, x1)
    ax.set_ylim(0, 8.4)
    ax.set_yticks([0, 1, 2, 4, 6, 8])
    ax.set_yticklabels(["0", "1x", "2x", "4x", "6x", "8x"])
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.09), frameon=False, fontsize=T_NOTE, labelcolor=INK2, handlelength=2.2)
    title(fig, "Once the grid binds, computing still grows about 4.5x a year, compared with 5.9x on the wanted path",
          f"Each year's capability-adjusted computing as a multiple of the year before. Hardware efficiency "
          f"{inp['hw_eff_growth']:.1f}x and algorithmic efficiency {inp['alg_eff_growth']:.1f}x a year in every path; only the power term differs.")
    fig.savefig(os.path.join(FIG_DIR, "fig2a_growth.png"), facecolor=SURFACE)
    plt.close(fig)

    # --- 2b: share of the wanted path, with the envelope for the grid path
    env = []
    for p0 in (rng["p0_us_ai_power_gw"][0], inp["p0_us_ai_power_gw"], rng["p0_us_ai_power_gw"][1]):
        for sc in (0.7, 1.0, 1.3):
            rr = run(dict(inp, p0_us_ai_power_gw=p0), supply, supply_scale=sc)
            env.append([100 * rr[i]["compute_grid"] / rr[i]["compute_unconstrained"] for i in range(1, len(rr))])
    env_lo = [min(v[i] for v in env) for i in range(len(xs))]
    env_hi = [max(v[i] for v in env) for i in range(len(xs))]
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200, facecolor=SURFACE)
    fig.subplots_adjust(left=0.085, right=0.80, top=0.80, bottom=0.14)
    style(ax, "Percent of the wanted path's computing")
    ax.fill_between(xs, env_lo, env_hi, color=ORANGE, alpha=0.12, linewidth=0, zorder=1)
    ax.hlines(100, xs[0], xs[-1], color=BLUE, linewidth=2, zorder=2)
    end_label(ax, xs[-1], 100, "Wanted path 100%", 0)
    for k, c, d, lab in paths[1:]:
        line(ax, xs, share[k], c, lab, dashed=d)
        end_label(ax, xs[-1], share[k][-1], f"{share[k][-1]:.0f}%", 0)
    ax.text(x0 + 0.15, 6, textwrap.fill(
        f"The shaded band shows where the grid-as-is line lands ({env_lo[-1]:.0f}% to {env_hi[-1]:.0f}% in 2035) "
        f"for any mix of today's AI power at 10, 15 or 20 GW and supply 30% lower, unchanged or 30% higher.", 60),
        fontsize=T_NOTE, color=INK2, va="bottom", linespacing=1.25, zorder=5)
    ax.set_xticks(xs)
    ax.set_xlim(x0, x1)
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
    ax.legend(handles=[Line2D([0], [0], color=BLUE, lw=2, label="Wanted path"),
                       Line2D([0], [0], color=ORANGE, lw=2, label="Grid as-is"),
                       Line2D([0], [0], color=GREEN, lw=2, label="All-out on-site power"),
                       Line2D([0], [0], color=GREEN, lw=2, linestyle="--", label="All-out plus orbital (launch-limited)")],
              loc="lower left", bbox_to_anchor=(0.0, 0.23), frameon=False, fontsize=T_NOTE, labelcolor=INK2, handlelength=2.2)
    title(fig, f"By 2035 today's grid delivers {r35['compute_grid']/r35['compute_unconstrained']:.0%} of the wanted path's "
               f"computing, and still {r35['compute_grid']/1e6:.1f} million times the 2025 level",
          "Computing delivered under each supply path as a share of the wanted path, which has unlimited power. "
          "The efficiency assumptions cancel out of this ratio.")
    fig.savefig(os.path.join(FIG_DIR, "fig2b_share.png"), facecolor=SURFACE)
    plt.close(fig)


# ---------------------------------------------------------------- Figure 3: campus gap
def rounded_bar(ax, x, h, w, color, r_px=4):
    """Bar with a 4px rounded data-end and a square base, drawn as a path."""
    y0, y1 = ax.get_ylim()
    px_per_unit = ax.get_window_extent().height / (y1 - y0)
    r = min(r_px / px_per_unit, h / 2)
    rx = min(r_px / (ax.get_window_extent().width / (ax.get_xlim()[1] - ax.get_xlim()[0])), w / 2)
    x0, x1 = x - w / 2, x + w / 2
    k = 0.5523
    verts = [(x0, 0), (x1, 0), (x1, h - r),
             (x1, h - r + k * r), (x1 - rx + k * rx, h), (x1 - rx, h),
             (x0 + rx, h),
             (x0 + rx - k * rx, h), (x0, h - r + k * r), (x0, h - r),
             (x0, 0)]
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none", zorder=3))


def fig3_campus(inp):
    plans = {}
    with open(os.path.join(HERE, "campus.csv"), newline="") as f:
        for row in csv.DictReader(f):
            plans[int(row["year"])] = (float(row["pipeline_gw"]), row["site"])
    years = [2026, 2027, 2028]
    base, t0 = inp["campus_trend_base_gw"], 2026.45
    rate = 2 ** (12 / inp["campus_trend_doubling_months"])
    trend = {y: base * rate ** (y + 0.5 - t0) for y in years}
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200, facecolor=SURFACE)
    fig.subplots_adjust(left=0.085, right=0.97, top=0.77, bottom=0.17)
    style(ax, "Gigawatts of IT power (GW)")
    ax.set_xlim(2025.5, 2028.5)
    ax.set_ylim(0, 6)
    fig.canvas.draw()
    w = 0.22
    for y in years:
        p, site = plans[y]
        rounded_bar(ax, y - w / 2 - 0.015, p, w, BLUE)
        rounded_bar(ax, y + w / 2 + 0.015, trend[y], w, MUTED)
        ax.text(y - w / 2 - 0.015, p + 0.1, f"{p:.2g}", ha="center", va="bottom", fontsize=T_AX, color=INK)
        ax.text(y + w / 2 + 0.015, trend[y] + 0.1, f"{trend[y]:.1f}", ha="center", va="bottom", fontsize=T_AX, color=INK2)
    ax.set_xticks(years)
    ax.set_xticklabels([f"{y}\n{plans[y][1]}" for y in years], linespacing=1.3)
    ax.set_yticks([0, 2, 4, 6])
    ax.legend(handles=[Line2D([0], [0], color=BLUE, lw=8, label="Largest campus planned for the year (Epoch AI tracker)"),
                       Line2D([0], [0], color=MUTED, lw=8, label="Epoch's trend, doubling every 10 months from 0.95 GW in June 2026")],
              loc="upper left", frameon=False, fontsize=T_NOTE, labelcolor=INK2)
    title(fig, "The biggest AI campus planned for 2028 is 2.3 gigawatts; the trend says about 5",
          "Largest single-site AI campus by IT power (what the chips draw, before cooling), mid-year, against the doubling "
          "time of the record campus since mid-2024.")
    fig.savefig(os.path.join(FIG_DIR, "fig3_campus_gap.png"), facecolor=SURFACE)
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    plt.rc("font", **FONT)
    inp, supply = load_inputs(), load_supply()
    rows = run(inp, supply)
    fig0_identity(inp, supply)
    fig1_power(rows)
    fig2_compute(rows, inp, supply)
    fig3_campus(inp)
    print("wrote", sorted(f for f in os.listdir(FIG_DIR) if f.endswith(".png")))


if __name__ == "__main__":
    main()
