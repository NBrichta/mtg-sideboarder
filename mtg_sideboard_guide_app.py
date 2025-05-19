import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="MTG Sideboard Guide", layout="wide")
st.title("MTG Sideboard Guide Generator")

# Step 1: Deck Input
st.header("1. Paste Your Deck")
mainboard_text = st.text_area("Mainboard (e.g. 4 Lightning Bolt)", height=200)
sideboard_text = st.text_area("Sideboard (e.g. 2 Prismatic Ending)", height=100)

if "deck_data" not in st.session_state:
    st.session_state.deck_data = {}
if "matchups" not in st.session_state:
    st.session_state.matchups = []

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
    st.success("Deck submitted! Now add matchups.")

# Step 2: Matchup Entry
if st.session_state.deck_data:
    st.header("2. Add Matchup Guide")
    opponent_name = st.text_input("Opponent Deck Name")

    st.subheader("Select cards to take OUT (from mainboard):")
    outs = st.multiselect("Out:", list(st.session_state.deck_data["mainboard"].keys()))

    st.subheader("Select cards to bring IN (from sideboard):")
    ins = st.multiselect("In:", list(st.session_state.deck_data["sideboard"].keys()))

    if st.button("Add Matchup") and opponent_name:
        matchup_row = {card: "" for card in list(st.session_state.deck_data["mainboard"].keys()) + list(st.session_state.deck_data["sideboard"].keys())}
        for card in outs:
            matchup_row[card] = "-1"
        for card in ins:
            matchup_row[card] = "+1"
        matchup_row["Matchup"] = opponent_name
        st.session_state.matchups.append(matchup_row)
        st.success(f"Matchup '{opponent_name}' added!")

# Step 3: Matrix Display
if st.session_state.matchups:
    st.header("3. Sideboard Matrix")
    df = pd.DataFrame(st.session_state.matchups).set_index("Matchup")
    st.dataframe(df.fillna(""))

    # Step 4: Export to PNG
    if st.button("Download Options"):
        fig, ax = plt.subplots(figsize=(len(df.columns) * 0.5 + 2, len(df.index) * 0.5 + 1))
        ax.axis("off")
        table = ax.table(cellText=df.fillna("").values,  # <-- Use raw values only
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
