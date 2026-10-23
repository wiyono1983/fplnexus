import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="FPL Fixtures",
    page_icon="⚽"
)

st.title("⚽ FPL Fixtures")

@st.cache_data(ttl=300)
def get_bootstrap():
    return requests.get(
        "https://fantasy.premierleague.com/api/bootstrap-static/"
    ).json()

@st.cache_data(ttl=300)
def get_fixtures():
    return requests.get(
        "https://fantasy.premierleague.com/api/fixtures/"
    ).json()

try:

    bootstrap = get_bootstrap()
    fixtures = get_fixtures()

    teams = pd.DataFrame(
        bootstrap["teams"]
    )

    fixture_df = pd.DataFrame(
        fixtures
    )

    team_lookup = dict(
        zip(
            teams["id"],
            teams["name"]
        )
    )

    fixture_df["Home Team"] = (
        fixture_df["team_h"].map(team_lookup)
    )

    fixture_df["Away Team"] = (
        fixture_df["team_a"].map(team_lookup)
    )

    gw_list = sorted(
        fixture_df["event"]
        .dropna()
        .unique()
    )

    selected_gw = st.selectbox(
        "Gameweek",
        gw_list
    )

    gw_df = fixture_df[
        fixture_df["event"] == selected_gw
    ].copy()

    gw_df["kickoff_time"] = pd.to_datetime(
        gw_df["kickoff_time"],
        errors="coerce"
    )

    start_date = (
        gw_df["kickoff_time"]
        .min()
        .strftime("%d %b")
    )

    end_date = (
        gw_df["kickoff_time"]
        .max()
        .strftime("%d %b %Y")
    )

    st.subheader(
        f"Gameweek {selected_gw}"
    )

    st.caption(
        f"{start_date} - {end_date}"
    )

    
        
            for _, row in gw_df.iterrows():

    kickoff = "--:--"

    if pd.notna(row["kickoff_time"]):
        kickoff = row["kickoff_time"].strftime("%H:%M")

    st.markdown(
        f"""
        <div style="text-align:center;">
            {row['Home Team']} <b>{kickoff}</b> {row['Away Team']}
        </div>
        """,
        unsafe_allow_html=True
    )


except Exception as e:
    st.error(
        f"Error: {e}"
    )
