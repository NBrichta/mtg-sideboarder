# Home.py
import streamlit as st
import sideboarder_modular as sb_mod

# 1. Configure the main page
st.set_page_config(
    page_title="MTG Sideboarder",
    page_icon="./images/icon.ico",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://github.com/NBrichta/mtg-sideboarder",
        "Report a bug": "https://github.com/NBrichta/mtg-sideboarder/issues",
        "About": "MTG Sideboarder is a passion project borne out of a frustration with clunky Excel spreadsheets and a love for Magic: The Gathering. I cannot express how thankful I am to everyone who has supported its development.",
        }
)
sb_mod.inject_css()

# 2. Splash screen UI
st.markdown("<h1 style='text-align:center'>MTG Sideboarder</h1>", unsafe_allow_html=True)
sb_mod.section_divider()
st.markdown("<p style='text-align:center'>A lightweight UI for designing and exporting Magic: The Gathering sideboard guides.</p>", unsafe_allow_html=True)

st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)

# Navigation buttons
sb_mod.splash_buttons()



st.markdown( """
        <div style='height:2rem'></div>
        <div style="display:flex;justify-content:space-between;width:100%;align-items:center;">
          <a href="https://sideboarder.bsky.social" target="_blank">
            <img src="https://img.shields.io/badge/@sideboarder.bsky-0285FF?style=for-the-badge&logo=bluesky&logoColor=fff">
          </a>
          <a href="https://ko-fi.com/sideboarder" target="_blank">
            <img src="https://img.shields.io/badge/support_the_project-F16061?style=for-the-badge&logo=ko-fi&logoColor=white">
          </a>
          <a href="https://github.com/NBrichta/mtg-sideboarder" target="_blank">
            <img src="https://img.shields.io/badge/follow_development-%23121011.svg?style=for-the-badge&logo=github&logoColor=white">
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>MTG Sideboarder is built with Python 3.1 and Streamlit 1.45.0</p>", unsafe_allow_html=True)

