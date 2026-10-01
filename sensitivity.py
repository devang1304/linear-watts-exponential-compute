"""
Sensitivity sweep for sim.py.

Varies one input at a time over its low/high range in inputs.csv (every input
that has a range), terrestrial supply by +/-30%, and two combinations. Reports,
for the grid-as-is path: the year power first binds, compute delivered as a
share of the unconstrained path in 2030, 2033 and 2035, the average compute
growth rate, and the demand path's share of US electricity sales in 2030; and,
for the orbital path: the year terrestrial plus orbital supply binds, orbital
capacity in 2030 and 2033, and compute delivered as a share of the
unconstrained path in 2035.

Run:  python sensitivity.py   -> prints a markdown table, writes results/sensitivity.csv
"""
import csv
import os

from sim import HERE, load_inputs, load_supply, run, binding_year, growth_rate

FIELDS = ["case", "binds_grid", "binds_terrestrial", "share_2030_grid", "share_2033_grid", "share_2035_grid",
          "growth_unconstrained", "growth_grid", "demand_share_2030_pct",
          "binds_terrestrial_plus_space", "space_gw_2030", "space_gw_2033", "share_2035_space"]

# Case label for each input with a range, in sweep order.
LABELS = {
    "p0_us_ai_power_gw": lambda v: f"Starting power {v:g} GW",
    "demand_growth": lambda v: f"Demand growth {v:.1f}x/yr",
    "hw_eff_growth": lambda v: f"Hardware efficiency {v:.1f}x/yr",
    "alg_eff_growth": lambda v: f"Algorithmic efficiency {v:.1f}x/yr",
    "space_kw_per_tonne": lambda v: f"Orbital compute {v:g} kW per tonne",
    "space_tonnes_per_launch": lambda v: f"Starship payload {v:g} t",
    "space_sat_life_years": lambda v: f"Satellite life {v:g} years",
    "dc_utilization": lambda v: f"Utilization {v:.0%}",
}
SPACE_AND_UTIL = ("space_kw_per_tonne", "space_tonnes_per_launch", "space_sat_life_years", "dc_utilization")


def load_ranges(path=None):
    """Return {name: (low, high)} for every row of inputs.csv that has a range."""
    path = path or os.path.join(HERE, "inputs.csv")
    out = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["low"] and r["high"]:
                out[r["name"]] = (float(r["low"]), float(r["high"]))
    return out


def metrics(inp, supply, supply_scale=1.0):
    rows = run(inp, supply, supply_scale)
    r30 = next(r for r in rows if r["year"] == 2030)
    r33 = next(r for r in rows if r["year"] == 2033)
    r35 = rows[-1]
    return {
        "binds_grid": binding_year(rows, "supply_grid_gw"),
        "binds_terrestrial": binding_year(rows, "supply_terrestrial_gw"),
        "share_2030_grid": r30["compute_grid"] / r30["compute_unconstrained"],
        "share_2033_grid": r33["compute_grid"] / r33["compute_unconstrained"],
        "share_2035_grid": r35["compute_grid"] / r35["compute_unconstrained"],
        "growth_unconstrained": growth_rate(rows, "compute_unconstrained", 2025, 2035),
        "growth_grid": growth_rate(rows, "compute_grid", 2025, 2035),
        "demand_share_2030_pct": r30["share_demand_pct"],
        "binds_terrestrial_plus_space": binding_year(rows, "supply_terrestrial_plus_space_gw"),
        "space_gw_2030": r30["space_capacity_gw"],
        "space_gw_2033": r33["space_capacity_gw"],
        "share_2035_space": r35["compute_space"] / r35["compute_unconstrained"],
    }


def one_at_a_time(base, rng, names):
    """Cases for each named input at its low and high end (a value equal to the base case is skipped)."""
    return [(LABELS[n](v), {n: v}, 1.0) for n in names if n in rng for v in rng[n] if v != base[n]]


def main():
    base = load_inputs()
    supply = load_supply()
    rng = load_ranges()
    unknown = set(rng) - set(LABELS)
    if unknown:
        raise SystemExit(f"inputs.csv has a range for {sorted(unknown)}; add a label to LABELS in sensitivity.py")

    p_lo, p_hi = rng["p0_us_ai_power_gw"]
    d_lo, d_hi = rng["demand_growth"]
    a_lo, a_hi = rng["alg_eff_growth"]
    cases = [("Base case", {}, 1.0)]
    cases += one_at_a_time(base, rng, ("p0_us_ai_power_gw", "demand_growth", "hw_eff_growth", "alg_eff_growth"))
    cases += [(f"Terrestrial supply {int(s*100)}%", {}, s) for s in (0.7, 1.3)]
    cases += one_at_a_time(base, rng, SPACE_AND_UTIL)
    cases += [(f"Pessimistic combo: {p_hi:g} GW start, {d_hi:.1f}x demand, 70% supply, {a_lo:.1f}x algorithms",
               {"p0_us_ai_power_gw": p_hi, "demand_growth": d_hi, "alg_eff_growth": a_lo}, 0.7)]
    cases += [(f"Optimistic combo: {p_lo:g} GW start, {d_lo:.1f}x demand, 130% supply, {a_hi:.1f}x algorithms",
               {"p0_us_ai_power_gw": p_lo, "demand_growth": d_lo, "alg_eff_growth": a_hi}, 1.3)]

    out = []
    for name, overrides, scale in cases:
        inp = dict(base)
        inp.update(overrides)
        m = metrics(inp, supply, scale)
        m["case"] = name
        out.append(m)

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "sensitivity.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for m in out:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()})

    print("| Case | Grid binds | Terrestrial binds | Compute vs wanted path, 2030 | 2033 | 2035 | Growth wanted | Growth grid-as-is | Share of US electricity, 2030 "
          "| Terrestrial + orbital binds | Orbital GW, 2030 | 2033 | Plus orbital vs wanted path, 2035 |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for m in out:
        print(f"| {m['case']} | {m['binds_grid'] or 'never'} | {m['binds_terrestrial'] or 'never'} | "
              f"{m['share_2030_grid']:.0%} | {m['share_2033_grid']:.0%} | {m['share_2035_grid']:.0%} | {m['growth_unconstrained']:.1f}x/yr | "
              f"{m['growth_grid']:.1f}x/yr | {m['demand_share_2030_pct']:.0f}% | {m['binds_terrestrial_plus_space'] or 'never'} | "
              f"{m['space_gw_2030']:.1f} | {m['space_gw_2033']:.1f} | {m['share_2035_space']:.0%} |")


if __name__ == "__main__":
    main()
