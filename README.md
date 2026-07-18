# Indiana Fever Shooting Heat Maps

Interactive shot charts and a shooting-efficiency dashboard for the WNBA's Indiana Fever, updated after each game. Green/red shot charts show where each player scores. A stats table also breaks down shooting percentages.

## How it works

    WNBA stats API - local scraper - data/*.csv - streamlit dashboard

The scraper runs locally, pulls shot-level data, and writes CSV files committed to the repo. The dashboard only reads those files, so the public app stays fast and reliable. 

## Quick start

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python examples/demo.py         # writes output/sample_shot_chart.png

## Data source

WNBA stats backend via the [`nba_api`](https://github.com/swar/nba_api)
package (`LeagueID=10`). Public game data, for personal / portfolio use.