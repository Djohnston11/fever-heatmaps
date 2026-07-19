"""
Indiana Fever shooting dashboard
Reads the scraped CSVs in data/ and renders interactive shot charts and splits
Run from the repo root: streamlit run app/streamlit_app.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
from lib import shot_chart

st.set_page_config(page_title="Fever Shooting", page_icon="🏀", layout="wide")

st.title("🏀 Indiana Fever - Shooting Dashboard")
st.caption("Green = made - Red = missed - 2026 season")

@st.cache_data
def load_data():
    """Read the scraped CSVs once and reuse them across reruns"""
    shots = pd.read_csv("data/shots.csv")
    splits = pd.read_csv("data/splits.csv")
    return shots, splits

shots, splits = load_data()

players = sorted(shots["PLAYER_NAME"].unique())
selected = st.selectbox("Select a player", players)

player_shots = shots[shots["PLAYER_NAME"] == selected]

chart_col, stats_col = st.columns([2, 1])

with chart_col:
    fig = shot_chart(player_shots, selected, subtitle="Indiana Fever - 2026")
    st.pyplot(fig)

with stats_col:
    st.subheader("Shooting splits")
    player_row = splits[splits["PLAYER_NAME"] == selected].iloc[0]
    st.metric("Field Goal %", f"{player_row['FG_PCT']}%")
    fg3 = player_row['FG3_PCT']
    st.metric("3-Point %", "—" if pd.isna(fg3) else f"{fg3}%")
    st.metric("Effective FG %", f"{player_row['EFG_PCT']}%")
    st.caption(f"{int(player_row['FGM'])}/{int(player_row['FGA'])} FG · "
               f"{int(player_row['FG3M'])}/{int(player_row['FG3A'])} from three")
    
st.divider()
st.subheader("Full roster — shooting splits")
st.dataframe(
    splits[["PLAYER_NAME", "FGA", "FG_PCT", "FG3A", "FG3_PCT", "EFG_PCT"]],
    hide_index=True,
    use_container_width=True,
)