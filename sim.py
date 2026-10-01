"""
Linear watts, exponential compute
=================================
A bounding model of US AI compute under electricity constraints, 2025-2035.

The whole model is one identity, run year by year:

    compute(t) = power(t) * hw_eff^(t-2025) * alg_eff^(t-2025)

where power(t) is the lesser of what the industry wants to build (the demand
path) and what can be connected (a supply path). Every constant is read from
inputs.csv and supply_paths.csv, each row of which carries its source URL.

Run:   python sim.py            -> prints a summary, writes results/sim_out.csv
Import: from sim import run, load_inputs, load_supply
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
YEARS = list(range(2025, 2036))


def load_inputs(path=None):
    """Return {name: value} from inputs.csv."""
    path = path or os.path.join(HERE, "inputs.csv")
    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out[row["name"]] = float(row["value"])
    return out


def load_supply(path=None):
    """Return {year: {grid_as_is_gw, all_out_terrestrial_gw, space_ai_launches}}."""
    path = path or os.path.join(HERE, "supply_paths.csv")
    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out[int(row["year"])] = {
                "grid_as_is_gw": float(row["grid_as_is_gw"] or 0),
                "all_out_terrestrial_gw": float(row["all_out_terrestrial_gw"] or 0),
                "space_ai_launches": float(row["space_ai_launches"] or 0),
            }
    return out


def run(inp, supply, supply_scale=1.0):
    """
    Run the model. Returns a list of dict rows, one per year.

    inp          : dict from load_inputs()
    supply       : dict from load_supply()
    supply_scale : multiplies every year's terrestrial additions (for sensitivity)
    """
    p0 = inp["p0_us_ai_power_gw"]
    g = inp["demand_growth"]
    hw = inp["hw_eff_growth"]
    alg = inp["alg_eff_growth"]
    kw_per_t = inp["space_kw_per_tonne"]
    t_per_launch = inp["space_tonnes_per_launch"]
    life = int(inp["space_sat_life_years"])
    util = inp["dc_utilization"]
    twh0 = inp["us_electricity_twh_2026"]
    twh_g = inp["us_electricity_growth"]

    # 1. Demand: what the industry wants to build (GW).
    demand = [p0 * g ** (y - 2025) for y in YEARS]

    # 2. Supply: cumulative connectable power under each path (GW).
    def cumulative(key):
        out = [p0]
        for y in YEARS[1:]:
            out.append(out[-1] + supply_scale * supply.get(y, {}).get(key, 0.0))
        return out

    s_grid = cumulative("grid_as_is_gw")
    s_terr = cumulative("all_out_terrestrial_gw")

    # Space: launches * tonnes * kW/t, retired after `life` years.
    gw_per_launch = kw_per_t * t_per_launch / 1e6
    space_add = {y: supply.get(y, {}).get("space_ai_launches", 0.0) * gw_per_launch for y in YEARS}
    space_cap = [sum(v for yy, v in space_add.items() if y - life < yy <= y) for y in YEARS]
    s_space = [a + b for a, b in zip(s_terr, space_cap)]

    # 3. Realized power = min(demand, supply).
    def realized(s):
        return [min(d, x) for d, x in zip(demand, s)]

    r_grid, r_terr, r_space = realized(s_grid), realized(s_terr), realized(s_space)

    # 4. Compute index (2025 = 1): power x hardware efficiency x algorithmic efficiency.
    def compute_index(p):
        return [(x / p0) * hw ** (y - 2025) * alg ** (y - 2025) for x, y in zip(p, YEARS)]

    # 5. Share of US electricity, for the sanity check.
    def share_pct(p):
        return [x * 8.76 * util / (twh0 * twh_g ** (y - 2026)) * 100 for x, y in zip(p, YEARS)]

    rows = []
    for i, y in enumerate(YEARS):
        rows.append({
            "year": y,
            "demand_gw": demand[i],
            "supply_grid_gw": s_grid[i],
            "supply_terrestrial_gw": s_terr[i],
            "space_capacity_gw": space_cap[i],
            "supply_terrestrial_plus_space_gw": s_space[i],
            "realized_grid_gw": r_grid[i],
            "realized_terrestrial_gw": r_terr[i],
            "realized_space_gw": r_space[i],
            "compute_unconstrained": compute_index(demand)[i],
            "compute_grid": compute_index(r_grid)[i],
            "compute_terrestrial": compute_index(r_terr)[i],
            "compute_space": compute_index(r_space)[i],
            "share_demand_pct": share_pct(demand)[i],
            "share_grid_pct": share_pct(r_grid)[i],
            "share_terrestrial_pct": share_pct(r_terr)[i],
        })
    return rows


def binding_year(rows, supply_key):
    """First year in which demand exceeds the given supply path, or None."""
    for r in rows:
        if r["demand_gw"] > r[supply_key] + 1e-9:
            return r["year"]
    return None


def growth_rate(rows, key, y0, y1):
    """Average annual growth factor of `key` between y0 and y1."""
    a = next(r[key] for r in rows if r["year"] == y0)
    b = next(r[key] for r in rows if r["year"] == y1)
    return (b / a) ** (1.0 / (y1 - y0))


def write_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})


def main():
    inp = load_inputs()
    supply = load_supply()
    rows = run(inp, supply)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    write_csv(rows, os.path.join(HERE, "results", "sim_out.csv"))

    gw_per_launch = inp["space_kw_per_tonne"] * inp["space_tonnes_per_launch"] / 1e6
    print(f"Tonnes per GW at {inp['space_kw_per_tonne']:.0f} kW/t: {1000/inp['space_kw_per_tonne']*1000:,.0f}"
          f"  -> launches per GW: {1/gw_per_launch:,.0f}  -> launches/yr for 100 GW/yr: {100/gw_per_launch:,.0f}")
    print(f"Grid-as-is binds in {binding_year(rows, 'supply_grid_gw')}; "
          f"all-out terrestrial binds in {binding_year(rows, 'supply_terrestrial_gw')}; "
          f"terrestrial + space binds in {binding_year(rows, 'supply_terrestrial_plus_space_gw')}")
    print(f"Compute growth 2025-2035: unconstrained {growth_rate(rows,'compute_unconstrained',2025,2035):.2f}x/yr, "
          f"grid-as-is {growth_rate(rows,'compute_grid',2025,2035):.2f}x/yr, "
          f"all-out terrestrial {growth_rate(rows,'compute_terrestrial',2025,2035):.2f}x/yr")
    print(f"{'year':>4} {'demand':>7} {'grid':>6} {'terr':>6} {'space':>6} | {'C_grid/U':>8} {'C_terr/U':>8} {'C_space/U':>9} | {'demand%':>7}")
    for r in rows:
        print(f"{r['year']:>4} {r['demand_gw']:>7.1f} {r['supply_grid_gw']:>6.0f} {r['supply_terrestrial_gw']:>6.0f} "
              f"{r['space_capacity_gw']:>6.1f} | {r['compute_grid']/r['compute_unconstrained']:>8.0%} "
              f"{r['compute_terrestrial']/r['compute_unconstrained']:>8.0%} {r['compute_space']/r['compute_unconstrained']:>9.0%} | "
              f"{r['share_demand_pct']:>6.0f}%")


if __name__ == "__main__":
    main()
