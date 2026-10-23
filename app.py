import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="FPL Fixtures",
    page_icon="⚽",
    layout="wide"
)

# =========================
# FIXTURES FUNCTION
# =========================
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


def show_fixtures():

    st.title("⚽ FPL Fixtures")

    try:

        bootstrap, fixtures = load_data()

        teams = pd.DataFrame(bootstrap["teams"])
        fixture_df = pd.DataFrame(fixtures)

        team_lookup = dict(
            zip(
                teams["id"],
                teams["name"]
            )
        )

        fixture_df["Home"] = fixture_df["team_h"].map(team_lookup)
        fixture_df["Away"] = fixture_df["team_a"].map(team_lookup)

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
            ["Home", "KO", "Away"]
        ]

        st.dataframe(
            fixture_view,
            hide_index=True,
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Error: {e}")


# =========================
# SIDEBAR
# =========================
menu = st.sidebar.radio(
    "📋 Menu",
    [
        "Fixtures",
        "League Info",
        "Standings",
        "Statistics",
        "Captain Picks",
        "Awards"
    ]
)

# =========================
# PAGES
# =========================
if menu == "Fixtures":
    show_fixtures()

elif menu == "League Info":
    st.title("🏆 League Info")
    st.info("FPL League ID: 147447")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("League ID", "147447")

    with col2:
        st.metric("Status", "Active")

elif menu == "Standings":

    st.title("📊 Standings")

    LEAGUE_ID = 147447

    try:

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        standings = pd.DataFrame(
            league["standings"]["results"]
        )

        table = standings[
            [
                "rank",
                "entry_name",
                "player_name",
                "total"
            ]
        ].copy()

        table.columns = [
            "Rank",
            "Team",
            "Manager",
            "Points"
        ]

        st.subheader(
            "League Table"
        )

        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True
        )

        st.subheader(
            "Top 5 Teams"
        )

        st.bar_chart(
            table.head(5).set_index(
                "Team"
            )["Points"]
        )

    except Exception as e:

        st.error(
            f"Error loading standings: {e}"
        )
elif menu == "Statistics":

    st.title("📈 Player Statistics")

    try:

        bootstrap = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/",
            timeout=20
        ).json()

        players = pd.DataFrame(
            bootstrap["elements"]
        )

        stat_options = {
            "Goals": "goals_scored",
            "Assists": "assists",
            "Clean Sheets": "clean_sheets",
            "Minutes": "minutes",
            "Bonus Points": "bonus",
            "ICT Index": "ict_index",
            "Influence": "influence",
            "Creativity": "creativity",
            "Threat": "threat",
            "Dream Team": "dreamteam_count",
            "Yellow Cards": "yellow_cards",
            "Red Cards": "red_cards",
            "Saves": "saves"
        }

        selected_stat = st.selectbox(
            "Select Statistic",
            list(stat_options.keys())
        )

        stat_col = stat_options[
            selected_stat
        ]

        stats_df = players[
            [
                "web_name",
                stat_col
            ]
        ].copy()

        stats_df.columns = [
            "Player",
            selected_stat
        ]

        stats_df = stats_df.sort_values(
            selected_stat,
            ascending=False
        ).head(20)

        st.subheader(
            f"Top 20 - {selected_stat}"
        )

        st.dataframe(
            stats_df,
            hide_index=True,
            use_container_width=True
        )

        st.bar_chart(
            stats_df.set_index(
                "Player"
            )[selected_stat]
        )

    except Exception as e:

        st.error(
            f"Error loading statistics: {e}"
        )

elif menu == "Captain Picks":

    st.title("🧢 Captain Picks")

    LEAGUE_ID = 147447

    try:

        bootstrap = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/",
            timeout=20
        ).json()

        current_gw = next(
            event["id"]
            for event in bootstrap["events"]
            if event["is_current"]
        )

        players = pd.DataFrame(
            bootstrap["elements"]
        )

        player_lookup = dict(
            zip(
                players["id"],
                players["web_name"]
            )
        )

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        entries = league["standings"]["results"]

        captain_data = []

        with st.spinner(
            "Loading captain picks..."
        ):

            for manager in entries:

                try:

                    entry_id = manager["entry"]

                    picks = requests.get(
                        f"https://fantasy.premierleague.com/api/entry/{entry_id}/event/{current_gw}/picks/",
                        timeout=20
                    ).json()

                    captain = next(
                        p
                        for p in picks["picks"]
                        if p["is_captain"]
                    )

                    captain_data.append(
                        {
                            "Team": manager["entry_name"],
                            "Captain": player_lookup.get(
                                captain["element"],
                                "Unknown"
                            ),
                            "Manager": manager["player_name"]
                        }
                    )

                except:
                    pass

        captain_df = pd.DataFrame(
            captain_data
        )

        st.subheader(
            f"Captain Picks GW {current_gw}"
        )

        st.dataframe(
            captain_df[
                [
                    "Team",
                    "Captain",
                    "Manager"
                ]
            ],
            hide_index=True,
            use_container_width=True
        )

        st.subheader(
            "Most Selected Captains"
        )

        popularity = (
            captain_df["Captain"]
            .value_counts()
            .reset_index()
        )

        popularity.columns = [
            "Captain",
            "Selected"
        ]

        st.dataframe(
            popularity,
            hide_index=True,
            use_container_width=True
        )

        st.bar_chart(
            popularity.set_index(
                "Captain"
            )["Selected"]
        )

    except Exception as e:

        st.error(
            f"Error loading captain picks: {e}"
        )

elif menu == "Awards":
    st.title("🏅 Awards")
    st.write("Penghargaan liga.")
