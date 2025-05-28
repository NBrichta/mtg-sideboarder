# splash.py
import streamlit as st
import sideboarder_modular as sb_mod

# 1. Configure the main page
st.set_page_config(
    page_title="Home - SideBoarder",
    page_icon="./images/icon.ico",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "mailto:sideboarder.dev@gmail.com",
        "Report a bug": "https://github.com/NBrichta/mtg-sideboarder/issues",
        "About": "MTG Sideboarder is a passion project borne out of a frustration with clunky Excel spreadsheets and a love for Magic: The Gathering. I cannot express how thankful I am to everyone who has supported its development.",
    },
)
sb_mod.inject_css()
sb_mod.render_sidebar()
# 2. Splash screen UI
st.markdown("<h1 style='text-align:center'>SideBoarder</h1>", unsafe_allow_html=True)
sb_mod.section_divider()
st.markdown(
    "<p style='text-align:center'>Create matchup-specific sideboard guides in seconds, completely free.</p>",
    unsafe_allow_html=True,
)
st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)

# Navigation buttons
sb_mod.splash_buttons()
st.markdown(
    """
        <div style='height:3rem'></div>
        <div style="display:flex;justify-content:space-between;width:100%;align-items:center;">          
          <a href="https://sideboarder.bsky.social" target="_blank">
            <img src="https://img.shields.io/badge/@sideboarder-0285FF?style=for-the-badge&logo=bluesky&logoColor=fff">
          </a>
          <a href="https://x.com/SideBoarder" target="_blank">
            <img src="https://img.shields.io/badge/@sideboarder-%23000000.svg?style=for-the-badge&logo=X&logoColor=white">
          </a>
          <a href="https://ko-fi.com/sideboarder" target="_blank">
            <img src="https://img.shields.io/badge/support-F16061?style=for-the-badge&logo=ko-fi&logoColor=white">
          </a>
          <a href="https://github.com/NBrichta/mtg-sideboarder" target="_blank">
            <img src="https://img.shields.io/badge/develop-%23121011.svg?style=for-the-badge&logo=github&logoColor=white">
          </a>
        </div>
        """,
    unsafe_allow_html=True,
)
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center'><i>SideBoarder monitors traffic for analytics purposes and does not store any personal information.</i></p>",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

with col2:
    st.subheader("Changelog")
    sb_mod.section_divider()
    st.markdown(
        """
    - `v1.0.0` Initial release.
  """
    )
