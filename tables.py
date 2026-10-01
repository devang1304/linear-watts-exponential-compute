"""
Render the post's tables as PNG images (Medium has no native tables).

    python tables.py  -> figures/tables/*.png

Numbering follows the order of appearance in the post: Table 1 = launch math (t6),
Table 2 = inputs (t1), Table 3 = sensitivity (t5). The other files are supplementary
tables kept for the repository and are not embedded in the post.
"""
import csv
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["text.parse_math"] = False  # keep "$" literal (prices), not mathtext

from sim import HERE, load_inputs, load_supply, run
from sensitivity import LABELS, load_ranges

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#6b6a65", "#e1e0d9"
OUT = os.path.join(HERE, "figures", "tables")
FONT = 10          # cell text, points
LINE_H = 0.215     # inches per text line at FONT


def render_table(name, title, headers, rows, widths, note=None, fontsize=FONT):
    """widths: relative column widths (sum ~ 1). Cells wrap to their column width."""
    chars_per_unit = 104 * 8.5 / fontsize  # characters across the full width (conservative)
    wrapped = []
    for r in rows:
        cells = [textwrap.wrap(str(c), max(6, int(w * chars_per_unit))) or [""] for c, w in zip(r, widths)]
        wrapped.append(cells)
    line_h = LINE_H * fontsize / FONT
    row_heights = [max(len(c) for c in cells) * line_h + 0.16 for cells in wrapped]
    head_lines = [textwrap.wrap(h, max(6, int(w * chars_per_unit))) or [""] for h, w in zip(headers, widths)]
    head_h = max(len(h) for h in head_lines) * line_h + 0.22
    title_lines = textwrap.wrap(title, 72)
    note_lines = textwrap.wrap(note, 125) if note else []
    title_h = 0.22 * len(title_lines) + 0.2
    height = 0.25 + title_h + head_h + sum(row_heights) + (0.22 + 0.16 * len(note_lines) if note else 0.15)
    fig = plt.figure(figsize=(8, height), dpi=200, facecolor=SURFACE)
    x0, x1 = 0.03, 0.97
    y = 1 - 0.2 / height
    fig.text(x0, y, "\n".join(title_lines), fontsize=12, color=INK, fontweight="semibold", va="top", linespacing=1.25)
    y -= (title_h + 0.05) / height
    xs = [x0]
    for w in widths[:-1]:
        xs.append(xs[-1] + w * (x1 - x0))
    for lines, x in zip(head_lines, xs):
        for i, ln in enumerate(lines):
            fig.text(x + 0.004, y - i * line_h / height, ln, fontsize=fontsize, color=INK2, fontweight="semibold", va="top")
    y -= head_h / height
    fig.add_artist(plt.Line2D([x0, x1], [y, y], color=MUTED, linewidth=0.8))
    for cells, rh in zip(wrapped, row_heights):
        top = y - 0.08 / height
        for lines, x in zip(cells, xs):
            for i, ln in enumerate(lines):
                fig.text(x + 0.004, top - i * line_h / height, ln, fontsize=fontsize, color=INK, va="top")
        y -= rh / height
        fig.add_artist(plt.Line2D([x0, x1], [y, y], color=GRID, linewidth=0.8))
    for i, ln in enumerate(note_lines):
        fig.text(x0, y - (0.2 + 0.16 * i) / height, ln, fontsize=8, color=MUTED, va="center")
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name), facecolor=SURFACE)
    plt.close(fig)


