import streamlit as st
from connection import MotherDuckConnection
import plotly.express as px
import duckdb

def top_weekly():
    
    db_name = "streamer_db" if st.secrets.general.is_deployed else "local_streamer_db"
    conn = st.connection(db_name, type=MotherDuckConnection)


    results = conn.query("SELECT DISTINCT year, week_number FROM channel_stats ORDER BY year ASC")
    years = set(results["year"])
    year = st.select_slider("Select year", years)
    weeks = sorted(set(results[results["year"] == year]["week_number"]))
    if len(weeks) == 1:
        week = weeks[0]
        st.write(f"Only one available week: {week}") 
    else:
        week = st.select_slider("Select week", weeks)
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


  

    streamers = st.multiselect("Select streamers", list(df["channel_name"]))
    
    choice_map = {
        "Hours Watched": "hours_watched",
        "Airtime in Minutes": "airtime_in_m"
    }
    
    if not streamers or len(streamers) < 2:
        st.warning("Choose two streamers to start comparing")
    else:
        choice = st.radio(label="Choose", options=["Hours Watched", "Airtime in Minutes"])
        column_choice = choice_map[choice]
        fig = px.bar(
            df[df["channel_name"].isin(streamers)],
            x=column_choice,
            y="channel_name",
            orientation="h",
            text=column_choice,
            title=f"Compare Streamers By {choice}"
        )
        fig.update_layout(xaxis_title=choice, yaxis_title="Streamer", yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig)


    local_conn = duckdb.connect(database=':memory:', read_only=False)
    local_conn.register('streamers', df)

    # Example Query: Get the top 2 channels by hours watched
    query = "SELECT * FROM streamers ORDER BY hours_watched DESC LIMIT 2"
    result_df = local_conn.execute(query).df()

    # Display in Streamlit
    st.write("Original DataFrame:", df)
    st.write("Top 2 Channels:", result_df)
    
   

top_weekly()