# Changelog

## 2026-10-01, v1.2, single date stamp

- Figures, Table 1 and README now carry one date, October 1, 2026, the day the post was written and published, in place of a separate September 30 data date. Inputs are unchanged.

## 2026-10-01, v1.1, pre-publication review

Corrections from a second review of the full draft (numbers, sources, editorial and adversarial passes, graded against a written rubric). The post text lives in the Medium draft; the corrections below were applied there.

Post:

- Single site: "Epoch's own projection for the largest campus is 4 to 16 gigawatts" removed. That range is Epoch's figure for the largest training run, which may span sites; Epoch's single-campus range for 2030 is 1 to 5 GW, now stated. The multi-site sentence now carries Epoch's conclusion that distributed training is feasible with bandwidth a smaller constraint than power, with optics kept as the cost.
- Headline growth rate now carries its range (about 3 to 6x once the grid binds at the ends of the efficiency ranges), and the 9.3 million figure is labelled as what the efficiency assumptions imply.
- Fleet-replacement caveat corrected from 55 to 65% to 50 to 65% (four- to six-year cycles at 1.4x a year give 65%, 57% and 51%).
- "AI's power grows only 12 to 20% a year by 2032" corrected to 17 to 20% in 2032 and about 12% by 2035.
- PJM's service population corrected from 65 to 67 million (PJM's July 14, 2026 release). "50% a year" corrected to "1.5 times a year". "About 150 lines of Python" corrected to about 170.
- The hardware-efficiency sentence no longer infers that 1.4x is the careful choice from a rack-throughput figure that also carries higher rack power.
- Buyer guidance now distinguishes Epoch's 13x a year all-benchmark price decline from about 5x a year for capability two years old, matching the price prediction; the price-index falsifier softened from "rises for two quarters" to "stops falling for a year".
- Orbital path: the model's crediting of orbital chips with ground efficiency is stated.
- Starship flight count and ship reuse tied to September 30, 2026; years added to the November 2025, March 2026 and February 2026 quotes.
- Table 1 image replaced (Falcon 9 flew 165 times in 2025, not about 170; "filing" for "prospectus"); Figure 3 image replaced ("full build" for "end-state").

Repository:

- charts.py and tables.py: en dashes and colons removed from all figure and table text, annotations reworded in plain sentences, fig2a title changed from "instead of 5.9x" to "compared with 5.9x on the wanted path", fig0 and fig1 labels reworded, table source notes rewritten as sentences, ranges written "a to b", "not swept" changed to "fixed".
- tables.py: Falcon 9 2025 launches 165; "prospectus" changed to "filing"; the campus table note now gives Epoch's 1 to 5 GW single-campus range and attributes the 4 to 16 GW to the largest training run.
- campus.csv: site label "xAI Colossus 2 end-state" changed to "xAI Colossus 2 full build"; the Hyperion note corrected as above.
- README: title of the Medium post added; en dash removed; result sentence and supply-path names reworded.
- All figures re-rendered.

## 2026-09-30, v1.0, first draft

Model, inputs and figures as of September 30, 2026.

Corrections from the pre-publication review (numbers, sources, editorial and adversarial passes over the full draft):

- Space: the launch count and the cost figure had used different mass budgets. The post now states both (12.5 kg per kW from SpaceX's design, 20.5 from Google's reference satellite: 125 to 205 launches per GW), labels Google's $810 per kW-year as launch cost only, and reconciles the text with the cost table ($1,000/kg is still above the most expensive grid power; $200/kg roughly matches the bill). "Fifteen times cheaper" corrected to sixteen (3,250/200).
- Single site: the trend is now Epoch's own series for the record campus (doubling every ten months from 0.95 GW in June 2026) instead of a 2.2x-per-year training-run rate applied to an unverified 0.5 GW 2025 base. The 2028 headline becomes "2.3 gigawatts instead of about 5"; the 2030 extrapolation is replaced by Epoch's 4-16 GW range; "already two years behind" becomes "the plans for 2027 and 2028 fall behind."
- Supply: added the nameplate-to-firm bridge (86 GW planned in 2026 is roughly 18 GW of average output) and the reasoning behind the 12 GW/yr grid-as-is path; "supply 30% higher or lower moves the year by one" corrected (30% lower: 2027; 30% higher: 2030).
- Model caveats added: frontier efficiency applied to the whole fleet (2035 grid-path figures would be 55-65% of those shown under a four- to six-year replacement cycle; growth rates unchanged); Epoch's algorithmic rate is measured on pre-training and applied to all compute; efficiency rates cannot move the binding year by construction because demand is fixed in watts; Epoch's 95% interval on the algorithmic rate (1.8-5.3x/yr) is wider than the range swept.
- Share-of-electricity check now given at 60-80% utilization (14-18% in 2030); "growth rate of AI's power falls below 10% a year" corrected to 12-20% through the early 2030s.
- Sources: Fairwater linked to Epoch's directory entry (2,263 MW IT power, Q2 2028); PJM auction, Palisades fuel loading, Suncatcher launch date, Musk's "2 to 3 years" quote, Hyperion's 5 GW and the satellite filings now cited; EIA's 2025 additions described as "the most since 2002" rather than a record; the SemiAnalysis throughput figure no longer described as per-watt; Musk's turbine quote dropped and his chips remark framed as a forecast; ESA's warning quoted with its condition; "1.1 million satellites" corrected to "more than a million" in filings; "fivefold per generation" corrected to two to four times; BLS CPI linked to the archived August release.
- Predictions: the METR task-length prediction dropped as off-thesis; the campus prediction tied to the trend's value (3.5 GW at end-2027); the power-additions prediction tied to a named series.
- Figures re-rendered for Medium's column width (larger type, darker greys, validated green); Figure 2 split into 2a (growth per year) and 2b (share of the wanted path); Figure 3 limited to 2026-2028; tables renumbered by order of appearance.

Corrections made during the first fact-check (48 claims checked against primary pages, before this draft):

- METR's "~1.5x acceleration of AI R&D" figure is a preliminary, "highly experimental" estimate from a separate assessment inside Anthropic, with an unspecified time period; it is now described as such rather than as a METR finding.
- A Reuters/Ipsos poll result had been paraphrased as "73% worry about AI"; the actual item is that 73% say AI companies have not done enough to prevent serious harm to society.
- A "four TPUs" count for Google's Suncatcher prototype satellite had no source; removed.
- The 110 m² radiator area attributed to SpaceX's AI1 satellite was a back-calculation from its 150 kW and 1,400 W/m² figures, not a reported number; now labeled as derived.
- Fairwater Wisconsin's 2.26 GW is projected IT power (Epoch); an earlier Epoch estimate of 3.3 GW total draw by late 2027 is noted alongside it.
- "First model rated Critical for cyber" (GPT-6 Astra) is OpenAI's first such model, not the industry's; reworded.
- Lumentum's supply-gap and indium-phosphide remarks are reported by Tom's Hardware in paraphrase; the CEO's verbatim figure is "somewhere greater than 30%".
