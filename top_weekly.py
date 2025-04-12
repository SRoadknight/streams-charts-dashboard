import streamlit as st
from connection import MotherDuckConnection
import plotly.express as px


def weekly_data(conn):
    results = conn.query("SELECT DISTINCT year, week_number FROM channel_stats ORDER BY year ASC")
    years = set(results["year"])
    year = st.sidebar.select_slider("Select year", years)
    weeks = sorted(set(results[results["year"] == year]["week_number"]))
    if len(weeks) == 1:
        week = weeks[0]
        st.write(f"Only one available week: {week}") 
    else:
        week = st.sidebar.select_slider("Select week", weeks)
    df = conn.query("SELECT * FROM channel_stats WHERE week_number = ? AND year = ?", params=[week, year], index_col="channel_id")
    st.write(df)
    fig = px.bar(
        df.head(10),
        x="hours_watched",
        y="channel_name",
        orientation="h",
        text="hours_watched",
        title="Top 10 Streamers by Hours Watched"
    )
    fig.update_layout(xaxis_title="Hours Watched", yaxis_title="Streamer", yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig)
    return df

@st.fragment
def comparison(weekly_data, selected_state):
    available_channels = sorted(list(weekly_data["channel_name"]))
    selected_and_available = [channel for channel in selected_state if channel in available_channels]
    currently_selected_streamers = st.multiselect("Select streamers", available_channels, default=selected_and_available)

    
    choice_map = {
        "Hours Watched": "hours_watched",
        "Airtime in Minutes": "airtime_in_m"
    }
    
    if len(currently_selected_streamers) < 2:
        st.warning("Choose two streamers to start comparing")
    else:
        choice = st.radio(label="Choose", options=["Hours Watched", "Airtime in Minutes"])
        column_choice = choice_map[choice]
        fig = px.bar(
            weekly_data[weekly_data["channel_name"].isin(currently_selected_streamers)],
            x=column_choice,
            y="channel_name",
            orientation="h",
            text=column_choice,
            title=f"Compare Streamers By {choice}"
        )
        fig.update_layout(xaxis_title=choice, yaxis_title="Streamer", yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig)
    st.session_state.selected_streamers = currently_selected_streamers + [channel for channel in selected_state if channel not in available_channels]


def top_weekly():
    db_name = "streamer_db" if st.secrets.general.is_deployed else "local_streamer_db"
    conn = st.connection(db_name, type=MotherDuckConnection)

    df_weekly = weekly_data(conn=conn)
    if "selected_streamers" not in st.session_state:
        st.session_state.selected_streamers = []
    comparison(df_weekly, st.session_state.selected_streamers)

top_weekly()