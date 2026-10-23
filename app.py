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
    st.write("Klasemen FPL League akan ditampilkan di sini.")

elif menu == "Statistics":
    st.title("📈 Statistics")
    st.write("Statistik league.")

elif menu == "Captain Picks":
    st.title("🧢 Captain Picks")
    st.write("Captain terpopuler.")
    elif menu == "Captain Picks":

    st.title("🧢 Captain Picks")

    LEAGUE_ID = 147447

    try:

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        entries = league["standings"]["results"]

        gw = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/",
            timeout=20
        ).json()["events"]

        current_gw = next(
            e["id"]
            for e in gw
            if e["is_current"]
        )

        captain_data = []

        progress = st.progress(0)

        for i, manager in enumerate(entries):

            entry_id = manager["entry"]

            picks = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_id}/event/{current_gw}/picks/",
                timeout=20
            ).json()

            captain_pick = next(
                p for p in picks["picks"]
                if p["is_captain"]
            )

            player_id = captain_pick["element"]

            captain_data.append(
                {
                    "Manager": manager["player_name"],
                    "Captain ID": player_id
                }
            )

            progress.progress(
                (i + 1) / len(entries)
            )

        teams = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/",
            timeout=20
        ).json()

        players = pd.DataFrame(
            teams["elements"]
        )

        player_lookup = dict(
            zip(
                players["id"],
                players["web_name"]
            )
        )

        captain_df = pd.DataFrame(
            captain_data
        )

        captain_df["Captain"] = (
            captain_df["Captain ID"]
            .map(player_lookup)
        )

        st.subheader(
            f"Captain Picks - GW {current_gw}"
        )

        st.dataframe(
            captain_df[
                ["Manager", "Captain"]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.subheader(
            "Captain Popularity"
        )

        popularity = (
            captain_df["Captain"]
            .value_counts()
            .reset_index()
        )

        popularity.columns = [
            "Player",
            "Managers"
        ]

        st.dataframe(
            popularity,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            popularity.set_index(
                "Player"
            )["Managers"]
        )

    except Exception as e:

        st.error(f"Error: {e}")


elif menu == "Awards":
    st.title("🏅 Awards")
    st.write("Penghargaan liga.")
