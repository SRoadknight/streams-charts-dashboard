import streamlit as st

def home():
    st.set_page_config(
            page_title="Twitch Top 100 Streamers",
            page_icon="👋",
        )

    st.write("# Welcome! 👋")


    st.markdown(
        """
        Twitch top 100 streamers weekly analysis. \n
    """
    )

home()