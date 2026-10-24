import streamlit as st
import pandas as pd
import yfinance as yf
import os
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
              fixture_df["team_h"]
              .map(team_lookup)
           )

           fixture_df["Away"] = (
              fixture_df["team_a"]
              .map(team_lookup)
           )

           fixture_df["kickoff_time"] = (
               pd.to_datetime(
                  fixture_df["kickoff_time"],
                  utc=True,
                  errors="coerce"
            )
              .dt.tz_convert(
                "Asia/Jakarta"
              )
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

           now = pd.Timestamp.now(
              tz="Asia/Jakarta"
           )

           def get_status(row):

               kickoff = row[
                  "kickoff_time"
               ]

               if pd.isna(kickoff):
                   return "-"

               diff_hours = (
                   now - kickoff
               ).total_seconds() / 3600

               if row.get(
                   "finished",
                   False
               ):
                   return "FT"

               if (
                   0 <= diff_hours < 2
               ):
                   return "LIVE"

               return kickoff.strftime(
                   "%H:%M"
               )

           gw_df["Kick Off"] = (
               gw_df.apply(
                  get_status,
                  axis=1
               )
            )

           gw_df["Score"] = gw_df.apply(
               lambda x:
               f"{int(x['team_h_score'])}-{int(x['team_a_score'])}"
               if pd.notna(
                   x["team_h_score"]
               )
               and pd.notna(
                   x["team_a_score"]
               )
               else "vs",
               axis=1
            )

           fixture_view = gw_df[
              [
                  "Kick Off",
                  "Home",
                  "Score",
                  "Away"
              ]
            ].copy()

           fixture_view.columns = [
              "Status",
              "Home Team",
              "Score",
              "Away Team"
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


        

# =========================
# SIDEBAR
# =========================

menu = st.sidebar.radio(
    "📋 Menu",
    ["Saham", "FPL"]
)

if menu == "Saham":

    submenu = st.sidebar.radio(
        "Menu Saham",
        [
            "IDX Nexus",
            "Value Screener",
            "Price Momentum",
            "Dividend Momentum",
            "Right Issue Calc",
            "MyPorto"
        ]
    )

else:

    submenu = st.sidebar.radio(
        "Menu FPL",
        [
            "Home",
            "Fixtures",
            "My Team",
            "Best XI",
            "League Info",
            "Standings",
            "Statistics",
            "Captain Picks",
            "Rival Analyzer",
            "Transfer Activity",
            "Transfer Trends"
        ]
    )

menu = submenu



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

elif menu == "My Team":

    st.title("👤 My Team")

    LEAGUE_ID = 147447

    lookup_method = st.radio(
       "Lookup Method",
        [
           "Team Name",
           "FPL Team ID"
        ],
        horizontal=True
    )

    if lookup_method == "Team Name":

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        standings = pd.DataFrame(
            league["standings"]["results"]
        )
 
        team_options = sorted(
           standings["entry_name"].tolist()
        )

        selected_team = st.selectbox(
           "🏆 Select Team",
           team_options
        )

        entry_id = standings.loc[
            standings["entry_name"]
            == selected_team,
            "entry"
        ].iloc[0]

    else:

        entry_id = st.number_input(
            "FPL Team ID",
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

            team_name = entry_data.get(
                "name",
                "Unknown"
            )

            manager_name = (
               f"{entry_data.get('player_first_name', '')} "
               f"{entry_data.get('player_last_name', '')}"
            ).strip()


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

            col1, col2, col3 = st.columns(3)

            with col1:
                 st.metric(
                   "🏆 Team",
                   team_name
                 )

            with col2:
                 st.metric(
                   "👤 Manager",
                   manager_name
                 )

            with col3:
                st.metric(
                  "🆔 Team ID",
                  entry_id
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
              "⚔️ Compare 2 Players To Sell"
            )

            col1, col2 = st.columns(2)

            with col1:

              compare_1 = st.selectbox(
                 "Player 1",
                 squad_df["Player"],
                 key="compare_1"
              )

            with col2:

               compare_2 = st.selectbox(
                 "Player 2",
                 squad_df["Player"],
                 index=1 if len(squad_df) > 1 else 0,
                 key="compare_2"
             )

            if compare_1 != compare_2:

               p1 = squad_df[
                 squad_df["Player"] == compare_1
               ].iloc[0]
 
               p2 = squad_df[
                 squad_df["Player"] == compare_2
               ].iloc[0]

               compare_df = pd.DataFrame(
               [
                {
                  "Metric": "Price",
                  compare_1: p1["Price"],
                  compare_2: p2["Price"]
                },
                {
                  "Metric": "Points",
                  compare_1: p1["Points"],
                  compare_2: p2["Points"]
                },
                {
                  "Metric": "Form",
                  compare_1: p1["Form"],
                  compare_2: p2["Form"]
                }
               ]
          )

            st.dataframe(
                 compare_df,
                 hide_index=True,
                 use_container_width=True
             )

            sell_score_1 = 0
            sell_score_2 = 0

            if p1["Points"] < p2["Points"]:
                sell_score_1 += 1
            else:
                sell_score_2 += 1

            if p1["Form"] < p2["Form"]:
                sell_score_1 += 1
            else:
                sell_score_2 += 1

            if p1["Price"] > p2["Price"]:
                sell_score_1 += 1
            else:
                sell_score_2 += 1

            st.subheader(
               "🚨 Recommendation"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                   compare_1,
                   f"{sell_score_1}/3"
                )

            with col2:

                st.metric(
                   compare_2,
                   f"{sell_score_2}/3"
                )

            if sell_score_1 > sell_score_2:

                st.error(
                   f"""
              Recommended Sell

              ❌ {compare_1}

              Reason:
              Lower overall value compared with {compare_2}.
              """
              )

            elif sell_score_2 > sell_score_1:

                st.error(
                  f"""
              Recommended Sell

              ❌ {compare_2}

              Reason:
              Lower overall value compared with {compare_1}.
              """
              )

            else:

                st.warning(
                  """
                Both players have similar profile.

                Consider using fixtures or personal preference
                as the deciding factor.
                """
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

            candidates["Ownership"] = pd.to_numeric(
                candidates["selected_by_percent"],
                errors="coerce"
            ).fillna(100)


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
                    "Value",
                    "Differential"
                ]
            )

            if ranking == "Points":

               candidates = candidates.sort_values(
                   "total_points",
                   ascending=False
              )

            elif ranking == "Form":

               candidates = candidates.sort_values(
                   "Form",
                   ascending=False
            )

            elif ranking == "Value":

               candidates = candidates.sort_values(
                   "Value",
                   ascending=False
            )

            else:

               candidates = candidates[
                  candidates["Ownership"] < 10
                  ].sort_values(
                  "Form",
                  ascending=False
            )


            suggestions = candidates[
                [
                    "web_name",
                    "Price",
                    "total_points",
                    "Form",
                    "Value",
                    "Ownership"
                ]
            ].head(10)

            suggestions.columns = [
                "Player",
                "Price",
                "Points",
                "Form",
                "Value",
                "Own %"
            ]

            st.subheader(
                f"🔥 Best {selected['Position']} Replacements"
            )

            st.dataframe(
                suggestions,
                hide_index=True,
                use_container_width=True
            )

            
            if not candidates.empty:

                points_pick = (
                    candidates
                    .sort_values(
                        "total_points",
                        ascending=False
                    )
                    .iloc[0]
                )

                form_pick = (
                    candidates
                    .sort_values(
                        "Form",
                        ascending=False
                    )
                    .iloc[0]
                )

                value_pick = (
                    candidates
                    .sort_values(
                        "Value",
                        ascending=False
                    )
                    .iloc[0]
                )

                diff_pool = candidates[
                    candidates["Ownership"] < 10
                ]

                if not diff_pool.empty:

                    diff_pick = (
                        diff_pool
                        .sort_values(
                            "Form",
                            ascending=False
                        )
                        .iloc[0]
                    )

                else:

                    diff_pick = form_pick

                recommended = form_pick

                remaining_budget = (
                    available_budget
                    - recommended["Price"]
                )

                st.success(
                    f"""
                ✅ Suggested Transfer

                {sell_player}
                ➡️
                {recommended['web_name']}

                Buy Price:
                £{recommended['Price']:.1f}m

                Remaining Budget:
                £{remaining_budget:.1f}m
                """
                )

                report = f"""
⚽ FPL NEXUS TRANSFER REPORT

   SELL PLAYER
     ❌ {sell_player}

   Sell Price: £{selected['Price']:.1f}m
   Current Bank: £{bank:.1f}m
   Available Budget: £{available_budget:.1f}m

   🏆 POINTS PICK
      {points_pick['web_name']}
      {points_pick['total_points']} pts

   🔥 FORM PICK
      {form_pick['web_name']}
      Form {form_pick['Form']}

   💰 VALUE PICK
      {value_pick['web_name']}
      Value {value_pick['Value']}

   🎯 DIFFERENTIAL PICK
      {diff_pick['web_name']}
      Ownership {diff_pick['Ownership']}%

 ✅ RECOMMENDED TRANSFER
    OUT: {sell_player}
    IN : {recommended['web_name']}
                
    Buy Price : £{recommended['Price']:.1f}m
    Remaining Budget: £{remaining_budget:.1f}m
"""

                st.subheader(
                    "📱 Copy To WhatsApp"
                )

                st.code(
                    report,
                    language="text"
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
                "Rank": 0.03,
                "Δ Rank": 0.08,
                "Team": 0.18,
                "Points": 0.07,
                "GW Points": 0.07,
                "Hits": 0.03,
                "Remaining Chips": 0.12,
                "Manager" : 0.20,
                "Team Value" : 0.10
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

elif menu == "Transfer Activity":

    st.title("🔄 Transfer Activity")

    LEAGUE_ID = 147447

    lookup_method = st.radio(
        "Lookup Method",
        [
            "Team Name",
            "FPL Team ID"
        ],
        horizontal=True
    )

    if lookup_method == "Team Name":

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        standings = pd.DataFrame(
            league["standings"]["results"]
        )

        team_options = sorted(
            standings["entry_name"].tolist()
        )

        selected_team = st.selectbox(
            "🏆 Select Team",
            team_options
        )

        entry_id = standings.loc[
            standings["entry_name"]
            == selected_team,
            "entry"
        ].iloc[0]

    else:

        entry_id = st.number_input(
            "FPL Team ID",
            min_value=1,
            step=1
        )

    if entry_id:

        try:

            bootstrap = requests.get(
                "https://fantasy.premierleague.com/api/bootstrap-static/",
                timeout=20
            ).json()

            players = pd.DataFrame(
                bootstrap["elements"]
            )

            player_lookup = dict(
                zip(
                    players["id"],
                    players["web_name"]
                )
            )

            current_gw = next(
                e["id"]
                for e in bootstrap["events"]
                if e["is_current"]
            )

            selected_gw = st.selectbox(
                "Gameweek",
                list(range(1, current_gw + 2))
            )

            entry_data = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_id}/",
                timeout=20
            ).json()

            team_name = entry_data.get(
                "name",
                "Unknown"
            )

            manager_name = (
                f"{entry_data.get('player_first_name', '')} "
                f"{entry_data.get('player_last_name', '')}"
            ).strip()

            bank = (
                entry_data.get(
                    "last_deadline_bank",
                    0
                ) / 10
            )

            active_chip = "None"

            try:

                picks = requests.get(
                    f"https://fantasy.premierleague.com/api/entry/{entry_id}/event/{selected_gw}/picks/",
                    timeout=20
                ).json()

                active_chip = (
                    picks.get(
                        "active_chip"
                    )
                    or "None"
                )

            except:
                pass

            transfers_data = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_id}/transfers/",
                timeout=20
            ).json()

            gw_transfers = [
                t
                for t in transfers_data
                if t["event"] == selected_gw
            ]

            st.subheader(
                f"GW{selected_gw} Transfer Activity"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "🏆 Team",
                    team_name
                )

            with col2:
                st.metric(
                    "👤 Manager",
                    manager_name
                )

            with col3:
                st.metric(
                    "🆔 Team ID",
                    entry_id
                )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "💰 Bank",
                    f"£{bank:.1f}m"
                )

            with col2:
                st.metric(
                    "🔄 Transfers",
                    len(gw_transfers)
                )

            with col3:
                st.metric(
                    "🎯 Active Chip",
                    active_chip
                )

            if gw_transfers:

                rows = []

                for transfer in gw_transfers:

                    rows.append(
                        {
                            "Date": (
                                transfer["time"][:16]
                                .replace(
                                    "T",
                                    " "
                                )
                            ),
                            "OUT": player_lookup.get(
                                transfer["element_out"],
                                "Unknown"
                            ),
                            "IN": player_lookup.get(
                                transfer["element_in"],
                                "Unknown"
                            )
                        }
                    )

                transfer_df = pd.DataFrame(
                    rows
                )

                st.dataframe(
                    transfer_df,
                    hide_index=True,
                    use_container_width=True
                )

                whatsapp_report = (
                    f"⚽ FPL NEXUS GW{selected_gw}\n\n"
                    f"Team: {team_name}\n"
                    f"Manager: {manager_name}\n"
                    f"Team ID: {entry_id}\n\n"
                    f"Bank: £{bank:.1f}m\n"
                    f"Chip: {active_chip}\n"
                    f"Transfers: {len(gw_transfers)}\n\n"
                )

                for _, row in transfer_df.iterrows():

                    whatsapp_report += (
                        f"OUT: {row['OUT']}\n"
                        f"IN : {row['IN']}\n\n"
                    )

                st.subheader(
                    "📱 Copy To WhatsApp"
                )

                st.code(
                    whatsapp_report,
                    language="text"
                )

            else:

                st.info(
                    f"No transfers recorded for GW{selected_gw}."
                )

        except Exception as e:

            st.error(
                f"Error loading transfers: {e}"
            )


