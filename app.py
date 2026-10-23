import streamlit as st
import pandas as pd
import requests
import plotly.express as px

TEAM_ID = 1158519

st.set_page_config(
    page_title="FPL Nexus",
    page_icon="⚽",
    layout="wide"
)

# =========================
# API HELPER
# =========================

def get_json(url):
    try:
        r = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
        r.raise_for_status()
        return r.json()

    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# =========================
# DATA
# =========================

@st.cache_data(ttl=300)
def get_bootstrap():
    return get_json(
        "https://fantasy.premierleague.com/api/bootstrap-static/"
    )

@st.cache_data(ttl=300)
def get_manager():
    return get_json(
        f"https://fantasy.premierleague.com/api/entry/{TEAM_ID}/"
    )

@st.cache_data(ttl=300)
def get_history():
    return get_json(
        f"https://fantasy.premierleague.com/api/entry/{TEAM_ID}/history/"
    )

@st.cache_data(ttl=300)
def get_fixtures():
    return get_json(
        "https://fantasy.premierleague.com/api/fixtures/"
    )

# =========================
# LOAD DATA
# =========================

bootstrap = get_bootstrap()

if not bootstrap:
    st.stop()

manager = get_manager()
history = get_history()

players = pd.DataFrame(
    bootstrap["elements"]
)

teams = pd.DataFrame(
    bootstrap["teams"]
)

events = pd.DataFrame(
    bootstrap["events"]
)

players = players.merge(
    teams[["id", "name"]],
    left_on="team",
    right_on="id",
    how="left",
    suffixes=("", "_team")
)

players.rename(
    columns={"id_x": "player_id"},
    inplace=True
)


# =========================
# CURRENT GW
# =========================

current_rows = events[
    events["is_current"] == True
]

if len(current_rows):
    current_gw = int(
        current_rows.iloc[0]["id"]
    )
else:
    current_gw = int(
        events["id"].max()
    )

# =========================
# SQUAD
# =========================

@st.cache_data(ttl=300)
def get_squad():
    return get_json(
        f"https://fantasy.premierleague.com/api/entry/{TEAM_ID}/event/{current_gw}/picks/"
    )

squad = get_squad()

# =========================
# SIDEBAR
# =========================

st.sidebar.title("⚽ FPL Nexus")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

page = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "My Team",
        "Captain Center",
        "Player Database",
        "Top Form Players",
        "Price Tracker",
        "Rank History",
        "Fixtures"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Team ID: 1158519"
)

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.title("⚽ FPL Nexus")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Overall Rank",
            f"{manager.get('summary_overall_rank',0):,}"
        )

    with col2:
        st.metric(
            "Total Points",
            manager.get(
                "summary_overall_points",
                0
            )
        )

    with col3:
        st.metric(
            "Team Value",
            f"£{manager.get('last_deadline_value',0)/10:.1f}"
        )

    with col4:
        st.metric(
            "Bank",
            f"£{manager.get('last_deadline_bank',0)/10:.1f}"
        )

    st.divider()

    st.subheader(
        "Manager Information"
    )

    st.json(
        {
            "Team Name":
                manager.get("name"),

            "Manager":
                manager.get(
                    "player_first_name",
                    ""
                )
                + " "
                +
                manager.get(
                    "player_last_name",
                    ""
                ),
        }
    )

# =========================
# MY TEAM
# =========================

elif page == "My Team":

    st.title("🏆 My Team")

    if squad:

        picks = pd.DataFrame(
            squad["picks"]
        )

        team = picks.merge(
    players,
    left_on="element",
    right_on="player_id"
)


        squad_view = team[
            [
                "position",
                "web_name",
                "name",
                "now_cost",
                "form",
                "total_points",
                "multiplier"
            ]
        ].copy()

        squad_view.columns = [
            "Squad Pos",
            "Player",
            "Club",
            "Price",
            "Form",
            "Points",
            "Captain"
        ]

        squad_view["Price"] = (
            squad_view["Price"] / 10
        )

        st.dataframe(
            squad_view,
            use_container_width=True
        )

# =========================
# CAPTAIN CENTER
# =========================

