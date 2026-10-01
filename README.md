# Linear watts, exponential compute

A bounding model of US AI compute under electricity constraints, 2025–2035, and the code behind the post of the same name.

The whole model is one identity, run year by year:

```
compute(t) = power(t) × hardware_efficiency^(t−2025) × algorithmic_efficiency^(t−2025)
```

where `power(t)` is the lesser of what the industry wants to build (a demand path) and what can be connected (a supply path). The result: with power growing linearly instead of 1.5x a year, compute still grows about 4.5x a year once the grid binds, against 5.9x on the wanted path; the largest single-site campus planned for 2028 is 2.3x under Epoch's trend; and orbital compute cannot add meaningful gigawatts before 2031 even on the vendor's mass budget.

**As of September 30, 2026.**

## Run it

```
pip install -r requirements.txt
python sim.py            # prints the summary, writes results/sim_out.csv
python sensitivity.py    # prints the sensitivity table, writes results/sensitivity.csv
python charts.py         # figures/fig0_identity.png, fig1_power.png, fig2a_growth.png, fig2b_share.png, fig3_campus_gap.png
python tables.py         # figures/tables/t1..t7.png (Table 1 = t6, Table 2 = t1, Table 3 = t5; the rest are supplementary)
```

Run them in this order; `tables.py` reads `results/sensitivity.csv`. `sim.py` and `sensitivity.py` use the standard library only; `charts.py` and `tables.py` need matplotlib. Another matplotlib version can change the PNGs' pixels but not their content.

## Change an input

Every parameter lives in one of three CSVs, each row with its source URL and date:

| File | What it holds |
| --- | --- |
| `inputs.csv` | Starting power, demand growth, the two efficiency terms, the space parameters, the share-of-electricity inputs, the single-site trend anchor. Columns: `name, value, low, high, unit, source_url, source_date, note`. |
| `supply_paths.csv` | Per-year GW newly connectable under the grid-as-is and all-out terrestrial paths, and AI-dedicated Starship launches per year. |
| `campus.csv` | The largest planned single-site campus by year (2026-2030), with the site and source. The trend it is compared with is Epoch's ten-month doubling from the June 2026 record (parameters in `inputs.csv`). |

The `low`/`high` columns are the ranges `sensitivity.py` sweeps, one input at a time, alongside terrestrial supply ±30% and two combinations. `results/sensitivity.csv` holds every case; Table 3 in the post shows a subset.

After editing a value, rerun all four scripts. The results and the plotted lines follow; titles, notes and a few table cells in `charts.py` and `tables.py` are written for the base case and have to be updated by hand.

`post.md` is the post. `CHANGELOG.md` lists the corrections made before publication.

## License

MIT. Cite the post and this repository if you reuse the model; the inputs belong to their sources.