def main():
    inp = load_inputs()
    supply = load_supply()
    rows = run(inp, supply)
    by_year = {r["year"]: r for r in rows}

    # Table 2 (post) / t1: inputs
    labels = {
        "p0_us_ai_power_gw": ("US AI data-center power, end-2025", "GW"),
        "demand_growth": ("Wanted path (what the industry is trying to build)", "x per year"),
        "hw_eff_growth": ("Hardware efficiency (operations per watt)", "x per year"),
        "alg_eff_growth": ("Algorithmic efficiency (compute for fixed performance)", "x per year"),
        "space_kw_per_tonne": ("Orbital compute per tonne launched, all-in", "kW per tonne"),
        "space_tonnes_per_launch": ("Starship payload to orbit", "tonnes"),
        "space_sat_life_years": ("Satellite life", "years"),
        "dc_utilization": ("Data-center utilization (share-of-electricity check only)", "fraction"),
        "us_electricity_twh_2026": ("US electricity sales, 2026", "TWh"),
        "us_electricity_growth": ("US electricity growth", "x per year"),
        "campus_trend_base_gw": ("Largest AI campus, June 2026 (trend anchor)", "GW"),
        "campus_trend_doubling_months": ("Doubling time of the largest campus", "months"),
    }
    sources = {
        "p0_us_ai_power_gw": "Epoch AI: global AI ~30 GW in Q4 2025; US taken as half (assumption)",
        "demand_growth": "Epoch AI (Jul 2026): US AI power 'could reach 100 GW' by 2030; Goldman: 31 -> 66 GW, 2025-27",
        "hw_eff_growth": "Epoch AI: FLOP/W of leading GPUs/TPUs doubles about every 2 years",
        "alg_eff_growth": "Epoch AI: compute for fixed performance halves every ~8 months (95% CI 5-14)",
        "space_kw_per_tonne": "SpaceX filing implies 100 kW/t, its satellite ~70; Google's reference satellite ~49. Vendor end used",
        "space_tonnes_per_launch": "SpaceX prospectus: Starship V3 designed for 100 t, fully reusable (design goal)",
        "space_sat_life_years": "Google Suncatcher paper: 5-year reference life, repair 'impracticable'",
        "dc_utilization": "Assumption",
        "us_electricity_twh_2026": "EIA Short-Term Energy Outlook, Sept 2026",
        "us_electricity_growth": "Assumption (EIA shows +1.8% for 2027)",
        "campus_trend_base_gw": "Epoch AI: Colossus 2 at ~950 MW of IT power, June 2026",
        "campus_trend_doubling_months": "Epoch AI: the record campus has doubled every ten months since mid-2024",
    }
    trows = []
    with open(os.path.join(HERE, "inputs.csv"), newline="") as f:
        for r in csv.DictReader(f):
            # a row without an entry above is shown with its own name, unit and note
            lab, unit = labels.get(r["name"], (r["name"], r["unit"]))
            rng = f"{r['low']}-{r['high']}" if r["low"] and r["high"] else "not swept"
            trows.append([lab, f"{float(r['value']):g} {unit}", rng, sources.get(r["name"], r["note"])])
    render_table("t1_inputs.png", "Table 2. Inputs; the range column is what the sensitivity analysis sweeps",
                 ["Input", "Value", "Range", "Source"], trows, [0.28, 0.16, 0.10, 0.46],
                 note="Full rows with URLs and dates in inputs.csv in the repository.")

    # Supplementary / t2: supply paths
    srows = []
    for y in range(2026, 2036):
        s = supply[y]
        srows.append([str(y), f"+{s['grid_as_is_gw']:.0f}", f"+{s['all_out_terrestrial_gw']:.0f}",
                      f"{s['space_ai_launches']:.0f}", f"{by_year[y]['space_capacity_gw']:.1f}"])
    render_table("t2_supply_paths.png", "Supplementary table. The three supply paths: GW newly connectable to AI sites each year",
                 ["Year", "Grid as-is (GW/yr)", "All-out on-site (GW/yr)", "AI Starship launches", "Orbital capacity in service (GW)"],
                 srows, [0.10, 0.20, 0.25, 0.20, 0.25],
                 note="Orbital capacity = launches x 100 t x 80 kW/t (the vendor's mass budget), retired after 5 years.")

    # Supplementary / t3: compute delivered
    crow = []
    for y in (2028, 2030, 2033, 2035):
        r = by_year[y]
        u = r["compute_unconstrained"]
        crow.append([str(y), (f"{u/1e6:.1f} million x" if u >= 1e6 else f"{u:,.0f}x"), f"{r['compute_grid']/u:.0%}",
                     f"{r['compute_terrestrial']/u:.0%}", f"{r['compute_space']/u:.0%}", f"{r['share_demand_pct']:.0f}%"])
    render_table("t3_compute_delivered.png", "Supplementary table. Computing delivered under each supply path, as a share of the wanted path",
                 ["Year", "Computing on the wanted path (x 2025)", "On today's grid", "With all-out on-site power", "Plus orbital", "Share of US electricity the wanted path needs"],
                 crow, [0.08, 0.20, 0.13, 0.17, 0.13, 0.29],
                 note="Hardware efficiency 1.4x and algorithmic efficiency 2.8x per year; utilization 80% for the last column.")

    # Supplementary / t4: campus gap (Epoch's trend: doubling every 10 months from the June 2026 record)
    base, t0 = inp["campus_trend_base_gw"], 2026.45
    rate = 2 ** (12 / inp["campus_trend_doubling_months"])
    camp = []
    with open(os.path.join(HERE, "campus.csv"), newline="") as f:
        for r in csv.DictReader(f):
            y = int(r["year"])
            if y > 2028:
                continue
            trend = base * rate ** (y + 0.5 - t0)
            camp.append([str(y), f"{float(r['pipeline_gw']):.2g} GW", r["site"], f"{trend:.1f} GW", f"{trend/float(r['pipeline_gw']):.1f}x"])
    render_table("t4_campus_gap.png", "Supplementary table. Largest planned single-site campus versus Epoch's ten-month-doubling trend (IT power, mid-year)",
                 ["Year", "Planned", "Site", "Trend", "Gap"], camp, [0.09, 0.13, 0.42, 0.14, 0.12],
                 note="Trend anchored on Colossus 2 at 0.95 GW in June 2026. Epoch's own projection for the largest campus in 2030 is 4-16 GW.")

    # Table 3 (post) / t5: sensitivity, condensed
    sens = {}
    with open(os.path.join(HERE, "results", "sensitivity.csv"), newline="") as f:
        for r in csv.DictReader(f):
            sens[r["case"]] = r
    def row(label, prefix):
        key = next((k for k in sens if k.startswith(prefix)), None)
        if key is None:
            raise SystemExit(f"results/sensitivity.csv has no case '{prefix}'; run sensitivity.py first")
        r = sens[key]
        return [label, r["binds_grid"] or "never", f"{float(r['share_2030_grid']):.0%}", f"{float(r['share_2035_grid']):.0%}",
                f"{float(r['growth_grid']):.1f}x", f"{float(r['demand_share_2030_pct']):.0f}%"]
    # case names follow the low/high columns of inputs.csv, as in sensitivity.py (which skips a value equal to the base case)
    ranges = load_ranges()
    def swept(name, label):
        return [row(label(v), LABELS[name](v)) for v in ranges[name] if v != inp[name]]
    (p_lo, p_hi), (d_lo, d_hi), (a_lo, a_hi) = (ranges[k] for k in ("p0_us_ai_power_gw", "demand_growth", "alg_eff_growth"))
    srows = [
        row(f"Base case ({inp['p0_us_ai_power_gw']:g} GW start, {inp['demand_growth']:.1f}x demand, base supply)", "Base"),
        *swept("p0_us_ai_power_gw", lambda v: f"Starting power {v:g} GW"),
        *swept("demand_growth", lambda v: f"Demand growth {v:.1f}x a year"),
        row("Supply 30% lower", "Terrestrial supply 70"),
        row("Supply 30% higher", "Terrestrial supply 130"),
        ["Both efficiency rates at the low or high end (hardware 1.3-1.5x, algorithms 2.0-3.5x): only the growth rate moves",
         "2029", "68%", "19%", "3.3x to 6.7x", "18%"],
        row(f"Pessimistic combination ({p_hi:g} GW, {d_hi:.1f}x demand, 70% supply, {a_lo:.1f}x algorithms)", "Pessimistic"),
        row(f"Optimistic combination ({p_lo:g} GW, {d_lo:.1f}x demand, 130% supply, {a_hi:.1f}x algorithms)", "Optimistic"),
    ]
    render_table("t5_sensitivity.png", "Table 3. Only starting power, demand growth and supply move the year the grid binds",
                 ["Case", "Today's grid binds", "Computing delivered vs the wanted path, 2030", "Same, 2035", "Grid-as-is growth per year, 2025-35 average", "Share of US electricity the wanted path needs, 2030"],
                 srows, [0.30, 0.11, 0.15, 0.10, 0.14, 0.14],
                 note="The efficiency rates scale both paths equally, so by construction they change the growth rate and not the binding year or the share delivered.")

    # Table 1 (post) / t6: launch math, on two mass budgets
    kw_t_lo, kw_t_hi = inp["space_kw_per_tonne"], 1000 / 20.5   # SpaceX's 12.5 kg/kW vs Google's 20.5 kg/kW
    t_l = inp["space_tonnes_per_launch"]
    def t_per_gw(kwt): return 1e6 / kwt
    def l_per_gw(kwt): return t_per_gw(kwt) / t_l
    launch = [
        ["1 GW of orbital compute", f"{t_per_gw(kw_t_lo):,.0f} to {t_per_gw(kw_t_hi):,.0f} t", f"{l_per_gw(kw_t_lo):,.0f} to {l_per_gw(kw_t_hi):,.0f}",
         "Starship has flown 3 times in 2026; Falcon 9 ~170 times in 2025"],
        ["SpaceX plant target: 1 GW a year from end-2027", f"{t_per_gw(kw_t_lo):,.0f} to {t_per_gw(kw_t_hi):,.0f} t/yr", f"{l_per_gw(kw_t_lo):,.0f} to {l_per_gw(kw_t_hi):,.0f} a year",
         "A Starship for AI every two to three days"],
        ["SpaceX prospectus: 100 GW a year", f"{100*t_per_gw(kw_t_lo)/1e6:.3g} to {100*t_per_gw(kw_t_hi)/1e6:.3g} million t/yr",
         f"{100*l_per_gw(kw_t_lo):,.0f} to {100*l_per_gw(kw_t_hi):,.0f} a year",
         f"{100*l_per_gw(kw_t_lo)/365:.0f} to {100*l_per_gw(kw_t_hi)/365:.0f} launches a day; each year's 100 GW is about a fifth of today's US average load"],
    ]
    render_table("t6_launch_math.png", "Table 1. One gigawatt in orbit takes 125 to 205 Starship launches",
                 ["Target", "Mass to orbit", f"Starship launches ({t_l:.0f} t each)", "Context"], launch, [0.27, 0.24, 0.17, 0.32],
                 note="Mass budgets: 12.5 kg per kW (between SpaceX's filing, which implies 10, and its satellite design, about 14) to 20.5 kg per kW (Google's reference satellite: 575 kg, 28 kW). Starship's 100 t payload is a design goal.")

    # Supplementary / t7: cost math (launch cost only, Google's basis)
    cost = [
        ["~$3,250/kg (Falcon 9 list price today)", "~$13,000", "4 to 23 times the bill"],
        ["$1,000/kg", "~$4,050", "1.3 to 7 times the bill"],
        ["$200/kg (Google's mid-2030s threshold)", "$810", "Within the range"],
    ]
    render_table("t7_cost_math.png", "Supplementary table. Launch cost alone per kilowatt-year in orbit, against a $570-3,000 electricity bill on the ground",
                 ["Launch price per kilogram", "Launch cost per kW-year", "Versus a terrestrial data center's electricity bill"], cost, [0.34, 0.26, 0.40],
                 note="Google's $810 at $200/kg for its reference satellite (20.5 kg per kW, five-year life), scaled linearly with launch price. Excludes the satellite itself.")

    print("wrote", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
