import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np

st.set_page_config(page_title="MTG Sideboard Guide", layout="centered")
st.title("MTG Sideboarder")

# Step 1: Deck Input
st.header("Paste Your Decklist (MTGO Format)")
mainboard_text = st.text_area("Mainboard (e.g. 4 Lightning Bolt)", height=200)
sideboard_text = st.text_area("Sideboard (e.g. 2 Prismatic Ending)", height=100)

# Session state initialization
for key, default in [
    ("deck_data", {}),
    ("matchups", []),
    ("out_quantities", {}),
    ("in_quantities", {}),
    ("confirm_reset", False),
    ("search_out", []),
    ("search_in", []),
    ("opponent_name", ""),
    ("confirm_add", False),
    ("clear_fields", False),
    ("card_labels", {}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

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

# Submit Decklist and apply internal keys
if st.button("Submit Deck"):
    main_raw = parse_decklist(mainboard_text)
    side_raw = parse_decklist(sideboard_text)

    mainboard = {f"MB:{name}": qty for name, qty in main_raw.items()}
    sideboard = {f"SB:{name}": qty for name, qty in side_raw.items()}

    labels = {**{k: k[3:] for k in mainboard}, **{k: k[3:] for k in sideboard}}

    st.session_state.deck_data = {"mainboard": mainboard, "sideboard": sideboard}
    st.session_state.card_labels = labels
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
    st.multiselect(
        "Search (mainboard):",
        options=list(st.session_state.deck_data["mainboard"].keys()),
        format_func=lambda k: st.session_state.card_labels.get(k, k),
        key="search_out"
    )
    for card in st.session_state.search_out:
        qty = st.number_input(
            f"Quantity to take out: {st.session_state.card_labels[card]}",
            min_value=1,
            max_value=st.session_state.deck_data["mainboard"][card],
            key=f"qty_out_{card}"
        )
        st.session_state.out_quantities[card] = qty

    st.subheader("Search card(s) to bring IN:")
    st.multiselect(
        "Search (sideboard):",
        options=list(st.session_state.deck_data["sideboard"].keys()),
        format_func=lambda k: st.session_state.card_labels.get(k, k),
        key="search_in"
    )
    for card in st.session_state.search_in:
        qty = st.number_input(
            f"Quantity to bring in: {st.session_state.card_labels[card]}",
            min_value=1,
            max_value=st.session_state.deck_data["sideboard"][card],
            key=f"qty_in_{card}"
        )
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
    mainboard = sorted(st.session_state.deck_data.get("mainboard", {}).keys())
    sideboard = sorted(st.session_state.deck_data.get("sideboard", {}).keys())
    ordered_columns = [col for col in mainboard if col in df.columns] + [col for col in sideboard if col in df.columns]
    df = df[ordered_columns][::-1]
    df = df.loc[:, (df != "").any(axis=0)]

    pretty_df = df.rename(columns=st.session_state.card_labels)
    st.dataframe(pretty_df.fillna(""))

    # Step 4: Export to PNG
    if st.button("Download Options"):
        df_export = df[::-1].copy()
        matrix = np.empty(df_export.shape, dtype=object)
        color_matrix = np.full(df_export.shape, '', dtype=object)

        for i in range(df_export.shape[0]):
            for j in range(df_export.shape[1]):
                val = df_export.iloc[i, j]
                if isinstance(val, str):
                    if val.startswith('+'):
                        matrix[i, j] = val[1:]
                        color_matrix[i, j] = '#b7e4c7'
                    elif val.startswith('-'):
                        matrix[i, j] = val[1:]
                        color_matrix[i, j] = '#f4cccc'
                    else:
                        matrix[i, j] = ''

        fontsize = 12
        cell_size = fontsize * 0.1
        fig_width = df.shape[1] * cell_size
        fig_height = df.shape[0] * cell_size
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
        ax.set_xlim(0, matrix.shape[1])
        ax.set_ylim(0, matrix.shape[0])

        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if matrix[i, j] != '' and color_matrix[i, j] != '':
                    ax.add_patch(plt.Rectangle((j, matrix.shape[0] - i - 1), 1, 1, color=color_matrix[i, j]))
                    ax.text(j + 0.5, matrix.shape[0] - i - 0.5, matrix[i, j], ha="center", va="center", fontsize=fontsize)

        ax.set_xticks(np.arange(len(df.columns)) + 0.5)
        ax.set_xticklabels([st.session_state.card_labels.get(col, col) for col in df.columns], rotation=45, ha="right", fontsize=9)
        ax.set_yticks(np.arange(len(df.index)) + 0.5)
        ax.set_yticklabels(df.index[::-1], fontsize=10)

        ax.set_title("Sideboard Guide", fontsize=14)
        ax.tick_params(left=True, bottom=True)
        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_xticks(np.arange(matrix.shape[1]), minor=True)
        ax.set_yticks(np.arange(matrix.shape[0]), minor=True)
        ax.grid(which='minor', color='black', linestyle='-', linewidth=1)
        ax.tick_params(which='minor', size=0)

        ax.invert_yaxis()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        st.download_button("Download PNG", data=buf.getvalue(), file_name="sideboard_guide.png", mime="image/png")
        plt.close(fig)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    if not st.session_state.confirm_reset:
        if st.button("Hard Reset All Data", key="reset_confirm_button"):
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
