# create.py
import streamlit as st
import sideboarder_modular as sb_mod


# Set page config (MUST BE FIRST)
st.set_page_config(
    page_title="Create - SideBoarder",
    page_icon="./images/icon.ico",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": "mailto:sideboarder.dev@gmail.com",
        "Report a bug": "https://github.com/NBrichta/mtg-sideboarder/issues",
        "About": "MTG Sideboarder is a passion project borne out of a frustration with clunky Excel spreadsheets and a love for Magic: The Gathering. I cannot express how thankful I am to everyone who has supported its development.",
    },
)

USE_DUMMY_MATCHUPS = False  # Inputs matchup_data automatically to save development time. Checked for False on commit.

# Inject custom CSS and set up page header
sb_mod.inject_css()
st.title("SideBoarder Generator")
st.markdown(
    """
    Generate a new sideboard guide by following the steps below:
    """
)

# Initialize session state
sb_mod.initialize_session_state(
    {
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
)


# Step 1: Deck input
if not st.session_state.deck_data:
    sb_mod.render_deck_input_section()


else:
    # Deck is locked: show disabled text‐areas + URL
    st.header("Decklist (locked)")
    sb_mod.section_divider()

    labels = st.session_state.card_labels
    mb = st.session_state.deck_data["mainboard"]
    sb = st.session_state.deck_data["sideboard"]

    main_lines = [f"{qty} {labels[k]}" for k, qty in mb.items()]
    side_lines = [f"{qty} {labels[k]}" for k, qty in sb.items()]

    st.text_area(
        "Mainboard",
        value="\n".join(main_lines),
        height=200,
        disabled=True,
        key="mainboard_readonly",
    )
    st.text_area(
        "Sideboard",
        value="\n".join(side_lines),
        height=100,
        disabled=True,
        key="sideboard_readonly",
    )

    # if they imported from Goldfish, show that too
    if st.session_state.get("gf_url"):
        st.text_input(
            "MTGGoldfish deck URL",
            value=st.session_state.gf_url,
            disabled=True,
            key="gf_url_readonly",
        )

    # Reset button
    if st.button(":red[Reset Decklist]"):
        st.session_state.clear()
        st.rerun()


# Step 2: Matchup entry
if st.session_state.deck_data:
    if (
        USE_DUMMY_MATCHUPS
    ):  # could probably nest this within sb_mod.render_matchup_entry(), but who cares
        st.session_state.matchups = sb_mod.get_dummy_matchups()
    else:
        st.header("Add Matchup Info")
        sb_mod.section_divider()
        sb_mod.render_matchup_entry()

# Step 3: Matrix preview & download
sb_mod.render_matrix_section()

# Sidebar (links + bug report) and hard reset
sb_mod.render_sidebar()
sb_mod.render_hard_reset_button()
