
import streamlit as st
import pandas as pd
import requests

TEAM_ID = 1158519

st.set_page_config(
    page_title="FPL Nexus",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ FPL Nexus")

@st.cache_data(ttl=300)
def get_manager():
    url = f"https://fantasy.premierleague.com/api/entry/{TEAM_ID}/"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()

try:
    manager = get_manager()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Overall Rank",
            f"{manager.get('summary_overall_rank',0):,}"
        )

    with col2:
        st.metric(
            "Total Points",
            manager.get("summary_overall_points",0)
        )

    with col3:
        st.metric(
            "Team Value",
            f"£{manager.get('last_deadline_value',0)/10:.1f}"
        )

    st.subheader("Team Information")

    st.write(
        {
            "Team Name": manager.get("name"),
            "Manager": (
                manager.get("player_first_name","")
                + " "
                + manager.get("player_last_name","")
            )
        }
    )

except Exception as e:
    st.error(f"Error: {e}")
