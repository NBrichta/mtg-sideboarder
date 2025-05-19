import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="MTG Sideboard Guide", layout="centered")
st.title("MTG Sideboarder")

# Step 1: Deck Input
st.header("Paste Your Decklist (MTGO Format)")
mainboard_text = st.text_area("Mainboard (e.g. 4 Lightning Bolt)", height=200)
sideboard_text = st.text_area("Sideboard (e.g. 2 Prismatic Ending)", height=100)

if "deck_data" not in st.session_state:
    st.session_state.deck_data = {}
if "matchups" not in st.session_state:
    st.session_state.matchups = []
if "out_quantities" not in st.session_state:
    st.session_state.out_quantities = {}
if "in_quantities" not in st.session_state:
    st.session_state.in_quantities = {}
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False
if "search_out" not in st.session_state:
    st.session_state.search_out = []
if "search_in" not in st.session_state:
    st.session_state.search_in = []
if "opponent_name" not in st.session_state:
    st.session_state.opponent_name = ""
if "confirm_add" not in st.session_state:
    st.session_state.confirm_add = False
if "clear_fields" not in st.session_state:
    st.session_state.clear_fields = False

# Helper function to parse pasted deck
@st.cache_data
def parse_decklist(deck_text):
    deck = {}
    for line in deck_text.strip().splitlines():
        try:
            qty, name = line.strip().split(" ", 1)
            deck[name] = int(qty)
        except ValueError:
            continue
    return deck

if st.button("Submit Deck"):
    st.session_state.deck_data = {
        "mainboard": parse_decklist(mainboard_text),
        "sideboard": parse_decklist(sideboard_text)
    }
    st.success("Decklist saved!")
    st.session_state.out_quantities = {}
    st.session_state.in_quantities = {}

# Step 2: Matchup Entry
if st.session_state.deck_data:
    st.header("Add Matchup Info")

    if st.session_state.clear_fields:
        st.session_state.search_out = []
        st.session_state.search_in = []
        st.session_state.opponent_name = ""
        st.session_state.out_quantities = {}
        st.session_state.in_quantities = {}
        st.session_state.clear_fields = False

    st.session_state.opponent_name = st.text_input("Opposing Deck Name", value=st.session_state.opponent_name)

    st.subheader("Search card(s) to take OUT")
    st.multiselect("Search (mainboard):", list(st.session_state.deck_data["mainboard"].keys()), key="search_out")
    for card in st.session_state.search_out:
        qty = st.number_input(f"Quantity to take out: {card}", min_value=1, max_value=st.session_state.deck_data["mainboard"][card], key=f"qty_out_{card}")
        st.session_state.out_quantities[card] = qty

    st.subheader("Search card(s) to bring IN:")
    st.multiselect("Search (sideboard):", list(st.session_state.deck_data["sideboard"].keys()), key="search_in")
    for card in st.session_state.search_in:
        qty = st.number_input(f"Quantity to bring in: {card}", min_value=1, max_value=st.session_state.deck_data["sideboard"][card], key=f"qty_in_{card}")
        st.session_state.in_quantities[card] = qty

    if not st.session_state.confirm_add:
        if st.button("Add Matchup") and st.session_state.opponent_name:
            st.session_state.confirm_add = True
            st.rerun()
    else:
        st.warning("Click 'Confirm Add' to submit, or 'Cancel' to undo. Confirming will clear all entry fields.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Add"):
                used_cards = set(st.session_state.out_quantities.keys()) | set(st.session_state.in_quantities.keys())
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

# Step 3: Matchup Matrix Preview
if st.session_state.matchups:
    st.header("Sideboard Matrix Preview")
    df = pd.DataFrame(st.session_state.matchups).set_index("Matchup")
    df = df.loc[:, (df != "").any(axis=0)]  # Keep only columns with at least one non-empty value
    st.dataframe(df.fillna(""))

    # Step 4: Export to PNG
    if st.button("Download Options"):
        fig, ax = plt.subplots(figsize=(len(df.columns) * 0.5 + 2, len(df.index) * 0.5 + 1))
        ax.axis("off")
        table = ax.table(cellText=df.fillna("").values,
                 rowLabels=df.index.tolist(),
                 colLabels=df.columns.tolist(),
                 cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        st.download_button("Download PNG", data=buf.getvalue(), file_name="sideboard_guide.png", mime="image/png")
        plt.close(fig)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    if not st.session_state.confirm_reset:
        if st.button("🔄 Hard Reset All Data", key="reset_confirm_button"):
            st.session_state.confirm_reset = True
    else:
        st.warning("This will clear all session data. Are you sure?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Reset", key="confirm_reset_yes"):
                st.session_state.clear()
                st.rerun()
        with col2:
            if st.button("Cancel", key="confirm_reset_cancel"):
                st.session_state.confirm_reset = False