elif menu == "Best XI":

    st.title("🔥 Best XI")

    LEAGUE_ID = 147447

    lookup_method = st.radio(
        "Lookup Method",
        [
            "Team Name",
            "FPL Team ID"
        ],
        horizontal=True
    )

    if lookup_method == "Team Name":

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        standings = pd.DataFrame(
            league["standings"]["results"]
        )

        team_options = sorted(
            standings["entry_name"].tolist()
        )

        selected_team = st.selectbox(
            "🏆 Select Team",
            team_options
        )

        entry_id = standings.loc[
            standings["entry_name"]
            == selected_team,
            "entry"
        ].iloc[0]

    else:

        entry_id = st.number_input(
            "FPL Team ID",
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

            entry_data = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_id}/",
                timeout=20
            ).json()

            team_name = entry_data.get(
                "name",
                "Unknown"
            )

            manager_name = (
                f"{entry_data.get('player_first_name', '')} "
                f"{entry_data.get('player_last_name', '')}"
            ).strip()

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
                        "Points": player["total_points"],
                        "Form": float(
                            player["form"]
                        ) if player["form"] else 0
                    }
                )

            squad_df = pd.DataFrame(
                squad
            )

            gk_df = squad_df[
                squad_df["Position"] == "GK"
            ].sort_values(
                "Form",
                ascending=False
            )

            def_df = squad_df[
                squad_df["Position"] == "DEF"
            ].sort_values(
                "Form",
                ascending=False
            )

            mid_df = squad_df[
                squad_df["Position"] == "MID"
            ].sort_values(
                "Form",
                ascending=False
            )

            fwd_df = squad_df[
                squad_df["Position"] == "FWD"
            ].sort_values(
                "Form",
                ascending=False
            )

            valid_formations = [
                (3,4,3),
                (3,5,2),
                (4,4,2),
                (4,3,3),
                (4,5,1),
                (5,4,1),
                (5,3,2),
                (5,2,3)
            ]

            best_score = -1
            best_xi = None
            best_formation = None

            for d, m, f in valid_formations:

                if (
                    len(def_df) < d
                    or len(mid_df) < m
                    or len(fwd_df) < f
                ):
                    continue

                xi = pd.concat(
                    [
                        gk_df.head(1),
                        def_df.head(d),
                        mid_df.head(m),
                        fwd_df.head(f)
                    ]
                )

                score = xi["Form"].sum()

                if score > best_score:

                    best_score = score
                    best_xi = xi.copy()
                    best_formation = (
                        f"{d}-{m}-{f}"
                    )

            bench = squad_df[
                ~squad_df["Player"].isin(
                    best_xi["Player"]
                )
            ]

            st.success(
                f"""
🏆 Team: {team_name}

👤 Manager: {manager_name}

✅ Best Formation: {best_formation}

🔥 Total Form Score: {best_score:.1f}
"""
            )

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "✅ Starting XI"
                )

                st.dataframe(
                    best_xi[
                        [
                            "Player",
                            "Position",
                            "Points",
                            "Form"
                        ]
                    ],
                    hide_index=True,
                    use_container_width=True
                )

            with col2:

                st.subheader(
                    "🪑 Bench Order"
                )

                bench = bench.sort_values(
                    "Form",
                    ascending=False
                )

                st.dataframe(
                    bench[
                        [
                            "Player",
                            "Position",
                            "Points",
                            "Form"
                        ]
                    ],
                    hide_index=True,
                    use_container_width=True
                )

            captain = (
                best_xi.sort_values(
                    "Form",
                    ascending=False
                )
                .iloc[0]
            )

            vice = (
                best_xi.sort_values(
                    "Form",
                    ascending=False
                )
                .iloc[1]
            )

            st.info(
                f"""
🧢 Recommended Captain

{captain['Player']}
(Form {captain['Form']})

🎖 Recommended Vice Captain

{vice['Player']}
(Form {vice['Form']})
"""
            )

        except Exception as e:

            st.error(
                f"Error loading squad: {e}"
            )             


