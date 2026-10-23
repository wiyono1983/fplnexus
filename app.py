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
        "Home",
        "Fixtures",
        "My Team",
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
if menu == "Home":

    st.title("⚽ FPL NEXUS")

    st.markdown(
        """
        ### Welcome to FPL Nexus

        All-in-one Fantasy Premier League dashboard
        for fixtures, team analysis, captain picks,
        league standings and transfer planning.
        """
    )

    st.divider()

    try:

        bootstrap = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/",
            timeout=20
        ).json()

        current_gw = next(
            e["id"]
            for e in bootstrap["events"]
            if e["is_current"]
        )

        top_player = max(
            bootstrap["elements"],
            key=lambda x: x["total_points"]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current GW",
                current_gw
            )

        with col2:
            st.metric(
                "Players",
                len(
                    bootstrap["elements"]
                )
            )

        with col3:
            st.metric(
                "Teams",
                len(
                    bootstrap["teams"]
                )
            )

        st.divider()

        st.subheader(
            "🏆 Season Highlights"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.info(
                f"""
                ⭐ Top Scorer

                {top_player['web_name']}

                {top_player['total_points']} pts
                """
            )

        with col2:
            st.info(
                """
                🏆 League

                League ID: 147447

                Status: Active
                """
            )

        st.divider()

        st.subheader(
            "🚀 Quick Features"
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.success(
                """
                📅 Fixtures

                View all upcoming gameweek fixtures
                and kick-off times.
                """
            )

        with c2:
            st.success(
                """
                👤 My Team

                Analyze your squad and get
                transfer recommendations.
                """
            )

        with c3:
            st.success(
                """
                🏆 Standings

                Follow league rankings
                and top managers.
                """
            )

        st.divider()

        st.subheader(
            "🔥 Available Modules"
        )

        features = pd.DataFrame(
            {
                "Feature": [
                    "Fixtures",
                    "My Team",
                    "Standings",
                    "Statistics",
                    "Captain Picks",
                    "Awards"
                ],
                "Status": [
                    "✅ Ready",
                    "✅ Ready",
                    "✅ Ready",
                    "✅ Ready",
                    "✅ Ready",
                    "✅ Ready"
                ]
            }
        )

        st.dataframe(
            features,
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.caption(
            f"Currently viewing Gameweek {current_gw}"
        )

    except Exception as e:

        st.error(
            f"Unable to load dashboard: {e}"
        )

elif menu == "Fixtures":
    show_fixtures()

elif menu == "League Info":
    st.title("🏆 League Info")
    st.info("FPL League ID: 147447")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("League ID", "147447")

    with col2:
        st.metric("Status", "Active")

elif menu == "My Team":

    st.title("👤 My Team")

    entry_id = st.number_input(
        "Enter FPL Team ID",
        min_value=1,
        step=1
    )

    if entry_id:

        try:

            bootstrap = requests.get(
                "https://fantasy.premierleague.com/api/bootstrap-static/",
                timeout=20
            ).json()

            current_gw = next(
                e["id"]
                for e in bootstrap["events"]
                if e["is_current"]
            )

            players = pd.DataFrame(
                bootstrap["elements"]
            )

            positions = {
                1: "GK",
                2: "DEF",
                3: "MID",
                4: "FWD"
            }

            # Get bank
            entry_data = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_id}/",
                timeout=20
            ).json()

            bank = (
                entry_data.get(
                    "last_deadline_bank",
                    0
                ) / 10
            )

            # Squad
            picks = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_id}/event/{current_gw}/picks/",
                timeout=20
            ).json()

            squad = []

            for p in picks["picks"]:

                player = players[
                    players["id"] == p["element"]
                ].iloc[0]

                squad.append(
                    {
                        "Player": player["web_name"],
                        "Position": positions[
                            player["element_type"]
                        ],
                        "Club": player["team"],
                        "Price": player["now_cost"] / 10,
                        "Points": player["total_points"],
                        "Form": float(
                            player["form"]
                        ) if player["form"] else 0
                    }
                )

            squad_df = pd.DataFrame(
                squad
            )

            current_squad = (
                squad_df["Player"]
                .tolist()
            )

            club_counts = (
                squad_df["Club"]
                .value_counts()
                .to_dict()
            )

            st.subheader(
                f"My Squad - GW {current_gw}"
            )

            st.dataframe(
                squad_df[
                    [
                        "Player",
                        "Position",
                        "Price",
                        "Points",
                        "Form"
                    ]
                ],
                hide_index=True,
                use_container_width=True
            )

            st.divider()

            st.subheader(
                "🔄 Transfer Planner"
            )

            sell_player = st.selectbox(
                "Player to Sell",
                squad_df["Player"]
            )

            selected = squad_df[
                squad_df["Player"]
                == sell_player
            ].iloc[0]

            # Kurangi kuota klub pemain yg dijual
            club_counts[
                selected["Club"]
            ] -= 1

            available_budget = (
                selected["Price"]
                + bank
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Player Sold",
                    sell_player
                )

            with col2:
                st.metric(
                    "Sell Price",
                    f"£{selected['Price']:.1f}m"
                )

            with col3:
                st.metric(
                    "Bank",
                    f"£{bank:.1f}m"
                )

            with col4:
                st.metric(
                    "Budget",
                    f"£{available_budget:.1f}m"
                )

            pos_map = {
                "GK": 1,
                "DEF": 2,
                "MID": 3,
                "FWD": 4
            }

            pos_id = pos_map[
                selected["Position"]
            ]

            candidates = players[
                players["element_type"]
                == pos_id
            ].copy()

            candidates["Price"] = (
                candidates["now_cost"]
                / 10
            )

            candidates["Club"] = (
                candidates["team"]
            )

            candidates["Form"] = (
                pd.to_numeric(
                    candidates["form"],
                    errors="coerce"
                ).fillna(0)
            )

            candidates["Value"] = (
                candidates["total_points"]
                / candidates["Price"]
            ).round(2)

            # Budget filter
            candidates = candidates[
                candidates["Price"]
                <= available_budget
            ]

            # Exclude existing squad
            candidates = candidates[
                ~candidates["web_name"]
                .isin(current_squad)
            ]

            # Max 3 players per club
            candidates = candidates[
                candidates.apply(
                    lambda x:
                    club_counts.get(
                        x["Club"],
                        0
                    ) < 3,
                    axis=1
                )
            ]

            ranking = st.selectbox(
                "Rank By",
                [
                    "Points",
                    "Form",
                    "Value"
                ]
            )

            if ranking == "Points":

                candidates = (
                    candidates
                    .sort_values(
                        "total_points",
                        ascending=False
                    )
                )

            elif ranking == "Form":

                candidates = (
                    candidates
                    .sort_values(
                        "Form",
                        ascending=False
                    )
                )

            else:

                candidates = (
                    candidates
                    .sort_values(
                        "Value",
                        ascending=False
                    )
                )

            suggestions = candidates[
                [
                    "web_name",
                    "Price",
                    "total_points",
                    "Form",
                    "Value"
                ]
            ].head(10)

            suggestions.columns = [
                "Player",
                "Price",
                "Points",
                "Form",
                "Value"
            ]

            st.subheader(
                f"🔥 Best {selected['Position']} Replacements"
            )

            st.dataframe(
                suggestions,
                hide_index=True,
                use_container_width=True
            )

            if not suggestions.empty:

                best = suggestions.iloc[0]

                st.success(
                    f"✅ Suggested Transfer: "
                    f"{sell_player} ➜ "
                    f"{best['Player']} "
                    f"(£{best['Price']:.1f}m | "
                    f"{best['Points']} pts)"
                )

                st.bar_chart(
                    suggestions.set_index(
                        "Player"
                    )["Points"]
                )

        except Exception as e:

            st.error(
                f"Error loading team: {e}"
            )



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
