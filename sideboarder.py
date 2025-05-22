import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sideboarder_modular as sb_mod



# Set page config (MUST BE FIRST)
st.set_page_config(
    page_title="MTG Sideboard Guide", page_icon="./icon.ico",
    layout="centered", initial_sidebar_state="auto",
    menu_items={
        "Get Help": "https://github.com/NBrichta/mtg-sideboarder",
        "Report a bug": "https://github.com/NBrichta/mtg-sideboarder/issues",
        "About": "MTG Sideboarder is a passion project..."
    },
)

USE_DUMMY_MATCHUPS = False

# Inject custom CSS and set up page header
sb_mod.inject_css()
st.title("MTG Sideboarder")
st.markdown(
    """
    A lightweight UI for designing and exporting Magic: The Gathering sideboard guides.
    Follow the steps below to get started!
    """
)

# Initialize session state
sb_mod.initialize_session_state({
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
})

# Step 1: Deck input
sb_mod.render_deck_input_section()

# Step 2: Matchup entry
if st.session_state.deck_data:
    if USE_DUMMY_MATCHUPS:
        st.session_state.matchups = sb_mod.get_dummy_matchups()
    else:
        sb_mod.render_matchup_entry()

# Step 3: Matrix preview & download
sb_mod.render_matrix_section()

# Sidebar (links + bug report) and hard reset
sb_mod.render_sidebar()
sb_mod.render_hard_reset_button()