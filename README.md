# US Open 2026

Connie Xu’s US Open 2026 prediction desk — men’s and women’s singles title odds for every main-draw player at Flushing Meadows.

This is a **form model, not betting lines**. Percents are form-weighted from the last 12 months of results, with a hard-court bump, then walked through the actual 128-player brackets. Eliminated players sit at 0%; remaining mass is renormalized to 100%.

## Run locally

```bash
npm install && npm run dev
```

Then open the URL Vite prints (usually `http://localhost:5173`).

```bash
npm run build
```

Rebuild the JSON catalogs from the snapshots in `scripts/sources/` with:

```bash
python3 scripts/build-data.py
```

## Data

- Draws: Wikipedia 2026 US Open men’s and women’s singles (retrieved 31 August 2026).
- Rankings used for the draw: ATP/WTA lists of **Monday 24 August 2026**.
- Ages and players outside that top-100 snapshot: ESPN ATP/WTA lists of 27 August 2026, when available. Missing stats render as an em dash.

Jannik Sinner withdrew with a right-knee injury and is not in the men’s draw. Round 1 is in progress as of 31 August 2026. Women’s final is 12 September; men’s final is 13 September.
