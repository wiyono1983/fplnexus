import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="FPL Fixtures",
    page_icon="⚽",
    layout="centered"
)

st.title("⚽ FPL Fixtures")

@st.cache_data(ttl=300)
def get_data():

    bootstrap = requests.get(
        "https://fantasy.premierleague.com/api/bootstrap-static/",
        timeout=20
    ).json()

    fixtures = requests.get(
        "https://fantasy.premierleague.com/api/fixtures/",
        timeout=20
    ).json()

    return bootstrap, fixtures


try:

    bootstrap, fixtures = get_data()

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

    fixture_df["kickoff_time"] = pd.to_datetime(
        fixture_df["kickoff_time"],
        errors="coerce"
    )

    gw_list = sorted(
        fixture_df["event"]
        .dropna()
        .unique()
    )

    gw = st.selectbox(
        "Gameweek",
        gw_list
    )

    gw_df = fixture_df[
        fixture_df["event"] == gw
    ].copy()

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
        f"Gameweek {gw}"
    )

    st.caption(
        f"{start_date} - {end_date}"
    )

    st.divider()

    for _, row in gw_df.iterrows():

        kickoff = "--:--"

        if pd.notna(row["kickoff_time"]):
            kickoff = row[
                "kickoff_time"
            ].strftime("%H:%M")

        left, center, right = st.columns(
            [5, 2, 5]
        )

        with left:
            st.markdown(
                f"<div style='text-align:right'>{row['Home Team']}</div>",
                unsafe_allow_html=True
            )

        with center:
            st.markdown(
                f"<div style='text-align:center'><b>{kickoff}</b></div>",
                unsafe_allow_html=True
            )

        with right:
            st.markdown(
                f"<div style='text-align:left'>{row['Away Team']}</div>",
                unsafe_allow_html=True
            )

except Exception as e:

    st.error(
        f"Error: {e}"
    )
