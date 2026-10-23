import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="FPL Fixtures",
    page_icon="⚽"
)

st.title("⚽ FPL Fixtures")

@st.cache_data(ttl=300)
def load_data():

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

    bootstrap, fixtures = load_data()

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

    fixture_df["Home"] = (
        fixture_df["team_h"].map(team_lookup)
    )

    fixture_df["Away"] = (
        fixture_df["team_a"].map(team_lookup)
    )

    fixture_df["kickoff_time"] = (
    pd.to_datetime(
        fixture_df["kickoff_time"],
        utc=True,
        errors="coerce"
    )
    .dt.tz_convert("Asia/Jakarta")
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

    st.subheader(
        f"Gameweek {gw}"
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

    st.caption(
        f"{start_date} - {end_date}"
    )

    gw_df["KO"] = (
        gw_df["kickoff_time"]
        .dt.strftime("%H:%M")
    )

    fixture_view = gw_df[
        [
            "Home",
            "KO",
            "Away"
        ]
    ]

    st.dataframe(
        fixture_view,
        hide_index=True,
        use_container_width=True
    )

except Exception as e:

    st.error(
        f"Error: {e}"
    )
