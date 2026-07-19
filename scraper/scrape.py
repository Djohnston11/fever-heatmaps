"""
Scrapes Indiana Fever shooting data from the WNBA stats backend and writes:
    data/shots.csv          every field-goal attempt by every player
    data/splits.csv         each player's shooting percentages
    state.json              the last game processed - no repeats
    
Run from the repo root:     python scraper/scrape.py
"""
import os
import time
import numpy as np
import pandas as pd
from nba_api.stats.endpoints import commonteamroster, shotchartdetail

# Config
FEVER_TEAM_ID = 1611661325          # Indiana Fever (WNBA)
SEASON        = "2026"              # WNBA season 
SEASON_TYPE   = "Regular Season"
LEAGUE_ID     = "10"                # 10 is WNBA 00 is NBA
DATA_DIR      = "data"
PAUSE         = 0.7                 # seconds between API calls

def get_roster():
    """Return a list of {'PLAYER_ID', 'PLAYER'} for the current roster"""
    print("Getting roster...")
    endpoint = commonteamroster.CommonTeamRoster(
        team_id=FEVER_TEAM_ID,
        season=SEASON,
        league_id_nullable=LEAGUE_ID,
    )
    df = endpoint.get_data_frames()[0]
    return df[["PLAYER_ID", "PLAYER"]].to_dict("records")

def get_player_shots(player_id):
    """Return a DataFrame of every field-goal attempt for one player."""
    time.sleep(PAUSE) # I want a break before each call So I do not get limited
    endpoint = shotchartdetail.ShotChartDetail(
        team_id=FEVER_TEAM_ID,
        player_id=player_id,
        league_id=LEAGUE_ID,
        season_nullable=SEASON,
        season_type_all_star=SEASON_TYPE,
        context_measure_simple="FGA",
    )
    return endpoint.get_data_frames()[0]

def scrape_all_shots():
    """Fetch shots for every player and combine into one DataFrame"""
    roster = get_roster()
    print(f"Fetching shots for {len(roster)} players...")

    all_frames = []
    for player in roster:
        name = player["PLAYER"]
        try:
            shots = get_player_shots(player["PLAYER_ID"])
        except Exception as error:
            print(f"  ! {name}: failed ({error})")
            continue

        if shots.empty:
            print(f"  - {name}: no shots yet")
            continue

        print(f"  + {name}: {len(shots)} shots")
        all_frames.append(shots)
    
    combined = pd.concat(all_frames, ignore_index=True)
    print(f"Total: {len(combined)} shots across {len(all_frames)} players")
    return combined

def save_shots(shots):
    """Write the combined shots to data/shots.csv."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "shots.csv")
    shots.to_csv(path, index=False)
    print(f"Saved -> {path}")

def build_splits(shots):
    """Compute per-player shooting splits from the combined shots table
    Covers FG%, 3 point %, eFG%"""
    df = shots.copy()
    df["IS_3"] = df["SHOT_TYPE"].str.contains("3PT") # True for 3 point attempts
    df["MADE"] = df["SHOT_MADE_FLAG"] == 1           # True on makes
    df["MADE_3"] = df["MADE"] & df["IS_3"]           #True on made 3

    grouped = df.groupby("PLAYER_NAME")
    splits = grouped.agg(
        FGA=("SHOT_MADE_FLAG", "size"),   # total attempts which is row count
        FGM=("MADE", "sum"),              # makes
        FG3A=("IS_3", "sum"),             # 3 attempts
        FG3M=("MADE_3", "sum"),           # made threes
    ).reset_index()

    splits["FG_PCT"] = (100 * splits["FGM"] / splits["FGA"]).round(1)
    splits["FG3_PCT"] = (100 * splits["FG3M"] / splits["FG3A"].replace(0, np.nan)).round(1)
    splits["EFG_PCT"] = (100 * (splits["FGM"] + 0.5 * splits["FG3M"]) / splits["FGA"]).round(1)

    return splits.sort_values("FGA", ascending=False).reset_index(drop=True)

def save_splits(splits):
    """Write the splits table to data/splits.csv."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "splits.csv")
    splits.to_csv(path, index=False)
    print(f"Saved -> {path}")

if __name__ == "__main__":
    shots = scrape_all_shots()
    save_shots(shots)
    splits = build_splits(shots)
    save_splits(splits)
    print("Done.")