elif menu == "IDX Nexus":


    st.title("📈 IDX Nexus")

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum dibuat. Tambahkan saham di menu MyPorto."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    if portfolio_df.empty:

        st.warning(
            "Portfolio kosong."
        )

        st.stop()

    idx_menu = st.radio(
        "Module",
        [
            "Watchlist",
            "Stock Detail",
            "Compare Stocks",
            "Value Screener"
        ],
        horizontal=True
    )

    # ==================================
    # WATCHLIST
    # ==================================

    if idx_menu == "Watchlist":

        rows = []

        for _, row in portfolio_df.iterrows():

            try:

                ticker = (
                    str(
                        row["Ticker"]
                    ).upper()
                    + ".JK"
                )

                stock = yf.Ticker(
                    ticker
                )

                hist = stock.history(
                    period="5d"
                )

                if hist.empty:
                    continue

                current = round(
                    hist["Close"]
                    .iloc[-1],
                    2
                )

                prev = round(
                    hist["Close"]
                    .iloc[-2],
                    2
                )

                change_pct = round(
                    (
                        (
                            current
                            - prev
                        )
                        / prev
                    )
                    * 100,
                    2
                )

                shares = (
                    row["Lot"]
                    * 100
                )

                market_value = (
                    current
                    * shares
                )

                cost_value = (
                    row["Avg Buy"]
                    * shares
                )

                pnl = (
                    market_value
                    - cost_value
                )

                pnl_pct = round(
                    (
                        pnl
                        /
                        cost_value
                    )
                    * 100,
                    2
                )

                rows.append(
                    {
                        "Ticker":
                        row["Ticker"],

                        "Lot":
                        row["Lot"],

                        "Avg Buy":
                        row["Avg Buy"],

                        "Current":
                        current,

                        "Day %":
                        change_pct,

                        "P/L":
                        round(
                            pnl
                        ),

                        "P/L %":
                        pnl_pct
                    }
                )

            except Exception:

                continue

        watchlist_df = pd.DataFrame(
            rows
        )

        st.dataframe(
            watchlist_df,
            hide_index=True,
            use_container_width=True
        )

        if not watchlist_df.empty:

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Stocks",
                    len(
                        watchlist_df
                    )
                )

            with col2:

                st.metric(
                    "Top Winner",
                    watchlist_df
                    .sort_values(
                        "P/L %",
                        ascending=False
                    )
                    .iloc[0]["Ticker"]
                )

            with col3:

                st.metric(
                    "Top Loser",
                    watchlist_df
                    .sort_values(
                        "P/L %"
                    )
                    .iloc[0]["Ticker"]
                )

    # ==================================
    # STOCK DETAIL
    # ==================================

    elif idx_menu == "Stock Detail":

        selected = st.selectbox(
            "Stock",
            portfolio_df[
                "Ticker"
            ]
        )

        try:

            stock = yf.Ticker(
                selected
                + ".JK"
            )

            hist = stock.history(
                period="1y"
            )

            if hist.empty:

                st.warning(
                    "Data tidak ditemukan."
                )

            else:

                current = round(
                    hist["Close"]
                    .iloc[-1],
                    2
                )

                high52 = round(
                    hist["High"]
                    .max(),
                    2
                )

                low52 = round(
                    hist["Low"]
                    .min(),
                    2
                )

                volume = int(
                    hist["Volume"]
                    .iloc[-1]
                )

                col1, col2, col3, col4 = st.columns(
                    4
                )

                with col1:

                    st.metric(
                        "Price",
                        current
                    )

                with col2:

                    st.metric(
                        "52W High",
                        high52
                    )

                with col3:

                    st.metric(
                        "52W Low",
                        low52
                    )

                with col4:

                    st.metric(
                        "Volume",
                        f"{volume:,}"
                    )

                st.subheader(
                    "1 Year Chart"
                )

                st.line_chart(
                    hist["Close"]
                )

                st.subheader(
                    "Recent Prices"
                )

                st.dataframe(
                    hist.tail(30),
                    use_container_width=True
                )

        except Exception as e:

            st.error(e)
       
    
            
        
            

     

    # ==================================
    # COMPARE
    # ==================================

    elif idx_menu == "Compare Stocks":

        tickers = (
            portfolio_df[
                "Ticker"
            ]
            .tolist()
        )

        if len(tickers) < 2:

            st.warning(
                "Minimal 2 saham."
            )

        else:

            col1, col2 = st.columns(
                2
            )

            with col1:

                stock1 = st.selectbox(
                    "Stock 1",
                    tickers
                )

            with col2:

                stock2 = st.selectbox(
                    "Stock 2",
                    tickers,
                    index=1
                )

            try:

                hist1 = yf.Ticker(
                    stock1 + ".JK"
                ).history(
                    period="6mo"
                )

                hist2 = yf.Ticker(
                    stock2 + ".JK"
                ).history(
                    period="6mo"
                )

                price1 = round(
                    hist1["Close"]
                    .iloc[-1],
                    2
                )

                price2 = round(
                    hist2["Close"]
                    .iloc[-1],
                    2
                )

                change1 = round(
                    (
                        (
                            price1
                            -
                            hist1["Close"]
                            .iloc[0]
                        )
                        /
                        hist1["Close"]
                        .iloc[0]
                    )
                    * 100,
                    2
                )

                change2 = round(
                    (
                        (
                            price2
                            -
                            hist2["Close"]
                            .iloc[0]
                        )
                        /
                        hist2["Close"]
                        .iloc[0]
                    )
                    * 100,
                    2
                )

                compare_df = pd.DataFrame(
                    [
                        {
                            "Metric":
                            "Price",

                            stock1:
                            price1,

                            stock2:
                            price2
                        },
                        {
                            "Metric":
                            "6M Return %",

                            stock1:
                            change1,

                            stock2:
                            change2
                        }
                    ]
                )

                st.dataframe(
                    compare_df,
                    hide_index=True,
                    use_container_width=True
                )

                chart_df = pd.DataFrame(
                    {
                        stock1:
                        hist1["Close"],

                        stock2:
                        hist2["Close"]
                    }
                )

                st.subheader(
                    "6 Month Comparison"
                )

                st.line_chart(
                    chart_df
                )

            except Exception as e:

                st.error(e)

            
