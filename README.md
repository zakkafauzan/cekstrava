## cekstrava

Strava scraping helper that:
- Resolves `strava.app.link` deep links to their final Strava web URLs
- Parses each athlete page for the monthly distance (from `div[data-testid="monthly-stats"]`)
- Exports results to `all_distance.csv`

### Requirements
- Python 3.8+
- Packages: `requests`, `beautifulsoup4`

Install deps:

```bash
pip install requests beautifulsoup4
```

### Input
- Create `allathletes.txt` in this folder.
- Put one URL per line. You can mix `https://strava.app.link/...` and `https://www.strava.com/athletes/<id>` links.

Example `allathletes.txt`:

```text
https://strava.app.link/abcdEFG
https://www.strava.com/athletes/33200775
```

### Run

```bash
python coba.py
```

This will:
- Resolve each link to a final Strava web URL
- Fetch and parse the athlete page
- Extract the monthly distance from `data-testid="monthly-stats"`
- Write `all_distance.csv`

### Output
`all_distance.csv` columns:
1) `athlete_name`
2) `distance` (numeric string; unit `km` stripped)
3) `final_url` (resolved destination)

### Notes
- Some pages or elements may change; the selector targets `div[data-testid="monthly-stats"]`.
- Network timeouts/redirect flows are handled with a desktop User-Agent and fallbacks.

