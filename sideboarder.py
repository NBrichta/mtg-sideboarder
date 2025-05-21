import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np
import sideboarder_modular as sb_mod

# ─────── DEVELOPMENT TOGGLE ───────
USE_DUMMY_MATCHUPS = False
# ───────────────────────────────────


st.set_page_config(
    page_title="MTG Sideboard Guide",
    page_icon="./icon.ico",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": "https://github.com/NBrichta/mtg-sideboarder",
        "Report a bug": "https://github.com/NBrichta/mtg-sideboarder/issues",
        "About": "MTG Sideboarder is a passion project borne out of frustration with tedious Excel spreadsheets and a desire to help the competitive MTG community. I cannot express how thankful I am to everyone who has supported its development.",
    },
)

# Inject CSS to force all text inputs & text areas into monospace
st.markdown(
    """
    <style>
      /* text_area widget */
      .stTextArea textarea {
        font-family: monospace !important;
      }
      /* text_input widget */
      .stTextInput input {
        font-family: monospace !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("MTG Sideboarder")

st.markdown(
    """
A lightweight UI for designing and exporting Magic: The Gathering sideboard guides.

Follow the steps below to get started!
"""
)

# =========== Step 1: Deck Input
st.header(
    "Import Decklist",
    help="Your decklist data **must** be in MTGO formatting for this to work properly. In the future, importing decklists from URLs is a high priority once I figure out how APIs work.",
)

st.markdown(
    """
    <hr style="
      border: 2px solid #AF5D63;
      width: 100%;
      margin: 0 0 1em 0;
    ">
    """,
    unsafe_allow_html=True,
)

"""
This section lets you import your decklist in standard MTGO format. Once you click **"Submit Deck"**, the cards will automatically be parsed into mainboard and sideboard libraries for the search bars in the next section.
"""

decklist_text = st.text_input(
    "Your Decklist Name",
    placeholder="Optional. If left blank, the exported guide will be untitled.",
)
mainboard_text = st.text_area(
    "Mainboard",
    height=200,
    placeholder="4 Amulet of Vigor\n4 Primeval Titan\n3 Scapeshift\n2 Lotus Field\netc.",
)
sideboard_text = st.text_area(
    "Sideboard", height=100, placeholder="1 Boseiju, Who Endures\n2 Dismember\netc."
)

# Initialize session state with structured defaults
default_session = {
    "deck_data": {},
    "matchups": [],
    "out_quantities": {},
    "in_quantities": {},
    "confirm_reset": False,
    "search_out": [],
    "search_in": [],
    "opponent_name": "",
    "confirm_add": False,
    "clear_fields": False,
    "card_labels": {},
}
for key, default in default_session.items():
    st.session_state.setdefault(key, default)

# If dev-mode, and you’ve already submitted a deck, load dummy matchups now
if USE_DUMMY_MATCHUPS and st.session_state.deck_data:
    st.session_state.matchups = sb_mod.get_dummy_matchups()

# Submit deck
if st.button("Submit Deck"):
    main_raw = sb_mod.parse_decklist(mainboard_text)
    side_raw = sb_mod.parse_decklist(sideboard_text)
    mainboard = {f"MB:{name}": qty for name, qty in main_raw.items()}
    sideboard = {f"SB:{name}": qty for name, qty in side_raw.items()}
    labels = {**{k: k[3:] for k in mainboard}, **{k: k[3:] for k in sideboard}}

    st.session_state.deck_data = {"mainboard": mainboard, "sideboard": sideboard}
    st.session_state.card_labels = labels
    st.success("Decklist saved.")
    st.session_state.out_quantities = {}
    st.session_state.in_quantities = {}

# ============= Step 2: Matchup Entry (skipped in DEV mode)

# only show the UI if you’re *not* using dummy data:
if not USE_DUMMY_MATCHUPS:
    sb_mod.render_matchup_entry()

# Matrix preview
if st.session_state.matchups:
    st.header("Sideboard Matrix Preview")
    """
    This section displays a sorted preview of your added matchups so far, with the most recent at the top. Once you are satisfied, click **"Download options"** to specify the format and size you want the output to be in.
    """
    df = pd.DataFrame(st.session_state.matchups).set_index("Matchup")
    mainboard = sorted(st.session_state.deck_data.get("mainboard", {}).keys())
    sideboard = sorted(st.session_state.deck_data.get("sideboard", {}).keys())
    ordered_columns = [col for col in mainboard if col in df.columns] + [
        col for col in sideboard if col in df.columns
    ]
    df = df[ordered_columns][::-1]
    df = df.loc[:, (df != "").any(axis=0)]
    pretty_df = df.rename(columns=st.session_state.card_labels)
    st.dataframe(pretty_df.fillna(""))

    if st.button("Download options"):
        fig = sb_mod.render_matrix_figure(df, st.session_state.card_labels)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        st.download_button(
            "Download PNG",
            data=buf.getvalue(),
            file_name="sideboard_guide.png",
            mime="image/png",
        )
        plt.close(fig)

# Development/Support links

st.sidebar.write(
    """
Thanks for using MTG Sideboarder!

Check out the changelogs or support development:
"""
)

st.sidebar.markdown(
    """
    <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
      <a href="https://github.com/NBrichta/mtg-sideboarder" target="_blank">
        <img src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
      </a>
      <a href="https://ko-fi.com/sideboarder" target="_blank">
        <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-fi">
      </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Divider
st.sidebar.markdown("---")

# Bug report
with st.sidebar.expander("🐛🖥️ &emsp; Submit a Bug Report"):
    bug_text = st.text_area(
        "This is my first attempt at building a web app so there are bound to be issues. Please describe the sequence of events that led to the error as best as you can here, or create an issue thread on the [GitHub](https://github.com/NBrichta/mtg-sideboarder/issues):",
        height=150,
    )
    include_session = st.checkbox(
        "Include session state (decklist and matchup info)", value=True
    )
    if st.button("Submit Report"):
        sb_mod.submit_bug_report(bug_text, include_session)


# Hard reset functionality
sb_mod.render_hard_reset_button()