elif page == "Captain Center":

    st.title("🎯 Captain Center")

    captain = players[
        [
            "web_name",
            "name",
            "form",
            "total_points",
            "selected_by_percent"
        ]
    ].copy()

    captain["form"] = pd.to_numeric(
        captain["form"],
        errors="coerce"
    )

    captain["selected_by_percent"] = pd.to_numeric(
        captain["selected_by_percent"],
        errors="coerce"
    )

    captain["score"] = (
        captain["form"] * 3
        +
        captain["total_points"] * 0.05
        +
        captain["selected_by_percent"] * 0.05
    )

    captain = captain.sort_values(
        "score",
        ascending=False
    )

    st.dataframe(
        captain.head(20),
        use_container_width=True
    )

# =========================
# PLAYER DATABASE
# =========================

elif page == "Player Database":

    st.title("📊 Player Database")

    search = st.text_input(
        "Search Player"
    )

    df = players.copy()

    if search:
        df = df[
            df["web_name"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    view = df[
        [
            "web_name",
            "name",
            "now_cost",
            "total_points",
            "goals_scored",
            "assists",
            "form"
        ]
    ]

    st.dataframe(
        view,
        use_container_width=True
    )

# =========================
# TOP FORM
# =========================

elif page == "Top Form Players":

    st.title("🔥 Top Form Players")

    form_df = players.copy()

    form_df["form"] = pd.to_numeric(
        form_df["form"],
        errors="coerce"
    )

    form_df = form_df.sort_values(
        "form",
        ascending=False
    ).head(20)

    fig = px.bar(
        form_df,
        x="web_name",
        y="form",
        color="name"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================
# PRICE TRACKER
# =========================

elif page == "Price Tracker":

    st.title("💰 Price Tracker")

    price_df = players[
        [
            "web_name",
            "name",
            "now_cost",
            "cost_change_event"
        ]
    ]

    st.dataframe(
        price_df.sort_values(
            "cost_change_event",
            ascending=False
        ),
        use_container_width=True
    )

# =========================
# HISTORY
# =========================

elif page == "Rank History":

    st.title("📈 Rank History")

    if history:

        current = pd.DataFrame(
            history["current"]
        )

        fig = px.line(
            current,
            x="event",
            y="overall_rank",
            markers=True,
            title="Overall Rank"
        )

        fig.update_yaxes(
            autorange="reversed"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =========================
# FIXTURES
# =========================
elif page == "Fixtures":

    st.title("📅 Fixtures")

    fixture_data = get_fixtures()

    if fixture_data:

        fixture_df = pd.DataFrame(fixture_data)

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
            fixture_df["event"].dropna().unique()
        )

        selected_gw = st.selectbox(
            "Gameweek",
            gw_list
        )

        gw_df = fixture_df[
            fixture_df["event"] == selected_gw
        ]

        st.markdown(
            f"### Gameweek {selected_gw}"
        )

        card_html = """
        <div style="
            border:1px solid #444;
            border-radius:15px;
            padding:15px;
            margin-top:10px;
        ">
        """

        for _, row in gw_df.iterrows():

            kickoff = ""

            if "kickoff_time" in row and pd.notna(row["kickoff_time"]):
                try:
                    kickoff = pd.to_datetime(
                        row["kickoff_time"]
                    ).strftime("%H:%M")
                except:
                    kickoff = "TBD"
            else:
                kickoff = "TBD"

            card_html += f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:10px 0;
            ">
                <div style="
                    width:40%;
                    text-align:left;
                    font-weight:600;
                ">
                    {row['Home Team']}
                </div>

                <div style="
                    width:20%;
                    text-align:center;
                    color:#999;
                    font-size:14px;
                ">
                    {kickoff}
                </div>

                <div style="
                    width:40%;
                    text-align:right;
                    font-weight:600;
                ">
                    {row['Away Team']}
                </div>
            </div>

            <hr style="
                border:none;
                border-top:1px solid #333;
            ">
            """

        card_html += "</div>"

        st.markdown(
            card_html,
            unsafe_allow_html=True
        )

    else:
        st.warning(
            "Fixture data tidak tersedia."
        )
