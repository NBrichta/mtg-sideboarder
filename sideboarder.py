import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np
import sideboarder_modular as sb_mod

st.set_page_config(page_title="MTG Sideboard Guide", layout="wide")
st.title("MTG Sideboarder")
"""
A lightweight web app for designing and exporting Magic: The Gathering sideboard guides.

Built using Python 3.1 and Streamlit.

Links:   [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=flat&logo=github&logoColor=white)](https://github.com/NBrichta/mtg-sideboarder)[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=flat&logo=ko-fi&logoColor=white)](https://ko-fi.com/sideboarder)
"""
# =========== Step 1: Deck Input
st.header(
    "Import Decklist",
    divider="grey",
    help="Your decklist data **must** be in MTGO formatting for this to work properly. In the future, importing decklists from URLs is a high priority once I figure out how APIs work.",
)
"""
This section lets you import your decklist in standard MTGO format. Once you click **"Submit Deck"**, the cards will automatically be parsed into mainboard and sideboard libraries for the search bars in the next section.
"""

decklist_text = st.text_input(
    "Your Decklist Name",
    placeholder="This is optional. If left blank, the exported guide will be untitled.",
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

# ============= Step 2: Matchup Entry
if st.session_state.deck_data:
    st.header("Add Matchup Info", divider="grey")
    """
    In this section, you first define a name for the archetype you are sideboarding for, then search the cards you would like to remove from your mainboard and the cards you would like to add in from your sideboard. Then click **"Add Matchup>Confirm"** to add your choices to your sideboard guide.
    """

    if st.session_state.clear_fields:
        st.session_state.search_out = []
        st.session_state.search_in = []
        st.session_state.opponent_name = ""
        st.session_state.out_quantities = {}
        st.session_state.in_quantities = {}
        st.session_state.clear_fields = False

    st.session_state.opponent_name = st.text_input(
        "Opposing Archetype Name",
        value=st.session_state.opponent_name,
        placeholder="e.g. Boros Energy",
    )

    st.subheader("Card(s) to take :red[OUT]:")
    st.multiselect(
        "Search:",
        options=list(st.session_state.deck_data["mainboard"].keys()),
        format_func=lambda k: st.session_state.card_labels.get(k, k),
        key="search_out",
    )
    for card in st.session_state.search_out:
        qty = st.number_input(
            f"Quantity to take out: {st.session_state.card_labels[card]}",
            min_value=1,
            max_value=st.session_state.deck_data["mainboard"][card],
            key=f"qty_out_{card}",
        )
        st.session_state.out_quantities[card] = qty

    st.subheader("Card(s) to bring :green[IN]:")
    st.multiselect(
        "Search:",
        options=list(st.session_state.deck_data["sideboard"].keys()),
        format_func=lambda k: st.session_state.card_labels.get(k, k),
        key="search_in",
    )
    for card in st.session_state.search_in:
        qty = st.number_input(
            f"Quantity to bring in: {st.session_state.card_labels[card]}",
            min_value=1,
            max_value=st.session_state.deck_data["sideboard"][card],
            key=f"qty_in_{card}",
        )
        st.session_state.in_quantities[card] = qty

    if not st.session_state.confirm_add:
        if st.button("Add Matchup"):
            if st.session_state.opponent_name.strip() == "":
                st.warning("Please enter an opposing archetype name.")
            else:
                st.session_state.confirm_add = True
                st.rerun()
    else:
        st.warning("Click Confirm to finalize or Cancel to undo.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm"):
                used_cards = set(st.session_state.out_quantities) | set(
                    st.session_state.in_quantities
                )
                matchup_row = {card: "" for card in used_cards}
                for card, qty in st.session_state.out_quantities.items():
                    matchup_row[card] = f"-{qty}"
                for card, qty in st.session_state.in_quantities.items():
                    matchup_row[card] = f"+{qty}"
                matchup_row["Matchup"] = st.session_state.opponent_name
                st.session_state.matchups.append(matchup_row)
                st.success(f"Matchup '{st.session_state.opponent_name}' added!")
                st.session_state.clear_fields = True
                st.session_state.confirm_add = False
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.confirm_add = False
                st.rerun()

# Matrix preview
if st.session_state.matchups:
    st.header("Sideboard Matrix Preview")
    """
    This section displays a sorted preview of your added matchups so far, with the most recent at the top. Once you are satisfied, click **"Download Options"** to specify the format you want the output to be in.
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

    if st.button("Download PNG"):
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

# Bug report
with st.sidebar.expander("🐛🖥️ Submit a Bug Report"):
    bug_text = st.text_area(
        "This is my first attempt at building a web app so there are bound to be issues. Please describe the sequence of events that led to the error as best as you can:",
        height=150,
    )
    include_session = st.checkbox(
        "Include session state (decklist and matchup info)", value=True
    )
    if st.button("Submit Report"):
        sb_mod.submit_bug_report(bug_text, include_session)

# Divider under bug report
st.sidebar.markdown("---")

# Hard reset functionality
sb_mod.render_hard_reset_button()
