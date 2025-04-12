import streamlit as st
from connection import MotherDuckConnection
import plotly.express as px
import duckdb
# import time  # Remove time


def get_streamer_list(conn):
    results = conn.query(
        "SELECT DISTINCT channel_name FROM channel_stats ORDER BY channel_name ASC;"
    )
    channels = results["channel_name"]
    return channels


def get_streamer_data(conn, channels):
    channel_name = st.selectbox(
        "Choose a streamer", options=channels, index=None, placeholder="Choose a Streamer"
    )
    if channel_name is None:
        return None
    df = conn.query(
        "SELECT * FROM channel_stats WHERE channel_name = ?", params={channel_name}
    )
    return df


def consec_weeks(local_conn, channel_df):
    query = """
    WITH week_indexed  AS (
        SELECT
            *,
            DATE_PART('epoch', DATE_TRUNC('week', start_date)) / 604800 AS continuous_week_index,
            ROW_NUMBER() OVER (PARTITION BY channel_name ORDER BY start_date) AS row_num
        FROM channel_df
    ),
    grouped_weeks AS (
    SELECT
        *,
        continuous_week_index - row_num AS group_id
    FROM week_indexed
    ),
    group_counts  AS (
        SELECT
            group_id,
            COUNT(*) AS consecutive_weeks
        FROM grouped_weeks
        GROUP BY group_id
    ),
    max_group AS (
        SELECT
            group_id
        FROM group_counts
        ORDER BY consecutive_weeks DESC, group_id DESC
        LIMIT 1
    )
    SELECT
        gw.*
    FROM grouped_weeks as gw
    JOIN max_group mg
    ON gw.group_id = mg.group_id
    """
    result_df = local_conn.execute(query).df()

    if result_df.shape[0] < 3:
        st.write(result_df)
    else:
        fig = px.line(
            result_df,
            x="start_date",
            y="hours_watched",
            title="Consecutive Weeks Hours Watched and Airtime in Minutes",
            labels={"start_date": "Date W/C", "hours_watched": "Hours Watched"},
        )
        fig.for_each_trace(lambda t: t.update(name="Hours Watched"))
        fig.update_traces(showlegend=True)
        fig.add_scatter(
            x=result_df["start_date"],
            y=result_df["airtime_in_m"],
            mode="lines",
            name="Airtime (Minutes)",
            yaxis="y2",
            hovertemplate="Date W/C=%{x}<br>Airtime (Minutes)=%{y}<extra></extra>",
        )
        fig.update_layout(
            xaxis=dict(title="Date (Week Commencing)"),
            yaxis=dict(title="Hours Watched"),
            yaxis2=dict(
                title="Airtime (Minutes)",
                overlaying="y",
                side="right",
                showgrid=False,
            ),
            legend=dict(x=0.5, y=1.1, orientation="h", xanchor="center", yanchor="top"),
        )

        st.plotly_chart(fig)


def streamer():
    db_name = "streamer_db" if st.secrets.general.is_deployed else "local_streamer_db"
    conn = st.connection(db_name, type=MotherDuckConnection)

    streamers = get_streamer_list(conn=conn)
    streamer_info = get_streamer_data(conn=conn, channels=streamers)

    if streamer_info is not None:
        with duckdb.connect(database=':memory:', read_only=False) as local_conn:
            local_conn.register('channel', streamer_info)
            st.write(streamer_info)
            # time.sleep(3)  # REMOVE this line
            consec_weeks(local_conn=local_conn, channel_df=streamer_info)


streamer()