elif menu == "Value Screener":

    st.title("💰 Value Screener")

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    if portfolio_df.empty:

        st.warning(
            "Portfolio kosong."
        )

        st.stop()

    rows = []

    for _, row in portfolio_df.iterrows():

        try:

            ticker = (
                str(
                    row["Ticker"]
                ).upper()
                + ".JK"
            )

            stock = yf.Ticker(
                ticker
            )

            info = stock.info

            current = info.get(
                "currentPrice"
            )

            pe = info.get(
                "trailingPE"
            )

            pbv = info.get(
                "priceToBook"
            )

            dividend = info.get(
                "dividendYield"
            )

            avg_buy = float(
                row["Avg Buy"]
            )

            profit_pct = None

            if current:

                profit_pct = round(
                    (
                        (
                            current
                            - avg_buy
                        )
                        / avg_buy
                    ) * 100,
                    2
                )

            status = "HOLD"

            if (
                pe is not None
                and pbv is not None
            ):

                if (
                    pe < 12
                    and pbv < 1.5
                ):

                    status = "BUY"

                elif (
                    pbv > 4
                    and profit_pct is not None
                    and profit_pct > 30
                ):

                    status = "TAKE PROFIT"

            rows.append(
                {
                    "Ticker":
                    row["Ticker"],

                    "Current":
                    current,

                    "Avg Buy":
                    avg_buy,

                    "Profit %":
                    profit_pct,

                    "PE":
                    pe,

                    "PBV":
                    pbv,

                    "Dividend %":
                    round(
                        dividend * 100,
                        2
                    )
                    if dividend
                    else None,

                    "Status":
                    status
                }
            )

        except Exception as e:

            st.error(
                f"{row['Ticker']} : {e}"
            )

    screen_df = pd.DataFrame(
        rows
    )

    if screen_df.empty:

        st.warning(
            "No data loaded"
        )

    else:

        st.dataframe(
            screen_df,
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.subheader(
            "✅ Buy Candidates"
        )

        buy_df = screen_df[
            screen_df["Status"]
            == "BUY"
        ]

        if buy_df.empty:

            st.info(
                "No buy candidates."
            )

        else:

            st.dataframe(
                buy_df,
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        st.subheader(
            "⚠️ Take Profit Candidates"
        )

        tp_df = screen_df[
            screen_df["Status"]
            == "TAKE PROFIT"
        ]

        if tp_df.empty:

            st.info(
                "No take profit candidates."
            )

        else:

            st.dataframe(
                tp_df,
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        st.subheader(
            "🏆 Lowest PBV"
        )

        cheap_df = (
            screen_df
            .dropna(
                subset=["PBV"]
            )
            .sort_values(
                "PBV"
            )
        )

        st.dataframe(
            cheap_df.head(10),
            hide_index=True,
            use_container_width=True
        )

                        
elif menu == "MyPorto":

    st.title("📁 My Portfolio")

    PORTFOLIO_FILE = "portfolio.csv"

    # Create file first time
    if not os.path.exists(PORTFOLIO_FILE):

        pd.DataFrame(
            columns=[
                "Ticker",
                "Lot",
                "Avg Buy"
            ]
        ).to_csv(
            PORTFOLIO_FILE,
            index=False,
            float_format="%.2f"
        )

    portfolio_df = pd.read_csv(PORTFOLIO_FILE)

    if not portfolio_df.empty:

        portfolio_df["Lot"] = pd.to_numeric(
            portfolio_df["Lot"],
            errors="coerce"
        ).fillna(0).astype(int)

        portfolio_df["Avg Buy"] = pd.to_numeric(
            portfolio_df["Avg Buy"],
            errors="coerce"
        ).fillna(0).astype(float)

    st.subheader("➕ Add / Update Position")

    col1, col2, col3 = st.columns(3)

    with col1:

        ticker = st.text_input(
            "Ticker",
            placeholder="BBCA"
        )

    with col2:

        lot = st.number_input(
            "Lot",
            min_value=1,
            value=100
        )

    with col3:

        avg_buy = st.number_input(
            "Buy Price",
            min_value=0.01,
            value=1000.00,
            step=0.01,
            format="%.2f"
        )

    if st.button("Save Position"):

        ticker = ticker.upper().strip()

        if ticker:

            existing = portfolio_df[
                portfolio_df["Ticker"] == ticker
            ]

            if not existing.empty:

                old_lot = int(
                    existing.iloc[0]["Lot"]
                )

                old_avg = float(
                    existing.iloc[0]["Avg Buy"]
                )

                total_lot = old_lot + lot

                new_avg = (
                    (old_lot * old_avg)
                    +
                    (lot * avg_buy)
                ) / total_lot

                portfolio_df.loc[
                    portfolio_df["Ticker"] == ticker,
                    "Lot"
                ] = total_lot

                portfolio_df.loc[
                    portfolio_df["Ticker"] == ticker,
                    "Avg Buy"
                ] = round(new_avg, 2)

                portfolio_df.to_csv(
                    PORTFOLIO_FILE,
                    index=False,
                    float_format="%.2f"
                )

                st.success(
                    f"""
✅ Updated {ticker}

Total Lot : {total_lot}

Average Buy : {new_avg:.2f}
"""
                )

            else:

                new_row = pd.DataFrame([
                    {
                        "Ticker": ticker,
                        "Lot": int(lot),
                        "Avg Buy": round(
                            float(avg_buy),
                            2
                        )
                    }
                ])

                portfolio_df = pd.concat(
                    [
                        portfolio_df,
                        new_row
                    ],
                    ignore_index=True
                )

                portfolio_df.to_csv(
                    PORTFOLIO_FILE,
                    index=False,
                    float_format="%.2f"
                )

                st.success(
                    f"{ticker} added."
                )

            st.rerun()

    st.divider()

    st.subheader("📊 Holdings")

    portfolio_df = pd.read_csv(PORTFOLIO_FILE)

    if portfolio_df.empty:

        st.info("Portfolio is empty.")

    else:

        portfolio_df["Avg Buy"] = pd.to_numeric(
            portfolio_df["Avg Buy"],
            errors="coerce"
        ).round(2)

        display_df = portfolio_df.copy()

        display_df["Avg Buy"] = display_df[
            "Avg Buy"
        ].map(
            lambda x: f"{x:.2f}"
        )

        st.metric(
            "Total Stocks",
            len(display_df)
        )

        st.dataframe(
            display_df.sort_values(
                "Ticker"
            ),
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.subheader("🗑 Delete Stock")

        delete_ticker = st.selectbox(
            "Select Stock",
            portfolio_df["Ticker"]
        )

        if st.button("Delete Stock"):

            portfolio_df = portfolio_df[
                portfolio_df["Ticker"]
                != delete_ticker
            ]

            portfolio_df.to_csv(
                PORTFOLIO_FILE,
                index=False,
                float_format="%.2f"
            )

            st.success(
                f"{delete_ticker} deleted."
            )

            st.rerun()

        st.divider()

        csv_data = portfolio_df.to_csv(
            index=False,
            float_format="%.2f"
        )

        st.download_button(
            label="📥 Download Portfolio CSV",
            data=csv_data,
            file_name="portfolio.csv",
            mime="text/csv"
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
            e["id"]
            for e in bootstrap["events"]
            if e["is_current"]
        )

        selected_gw = st.selectbox(
            "📅 Select Gameweek",
            list(range(1, current_gw + 1)),
            index=current_gw - 1
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

        entries = (
            league["standings"]["results"]
        )

        rows = []

        ownership_count = {}
        captain_count = {}
        vice_count = {}

        eo_bonus = {}

        triple_captain_count = {}

        chip_usage = {
            "3xc": 0,
            "bboost": 0,
            "freehit": 0,
            "wildcard": 0,
        }

        for manager in entries:

            try:

                entry_id = manager["entry"]

                picks = requests.get(
                    f"https://fantasy.premierleague.com/api/entry/{entry_id}/event/{selected_gw}/picks/",
                    timeout=20,
                ).json()

                if "picks" not in picks:
                    continue

                active_chip = picks.get(
                    "active_chip"
                )

                if active_chip in chip_usage:
                    chip_usage[active_chip] += 1

                captain = None
                vice = None

                for p in picks["picks"]:

                    player_name = player_lookup.get(
                        p["element"],
                        "Unknown",
                    )

                    ownership_count[player_name] = (
                        ownership_count.get(
                            player_name,
                            0,
                        )
                        + 1
                    )

                    if p["is_captain"]:

                        captain = player_name

                        captain_count[player_name] = (
                            captain_count.get(
                                player_name,
                                0,
                            )
                            + 1
                        )

                        bonus = (
                            2
                            if active_chip == "3xc"
                            else 1
                        )

                        eo_bonus[player_name] = (
                            eo_bonus.get(
                                player_name,
                                0,
                            )
                            + bonus
                        )

                        if active_chip == "3xc":

                            triple_captain_count[player_name] = (
                                triple_captain_count.get(
                                    player_name,
                                    0,
                                )
                                + 1
                            )

                    if p["is_vice_captain"]:

                        vice = player_name

                        vice_count[player_name] = (
                            vice_count.get(
                                player_name,
                                0,
                            )
                            + 1
                        )

                rows.append(
                    {
                        "Team": manager["entry_name"],
                        "Manager": manager["player_name"],
                        "Captain": captain,
                        "Vice Captain": vice,
                        "Chip": active_chip or "-",
                    }
                )

            except Exception:
                continue

        captain_df = pd.DataFrame(
            rows
        )

        total_managers = len(
            captain_df
        )

        st.subheader(
            f"GW{selected_gw} Captain Picks"
        )

        st.dataframe(
            captain_df,
            hide_index=True,
            use_container_width=True,
        )
        ownership = (
            captain_df["Captain"]
            .value_counts()
            .reset_index()
        )

        ownership.columns = [
            "Captain",
            "Managers"
        ]

        ownership["Ownership"] = (
            ownership["Managers"]
            / total_managers
            * 100
        ).round(1)

        st.subheader(
            "🏆 Captain Ownership"
        )

        st.dataframe(
            ownership,
            hide_index=True,
            use_container_width=True
        )

        vice_df = (
            pd.Series(
                vice_count
            )
            .sort_values(
                ascending=False
            )
            .reset_index()
        )

        vice_df.columns = [
            "Vice Captain",
            "Managers"
        ]

        vice_df["Ownership"] = (
            vice_df["Managers"]
            / total_managers
            * 100
        ).round(1)

        st.subheader(
            "🎖 Vice Captain Ownership"
        )

        st.dataframe(
            vice_df,
            hide_index=True,
            use_container_width=True
        )

        eo_rows = []

        for player in ownership_count:

            own_pct = round(
                ownership_count[player]
                / total_managers
                * 100,
                1
            )

            cap_pct = round(
                captain_count.get(
                    player,
                    0
                )
                / total_managers
                * 100,
                1
            )

            tc_pct = round(
                triple_captain_count.get(
                    player,
                    0
                )
                / total_managers
                * 100,
                1
            )

            eo_pct = round(
                (
                    ownership_count[player]
                    + eo_bonus.get(
                        player,
                        0
                    )
                )
                / total_managers
                * 100,
                1
            )

            eo_rows.append(
                {
                    "Player": player,
                    "Ownership %": own_pct,
                    "Captain %": cap_pct,
                    "Triple Captain %": tc_pct,
                    "EO %": eo_pct,
                }
            )

        eo_df = (
            pd.DataFrame(
                eo_rows
            )
            .sort_values(
                "EO %",
                ascending=False
            )
        )

        st.subheader(
            "📈 Effective Ownership"
        )

        st.dataframe(
            eo_df.head(20),
            hide_index=True,
            use_container_width=True
        )

        chip_df = pd.DataFrame(
            [
                {
                    "Chip": "Triple Captain",
                    "Managers": chip_usage["3xc"],
                    "Usage %": round(
                        chip_usage["3xc"]
                        / total_managers
                        * 100,
                        1
                    )
                    if total_managers
                    else 0,
                },
                {
                    "Chip": "Bench Boost",
                    "Managers": chip_usage["bboost"],
                    "Usage %": round(
                        chip_usage["bboost"]
                        / total_managers
                        * 100,
                        1
                    )
                    if total_managers
                    else 0,
                },
                {
                    "Chip": "Free Hit",
                    "Managers": chip_usage["freehit"],
                    "Usage %": round(
                        chip_usage["freehit"]
                        / total_managers
                        * 100,
                        1
                    )
                    if total_managers
                    else 0,
                },
                {
                    "Chip": "Wildcard",
                    "Managers": chip_usage["wildcard"],
                    "Usage %": round(
                        chip_usage["wildcard"]
                        / total_managers
                        * 100,
                        1
                    )
                    if total_managers
                    else 0,
                },
            ]
        )

        st.subheader(
            "🎯 Chip Usage"
        )

        st.dataframe(
            chip_df,
            hide_index=True,
            use_container_width=True
        )
        if triple_captain_count:

            tc_df = (
                pd.Series(
                    triple_captain_count
                )
                .sort_values(
                    ascending=False
                )
                .reset_index()
            )

            tc_df.columns = [
                "Player",
                "Triple Captain Count"
            ]

            tc_df["Usage %"] = (
                tc_df["Triple Captain Count"]
                / total_managers
                * 100
            ).round(1)

            st.subheader(
                "🚀 Triple Captain Picks"
            )

            st.dataframe(
                tc_df,
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        wa_text = (
            f"🧢 GW{selected_gw} CAPTAIN REPORT\n\n"
        )

        wa_text += (
            "🏆 TOP CAPTAINS\n"
        )

        for _, row in ownership.head(3).iterrows():

            wa_text += (
                f"• {row['Captain']} "
                f"({row['Ownership']}%)\n"
            )

        wa_text += "\n"

        wa_text += (
            "🎖 TOP VICE CAPTAINS\n"
        )

        for _, row in vice_df.head(3).iterrows():

            wa_text += (
                f"• {row['Vice Captain']} "
                f"({row['Ownership']}%)\n"
            )

        wa_text += "\n"

        wa_text += (
            "🎯 CHIP USAGE\n"
        )

        if chip_usage["3xc"] > 0:

            wa_text += (
                f"• Triple Captain : "
                f"{chip_usage['3xc']}/{total_managers}\n"
            )

        if chip_usage["bboost"] > 0:

            wa_text += (
                f"• Bench Boost : "
                f"{chip_usage['bboost']}/{total_managers}\n"
            )

        if chip_usage["freehit"] > 0:

            wa_text += (
                f"• Free Hit : "
                f"{chip_usage['freehit']}/{total_managers}\n"
            )

        if chip_usage["wildcard"] > 0:

            wa_text += (
                f"• Wildcard : "
                f"{chip_usage['wildcard']}/{total_managers}\n"
            )

        if triple_captain_count:

            wa_text += "\n"

            wa_text += (
                "🚀 TRIPLE CAPTAIN PICKS\n"
            )

            for _, row in tc_df.iterrows():

                wa_text += (
                    f"• {row['Player']} "
                    f"({row['Triple Captain Count']})\n"
                )

        wa_text += "\n"

        wa_text += (
            "📈 TOP 5 EO\n"
        )

        for _, row in eo_df.head(5).iterrows():

            wa_text += (
                f"• {row['Player']} "
                f"({row['EO %']}%)\n"
            )

        st.subheader(
            "📱 Copy To WhatsApp"
        )

        st.code(
            wa_text,
            language="text"
        )

    except Exception as e:

        st.error(
            f"Error loading captain picks: {e}"
        )
elif menu == "Statistics":

    st.title("📈 Player Statistics")

    stat_options = [
        "Goals",
        "Assists",
        "Clean Sheets",
        "Minutes",
        "Bonus Points",
        "ICT Index",
        "Influence",
        "Creativity",
        "Threat",
        "Saves",
        "DefCon"
    ]

    selected_stat = st.selectbox(
        "Select Statistic",
        stat_options
    )

    try:

        if selected_stat == "DefCon":

            tables = pd.read_html(
                "https://fpldraft.me/fpl-defensive-contributions"
            )

            raw = tables[0]

            stats_df = raw.iloc[
                :,
                [0, 1, -1]
            ].copy()

            stats_df.columns = [
                "Rank",
                "Player",
                "DefCon"
            ]

            stats_df["Player"] = (
                stats_df["Player"]
                .astype(str)
                .str[:-6]
            )

            stats_df["DefCon"] = pd.to_numeric(
                stats_df["DefCon"],
                errors="coerce"
            ).fillna(0)

            stats_df = stats_df.head(10)

        else:

            bootstrap = requests.get(
                "https://fantasy.premierleague.com/api/bootstrap-static/",
                timeout=20
            ).json()

            players = pd.DataFrame(
                bootstrap["elements"]
            )

            stat_map = {
                "Goals": "goals_scored",
                "Assists": "assists",
                "Clean Sheets": "clean_sheets",
                "Minutes": "minutes",
                "Bonus Points": "bonus",
                "ICT Index": "ict_index",
                "Influence": "influence",
                "Creativity": "creativity",
                "Threat": "threat",
                "Saves": "saves"
            }

            stat_col = stat_map[
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

            stats_df[selected_stat] = pd.to_numeric(
                stats_df[selected_stat],
                errors="coerce"
            ).fillna(0)

            stats_df = stats_df.sort_values(
                selected_stat,
                ascending=False
            )

            stats_df = stats_df.head(10)

            stats_df.insert(
                0,
                "Rank",
                range(
                    1,
                    len(stats_df) + 1
                )
            )

        st.subheader(
            f"🏆 Top 10 {selected_stat}"
        )

        st.dataframe(
            stats_df,
            hide_index=True,
            use_container_width=True
        )

        wa_text = (
            f"📈 {selected_stat.upper()} TOP 5\n\n"
        )

        for _, row in (
            stats_df.head(5)
            .iterrows()
        ):

            value = row[selected_stat]

            if isinstance(
                value,
                float
            ):

                value = round(
                    value,
                    1
                )

            wa_text += (
                f"• {row['Player']} "
                f"({value})\n"
            )

        st.subheader(
            "📱 Copy To WhatsApp"
        )

        st.code(
            wa_text,
            language="text"
        )

    except Exception as e:

        st.error(
            f"Error loading statistics: {e}"
        )
elif menu == "Transfer Trends":

    st.title("🔥 Transfer Trends")

    LEAGUE_ID = 147447

    try:

        bootstrap = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/",
            timeout=20
        ).json()

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

        standings = pd.DataFrame(
            league["standings"]["results"]
        )

        current_gw = next(
            e["id"]
            for e in bootstrap["events"]
            if e["is_current"]
        )

        selected_gw = st.selectbox(
            "Gameweek",
            list(range(1, current_gw + 2))
        )

        transfers_in = []
        transfers_out = []

        latest_transfers = []

        no_transfer_teams = []

        progress = st.progress(0)

        for idx, row in standings.iterrows():

            try:

                entry_id = row["entry"]

                transfers = requests.get(
                    f"https://fantasy.premierleague.com/api/entry/{entry_id}/transfers/",
                    timeout=20
                ).json()

                gw_transfers = [
                    t
                    for t in transfers
                    if t["event"] == selected_gw
                ]

                if len(gw_transfers) == 0:

                    no_transfer_teams.append(
                        {
                            "Team": row["entry_name"],
                            "Manager": row["player_name"]
                        }
                    )

                for t in gw_transfers:

                    player_in = player_lookup.get(
                        t["element_in"],
                        "Unknown"
                    )

                    player_out = player_lookup.get(
                        t["element_out"],
                        "Unknown"
                    )

                    transfers_in.append(
                        player_in
                    )

                    transfers_out.append(
                        player_out
                    )

                    latest_transfers.append(
                        {
                            "Team": row["entry_name"],
                            "Manager": row["player_name"],
                            "OUT": player_out,
                            "IN": player_in,
                            "Time": t["time"]
                        }
                    )

                progress.progress(
                    (idx + 1)
                    / len(standings)
                )

            except Exception:
                pass

        progress.empty()

        # Most Bought

        st.subheader(
            f"📈 Most Bought GW{selected_gw}"
        )

        if transfers_in:

            bought_df = (
                pd.Series(
                    transfers_in
                )
                .value_counts()
                .reset_index()
            )

            bought_df.columns = [
                "Player",
                "Bought"
            ]

            st.dataframe(
                bought_df.head(10),
                hide_index=True,
                use_container_width=True
            )

        else:

            bought_df = pd.DataFrame(
                columns=["Player", "Bought"]
            )

            st.info(
                "No transfers in."
            )

        st.divider()

        # Most Sold

        st.subheader(
            f"📉 Most Sold GW{selected_gw}"
        )

        if transfers_out:

            sold_df = (
                pd.Series(
                    transfers_out
                )
                .value_counts()
                .reset_index()
            )

            sold_df.columns = [
                "Player",
                "Sold"
            ]

            st.dataframe(
                sold_df.head(10),
                hide_index=True,
                use_container_width=True
            )

        else:

            sold_df = pd.DataFrame(
                columns=["Player", "Sold"]
            )

            st.info(
                "No transfers out."
            )

        st.divider()

        # Latest Transfers

        st.subheader(
            "🔄 Latest Transfers"
        )

        if latest_transfers:

            latest_df = pd.DataFrame(
                latest_transfers
            )

            latest_df = latest_df.sort_values(
                "Time",
                ascending=False
            )

            st.dataframe(
                latest_df,
                hide_index=True,
                use_container_width=True
            )

        else:

            st.info(
                "No transfers found."
            )

        st.divider()

        # No Transfer Teams

        st.subheader(
            "🟢 Teams With No Transfer"
        )

        if no_transfer_teams:

            no_transfer_df = pd.DataFrame(
                no_transfer_teams
            )

            st.dataframe(
                no_transfer_df,
                hide_index=True,
                use_container_width=True
            )

            st.caption(
                f"{len(no_transfer_df)} teams rolled transfer"
            )

        else:

            st.success(
                "Everyone made transfers."
            )

        st.divider()

        # WhatsApp Report

        wa_text = (
            f"🔥 GW{selected_gw} TRANSFER TRENDS\n\n"
        )

        wa_text += (
            "📈 TOP 5 BOUGHT\n"
        )

        if not bought_df.empty:

            for _, row in (
                bought_df.head(5)
                .iterrows()
            ):

                wa_text += (
                    f"• {row['Player']} "
                    f"({row['Bought']})\n"
                )

        wa_text += "\n"

        wa_text += (
            "📉 TOP 5 SOLD\n"
        )

        if not sold_df.empty:

            for _, row in (
                sold_df.head(5)
                .iterrows()
            ):

                wa_text += (
                    f"• {row['Player']} "
                    f"({row['Sold']})\n"
                )

        wa_text += "\n"

        wa_text += (
            "🟢 NO TRANSFER\n"
        )

        wa_text += (
            f"{len(no_transfer_teams)} teams\n"
        )

        for team in no_transfer_teams[:5]:

            wa_text += (
                f"• {team['Team']}\n"
            )

        st.subheader(
            "📱 Copy To WhatsApp"
        )

        st.code(
            wa_text,
            language="text"
        )

    except Exception as e:

        st.error(
            f"Error loading trends: {e}"
        )
elif menu == "Rival Analyzer":

    st.title("⚔️ Rival Analyzer")

    LEAGUE_ID = 147447

    try:

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        standings = pd.DataFrame(
            league["standings"]["results"]
        )

        teams = sorted(
            standings["entry_name"].tolist()
        )

        col1, col2 = st.columns(2)

        with col1:

            team_a = st.selectbox(
                "Team A",
                teams,
                index=0
            )

        with col2:

            team_b = st.selectbox(
                "Team B",
                teams,
                index=min(
                    1,
                    len(teams) - 1
                )
            )

        if team_a != team_b:

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

            player_lookup = dict(
                zip(
                    players["id"],
                    players["web_name"]
                )
            )

            entry_a = standings.loc[
                standings["entry_name"] == team_a,
                "entry"
            ].iloc[0]

            entry_b = standings.loc[
                standings["entry_name"] == team_b,
                "entry"
            ].iloc[0]

            rank_a = standings.loc[
                standings["entry_name"] == team_a,
                "rank"
            ].iloc[0]

            rank_b = standings.loc[
                standings["entry_name"] == team_b,
                "rank"
            ].iloc[0]

            points_a = standings.loc[
                standings["entry_name"] == team_a,
                "total"
            ].iloc[0]

            points_b = standings.loc[
                standings["entry_name"] == team_b,
                "total"
            ].iloc[0]

            picks_a = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_a}/event/{current_gw}/picks/",
                timeout=20
            ).json()

            picks_b = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_b}/event/{current_gw}/picks/",
                timeout=20
            ).json()

            captain_a = "-"
            vice_a = "-"

            for p in picks_a["picks"]:

                if p["is_captain"]:

                    captain_a = player_lookup.get(
                        p["element"],
                        "Unknown"
                    )

                if p["is_vice_captain"]:

                    vice_a = player_lookup.get(
                        p["element"],
                        "Unknown"
                    )

            captain_b = "-"
            vice_b = "-"

            for p in picks_b["picks"]:

                if p["is_captain"]:

                    captain_b = player_lookup.get(
                        p["element"],
                        "Unknown"
                    )

                if p["is_vice_captain"]:

                    vice_b = player_lookup.get(
                        p["element"],
                        "Unknown"
                    )

            squad_a = {
                player_lookup[p["element"]]
                for p in picks_a["picks"]
            }

            squad_b = {
                player_lookup[p["element"]]
                for p in picks_b["picks"]
            }

            common_players = sorted(
                squad_a & squad_b
            )

            only_a = sorted(
                squad_a - squad_b
            )

            only_b = sorted(
                squad_b - squad_a
            )

            st.subheader(
                "📊 Rival Overview"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    team_a,
                    f"{points_a} pts",
                    delta=f"Rank {rank_a}"
                )

            with col2:

                st.metric(
                    "Points Gap",
                    abs(
                        points_a - points_b
                    )
                )

            with col3:

                st.metric(
                    team_b,
                    f"{points_b} pts",
                    delta=f"Rank {rank_b}"
                )
            st.divider()

            st.subheader(
                "🧢 Captain Comparison"
            )

            cap_df = pd.DataFrame(
                [
                    {
                        "Team": team_a,
                        "Captain": captain_a,
                        "Vice Captain": vice_a
                    },
                    {
                        "Team": team_b,
                        "Captain": captain_b,
                        "Vice Captain": vice_b
                    }
                ]
            )

            st.dataframe(
                cap_df,
                hide_index=True,
                use_container_width=True
            )

            if captain_a != captain_b:

                st.warning(
                    f"""
Captain Differential

{team_a}: {captain_a}

{team_b}: {captain_b}
"""
                )

            st.divider()

            st.subheader(
                "🤝 Common Players"
            )

            common_df = pd.DataFrame(
                {
                    "Player": common_players
                }
            )

            st.metric(
                "Common Players",
                len(common_players)
            )

            st.dataframe(
                common_df,
                hide_index=True,
                use_container_width=True
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    f"🔵 Only {team_a}"
                )

                only_a_df = pd.DataFrame(
                    {
                        "Player": only_a
                    }
                )

                st.metric(
                    "Unique Picks",
                    len(only_a)
                )

                st.dataframe(
                    only_a_df,
                    hide_index=True,
                    use_container_width=True
                )

            with col2:

                st.subheader(
                    f"🟠 Only {team_b}"
                )

                only_b_df = pd.DataFrame(
                    {
                        "Player": only_b
                    }
                )

                st.metric(
                    "Unique Picks",
                    len(only_b)
                )

                st.dataframe(
                    only_b_df,
                    hide_index=True,
                    use_container_width=True
                )

            similarity = round(
                len(common_players)
                /
                max(
                    len(
                        squad_a | squad_b
                    ),
                    1
                )
                * 100,
                1
            )

            st.divider()

            st.success(
                f"""
Similarity Score

{similarity}%

Common Players:
{len(common_players)}

Differentials:
{len(only_a) + len(only_b)}
"""
            )

            st.divider()

            wa_text = (
                "⚔️ RIVAL ANALYZER\n\n"
            )

            wa_text += (
                f"{team_a}\n"
                f"Rank #{rank_a}\n"
                f"{points_a} pts\n\n"
            )

            wa_text += (
                f"{team_b}\n"
                f"Rank #{rank_b}\n"
                f"{points_b} pts\n\n"
            )

            wa_text += (
                f"📊 Gap: "
                f"{abs(points_a - points_b)} pts\n\n"
            )

            wa_text += (
                f"🧢 Captain\n"
                f"{team_a}: {captain_a}\n"
                f"{team_b}: {captain_b}\n\n"
            )

            wa_text += (
                f"🎖 Vice Captain\n"
                f"{team_a}: {vice_a}\n"
                f"{team_b}: {vice_b}\n\n"
            )

            wa_text += (
                f"🤝 Common Players: "
                f"{len(common_players)}\n"
            )

            wa_text += (
                f"📈 Similarity: "
                f"{similarity}%\n\n"
            )

            wa_text += (
                f"🔵 Only {team_a}: "
                f"{len(only_a)}\n"
            )

            for player in only_a[:5]:
                wa_text += (
                    f"• {player}\n"
                )

            wa_text += "\n"

            wa_text += (
                f"🟠 Only {team_b}: "
                f"{len(only_b)}\n"
            )

            for player in only_b[:5]:
                wa_text += (
                    f"• {player}\n"
                )

            st.subheader(
                "📱 Copy To WhatsApp"
            )

            st.code(
                wa_text,
                language="text"
            )

    except Exception as e:

        st.error(
            f"Error loading rival analysis: {e}"
        )

elif menu == "Right Issue Calc":

    st.title(
        "🎁 Right Issue Calculator"
    )

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    ticker = st.selectbox(
        "Ticker",
        portfolio_df["Ticker"]
    )

    row = portfolio_df[
        portfolio_df["Ticker"]
        == ticker
    ].iloc[0]

    lots = int(
        row["Lot"]
    )

    avg_buy = float(
        row["Avg Buy"]
    )

    shares = lots * 100

    current_price = 0

    try:

        hist = yf.Ticker(
            ticker + ".JK"
        ).history(
            period="5d"
        )

        current_price = float(
            hist["Close"].iloc[-1]
        )

    except:
        pass

    st.subheader(
        "📋 Rights Issue Parameters"
    )

    col1, col2 = st.columns(2)

    with col1:

        rights_price = st.number_input(
            "RI Price",
            min_value=1.0,
            value=max(
                current_price * 0.8,
                1.0
            )
        )

    with col2:

        cum_date = st.text_input(
            "Cum Date",
            ""
        )

    st.markdown(
        "### Ratio"
    )

    col1, col2 = st.columns(2)

    with col1:

        ratio_old = st.number_input(
            "Existing Shares",
            min_value=1,
            value=5
        )

    with col2:

        ratio_new = st.number_input(
            "New Shares",
            min_value=1,
            value=1
        )

    rights_shares = int(
        shares
        * ratio_new
        / ratio_old
    )

    funds_needed = (
        rights_shares
        * rights_price
    )

    discount = round(
        (
            (
                current_price
                - rights_price
            )
            / current_price
        )
        * 100,
        2
    ) if current_price else 0

    terp = round(
        (
            (
                ratio_old
                * current_price
            )
            +
            (
                ratio_new
                * rights_price
            )
        )
        /
        (
            ratio_old
            + ratio_new
        ),
        2
    ) if current_price else 0

    profit_to_terp = round(
        (
            (
                current_price
                - terp
            )
            / terp
        )
        * 100,
        2
    ) if terp else 0

    st.subheader(
        "📊 RI Analysis"
    )

    result_df = pd.DataFrame(
        [
            {
                "Metric": "Current Price",
                "Value":
                f"{current_price:,.0f}"
            },
            {
                "Metric": "RI Price",
                "Value":
                f"{rights_price:,.0f}"
            },
            {
                "Metric": "Discount",
                "Value":
                f"{discount:.2f}%"
            },
            {
                "Metric": "Ratio",
                "Value":
                f"{ratio_old}:{ratio_new}"
            },
            {
                "Metric": "Owned Shares",
                "Value":
                f"{shares:,}"
            },
            {
                "Metric": "Rights Shares",
                "Value":
                f"{rights_shares:,}"
            },
            {
                "Metric": "Funds Needed",
                "Value":
                f"Rp {funds_needed:,.0f}"
            },
            {
                "Metric": "TERP",
                "Value":
                f"{terp:,.0f}"
            },
            {
                "Metric": "Premium vs TERP",
                "Value":
                f"{profit_to_terp:.2f}%"
            },
            {
                "Metric": "Avg Buy",
                "Value":
                f"{avg_buy:,.0f}"
            }
        ]
    )

    st.dataframe(
        result_df,
        hide_index=True,
        use_container_width=True
    )

    score = 0

    if discount >= 20:

        score += 3

    elif discount >= 10:

        score += 2

    elif discount >= 5:

        score += 1

    if current_price > terp:

        score += 2

    if score >= 5:

        rating = "🔥 Attractive"

    elif score >= 3:

        rating = "⚠️ Neutral"

    else:

        rating = "🚫 Less Attractive"

    st.metric(
        "RI Rating",
        rating
    )

    st.divider()

    wa_text = (
        "🎁 RIGHTS ISSUE ANALYZER\n\n"
        f"{ticker}\n\n"
        f"Current Price : {current_price:,.0f}\n"
        f"RI Price : {rights_price:,.0f}\n"
        f"Discount : {discount:.2f}%\n\n"
        f"Ratio : {ratio_old}:{ratio_new}\n"
        f"Shares Owned : {shares:,}\n"
        f"HMETD : {rights_shares:,}\n\n"
        f"Need Funds : Rp {funds_needed:,.0f}\n"
        f"TERP : {terp:,.0f}\n"
        f"Premium vs TERP : {profit_to_terp:.2f}%\n\n"
        f"Rating : {rating}"
    )

    if cum_date:

        wa_text += (
            f"\nCum Date : {cum_date}"
        )

    st.subheader(
        "📱 Copy To WhatsApp"
    )

    st.code(
        wa_text,
        language="text"
    )
elif menu == "Dividend Momentum":

    st.title("💰 Dividend Momentum")

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    rows = []

    total_dividend = 0

    for _, row in portfolio_df.iterrows():

        try:

            ticker = row["Ticker"]

            stock = yf.Ticker(
                ticker + ".JK"
            )

            hist = stock.history(
                period="1y"
            )

            if hist.empty:
                continue

            current_price = float(
                hist["Close"]
                .iloc[-1]
            )

            dividends = stock.dividends

            dividend_per_share = 0

            if not dividends.empty:

                dividend_per_share = float(
                    dividends.tail(1)
                    .iloc[0]
                )

            shares = (
                int(row["Lot"])
                * 100
            )

            avg_buy = float(
                row["Avg Buy"]
            )

            current_yield = round(
                (
                    dividend_per_share
                    / current_price
                )
                * 100,
                2
            ) if current_price else 0

            yoc = round(
                (
                    dividend_per_share
                    / avg_buy
                )
                * 100,
                2
            ) if avg_buy else 0

            cash_dividend = (
                dividend_per_share
                * shares
            )

            total_dividend += (
                cash_dividend
            )

            score = 0

            if current_yield >= 8:

                score += 3

            elif current_yield >= 6:

                score += 2

            elif current_yield >= 4:

                score += 1

            if yoc > current_yield:

                score += 1

            if current_price < avg_buy:

                score += 1

            if score >= 4:

                rating = "🔥 Strong"

            elif score >= 2:

                rating = "✅ Good"

            else:

                rating = "⚠️ Weak"

            rows.append(
                {
                    "Ticker":
                    ticker,

                    "Price":
                    round(
                        current_price,
                        0
                    ),

                    "Dividend":
                    round(
                        dividend_per_share,
                        2
                    ),

                    "Yield %":
                    current_yield,

                    "YOC %":
                    yoc,

                    "Cash Dividend":
                    round(
                        cash_dividend
                    ),

                    "Rating":
                    rating
                }
            )

        except:
            pass

    dividend_df = pd.DataFrame(
        rows
    )

    if dividend_df.empty:

        st.warning(
            "No dividend data found."
        )

    else:

        dividend_df = (
            dividend_df
            .sort_values(
                "Yield %",
                ascending=False
            )
        )

        st.metric(
            "💵 Expected Dividend",
            f"Rp {total_dividend:,.0f}"
        )

        st.dataframe(
            dividend_df,
            hide_index=True,
            use_container_width=True
        )

        st.subheader(
            "🏆 Top Dividend Opportunities"
        )

        st.dataframe(
            dividend_df.head(5),
            hide_index=True,
            use_container_width=True
        )

        wa_text = (
            "💰 DIVIDEND MOMENTUM\n\n"
        )

        wa_text += (
            f"Expected Dividend\n"
            f"Rp {total_dividend:,.0f}\n\n"
        )

        for _, row in (
            dividend_df.head(5)
            .iterrows()
        ):

            wa_text += (
                f"• {row['Ticker']}\n"
                f"Yield {row['Yield %']}%\n"
                f"YOC {row['YOC %']}%\n"
                f"Cash Rp {row['Cash Dividend']:,.0f}\n\n"
            )

        st.subheader(
            "📱 Copy To WhatsApp"
        )

        st.code(
            wa_text,
            language="text"
        )
elif menu == "Price Momentum":

    st.title("🚀 Price Momentum")

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    rows = []

    for _, row in portfolio_df.iterrows():

        try:

            ticker = row["Ticker"]

            hist = yf.Ticker(
                ticker + ".JK"
            ).history(
                period="1y"
            )

            if len(hist) < 60:
                continue

            close = hist["Close"]

            current = float(
                close.iloc[-1]
            )

            ret_1w = round(
                (
                    (
                        current
                        - close.iloc[-6]
                    )
                    /
                    close.iloc[-6]
                )
                * 100,
                2
            )

            ret_1m = round(
                (
                    (
                        current
                        - close.iloc[-21]
                    )
                    /
                    close.iloc[-21]
                )
                * 100,
                2
            )

            ret_3m = round(
                (
                    (
                        current
                        - close.iloc[-63]
                    )
                    /
                    close.iloc[-63]
                )
                * 100,
                2
            )

            high_52w = float(
                close.max()
            )

            gap_high = round(
                (
                    (
                        current
                        /
                        high_52w
                    )
                    - 1
                )
                * 100,
                2
            )

            ma20 = float(
                close.tail(20)
                .mean()
            )

            ma50 = float(
                close.tail(50)
                .mean()
            )

            volume_now = float(
                hist["Volume"]
                .iloc[-1]
            )

            volume_avg = float(
                hist["Volume"]
                .tail(20)
                .mean()
            )

            vol_ratio = round(
                volume_now
                / volume_avg,
                1
            ) if volume_avg > 0 else 0

            if (
                current > ma20
                and current > ma50
                and vol_ratio >= 1.5
                and gap_high >= -5
            ):

                rating = "🔥 Strong"

            elif (
                current > ma20
                and current > ma50
            ):

                rating = "✅ Building"

            else:

                rating = "⚠️ Weak"

            rows.append(
                {
                    "Ticker":
                    ticker,

                    "Price":
                    round(
                        current,
                        0
                    ),

                    "1W %":
                    ret_1w,

                    "1M %":
                    ret_1m,

                    "3M %":
                    ret_3m,

                    "Gap 52W High %":
                    gap_high,

                    "Vol Ratio":
                    vol_ratio,

                    "Rating":
                    rating
                }
            )

        except:
            pass

    momentum_df = pd.DataFrame(
        rows
    )

    if momentum_df.empty:

        st.warning(
            "No data found."
        )

    else:

        momentum_df = momentum_df.sort_values(
            [
                "3M %",
                "1M %"
            ],
            ascending=False
        )

        st.dataframe(
            momentum_df,
            hide_index=True,
            use_container_width=True
        )

        st.subheader(
            "🔥 Strong Momentum"
        )

        strong_df = momentum_df[
            momentum_df["Rating"]
            == "🔥 Strong"
        ]

        if not strong_df.empty:

            st.dataframe(
                strong_df,
                hide_index=True,
                use_container_width=True
            )

        wa_text = (
            "🚀 PRICE MOMENTUM\n\n"
        )

        for _, row in (
            momentum_df.head(5)
            .iterrows()
        ):

            wa_text += (
                f"• {row['Ticker']}\n"
                f"1M {row['1M %']}%\n"
                f"3M {row['3M %']}%\n"
                f"Gap52H {row['Gap 52W High %']}%\n"
                f"{row['Rating']}\n\n"
            )

        st.subheader(
            "📱 Copy To WhatsApp"
        )

        st.code(
            wa_text,
            language="text"
        )
