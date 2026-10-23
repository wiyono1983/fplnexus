import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from io import BytesIO

 
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

    LEAGUE_ID = 147447

    try:

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        standings = pd.DataFrame(
            league["standings"]["results"]
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "League ID",
                LEAGUE_ID
            )

        with col2:
            st.metric(
                "Members",
                len(standings)
            )

        members = []

        progress = st.progress(0)

        for idx, row in standings.iterrows():

            try:

                entry_id = row["entry"]

                history = requests.get(
                    f"https://fantasy.premierleague.com/api/entry/{entry_id}/history/",
                    timeout=20
                ).json()

                current = history.get(
                    "current",
                    []
                )

                latest_gw = (
                    current[-1]
                    if current
                    else {}
                )

                gw_points = latest_gw.get(
                    "points",
                    0
                )

                hits = latest_gw.get(
                    "event_transfers_cost",
                    0
                )

                team_value = (
                    latest_gw.get(
                        "value",
                        0
                    ) / 10
                )

                rank_change = (
                    row["last_rank"]
                    - row["rank"]
                )

                chips = history.get(
                    "chips",
                    []
                )

                used_chips = {
                    chip["name"]
                    for chip in chips
                }

                remaining = []

                if "wildcard" not in used_chips:
                    remaining.append("WC")

                if "freehit" not in used_chips:
                    remaining.append("FH")

                if "bboost" not in used_chips:
                    remaining.append("BB")

                if "3xc" not in used_chips:
                    remaining.append("TC")

                remaining_chips = (
                    ", ".join(remaining)
                    if remaining
                    else "-"
                )

                members.append(
                    {
                        "Rank": row["rank"],
                        "Δ Rank": rank_change,
                        "Team": row["entry_name"],
                        "Manager": row["player_name"],
                        "Team ID": entry_id,
                        "Points": row["total"],
                        "GW Points": gw_points,
                        "Hits": hits,
                        "Remaining Chips": remaining_chips,
                        "Team Value": team_value
                    }
                )

                progress.progress(
                    (idx + 1) / len(standings)
                )

            except:
                pass

        progress.empty()

        league_df = pd.DataFrame(members)

        display_df = league_df.copy()

        display_df["Δ Rank"] = display_df["Δ Rank"].apply(
            lambda x:
            f"▲{x}" if x > 0
            else (
                f"▼{abs(x)}"
                if x < 0
                else "▬"
            )
        )

        display_df["Hits"] = display_df["Hits"].apply(
            lambda x:
            f"-{x}"
            if x > 0
            else "0"
        )

        display_df["Team Value"] = display_df["Team Value"].apply(
            lambda x:
            f"£{x:.1f}m"
        )

        st.subheader("League Members")

        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.subheader("🏅 Awards Snapshot")

        leader = league_df.sort_values("Rank").iloc[0]

        gw_winner = league_df.sort_values(
            "GW Points",
            ascending=False
        ).iloc[0]

        biggest_hit = league_df.sort_values(
            "Hits",
            ascending=False
        ).iloc[0]

        richest = league_df.sort_values(
            "Team Value",
            ascending=False
        ).iloc[0]

        biggest_climber = league_df.sort_values(
            "Δ Rank",
            ascending=False
        ).iloc[0]

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "👑 Leader",
                leader["Team"]
            )

        with col2:
            st.metric(
                "🎯 GW Winner",
                gw_winner["Team"]
            )

        with col3:
            st.metric(
                "💥 Biggest Hit",
                biggest_hit["Team"]
            )

        with col4:
            st.metric(
                "💰 Richest Squad",
                richest["Team"]
            )

        with col5:
            st.metric(
                "🚀 Biggest Climber",
                biggest_climber["Team"]
            )

        st.divider()

        st.subheader("📷 Export League Table")

        selected_columns = st.multiselect(
            "Select Columns",
            display_df.columns.tolist(),
            default=[
                "Rank",
                "Δ Rank",
                "Team",
                "Points",
                "GW Points",
                "Hits",
                "Remaining Chips"
            ]
        )

        if selected_columns:

            export_df = display_df[selected_columns]

            fig_height = max(
                2,
                len(export_df) * 0.45
            )

            fig_width = 14

            fig, ax = plt.subplots(
                figsize=(fig_width, fig_height)
            )

            ax.axis("off")

            # Fixed FPL-style column widths
            width_map = {
                "Rank": 0.08,
                "Δ Rank": 0.08,
                "Team": 0.18,
                "Points": 0.12,
                "GW Points": 0.12,
                "Hits": 0.08,
                "Remaining Chips": 0.22
            }

            col_widths = [
                width_map.get(col, 0.15)
                for col in export_df.columns
            ]

            
            table = ax.table(
                cellText=export_df.values,
                colLabels=export_df.columns,
                colWidths=col_widths,
                loc="center"
            )

            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)

            for (row, col), cell in table.get_celld().items():

                cell.set_edgecolor("#444444")
                cell.set_linewidth(0.75)

                if row == 0:

                    cell.set_facecolor("#2E7D32")

                    cell.set_text_props(
                        color="white",
                        weight="bold",
                        ha="center"
                    )

                else:

                    column = export_df.columns[col]

                    if column in [
                        "Team",
                        "Manager",
                        "Remaining Chips"
                    ]:
                        cell.set_text_props(
                            ha="left"
                        )
                    else:
                        cell.set_text_props(
                            ha="center"
                        )

            plt.tight_layout()

            img_buffer = BytesIO()

            plt.savefig(
                img_buffer,
                format="jpg",
                dpi=300,
                bbox_inches="tight",
                facecolor="white"
            )

            img_buffer.seek(0)

            st.image(
                img_buffer,
                caption="League Table Preview"
            )

            st.download_button(
                label="📥 Download JPG",
                data=img_buffer,
                file_name="league_table.jpg",
                mime="image/jpeg"
            )

            plt.close()

    except Exception as e:

        st.error(
            f"Error loading league info: {e}"
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
