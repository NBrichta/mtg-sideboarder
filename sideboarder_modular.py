import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np
import requests


# === DEV MODE OPTIONS ===
def get_matchups_from_ui():
    st.header("Enter your matchups")
    num = st.number_input("How many matchups?", min_value=1, max_value=8, value=2)
    matchups = []
    for i in range(num):
        col1, col2, col3 = st.columns([2, 3, 3])
        with col1:
            opp = st.text_input(f"Opponent {i+1}", key=f"opp_{i}")
        with col2:
            ins = st.text_area(
                f"Cards IN vs {i+1}", placeholder="comma-separated", key=f"in_{i}"
            )
        with col3:
            outs = st.text_area(
                f"Cards OUT vs {i+1}", placeholder="comma-separated", key=f"out_{i}"
            )
        ins_list = [c.strip() for c in ins.split(",") if c.strip()]
        outs_list = [c.strip() for c in outs.split(",") if c.strip()]
        matchups.append({"opponent": opp, "ins": ins_list, "outs": outs_list})
    return matchups


def get_dummy_matchups():
    return [
        {
            "opponent": "Mono‐Green Stompy",
            "ins": ["Path to Exile", "Leyline of Sanctity"],
            "outs": ["Wild Growth", "Llanowar Elves"],
        },
        {
            "opponent": "Burn",
            "ins": ["Eidolon of the Great Revel"],
            "outs": ["Goblin Guide", "Lightning Bolt"],
        },
    ]


# ========================


# === Decklist Parser ===
@st.cache_data(show_spinner=False)
def parse_decklist(deck_text: str) -> dict[str, int]:
    """Parse MTGO‐style decklist into {card_name: quantity}."""
    deck = {}
    for line in deck_text.strip().splitlines():
        try:
            qty, name = line.strip().split(" ", 1)
            deck[name] = int(qty)
        except ValueError:
            continue
    return deck


# ========================


# === Matchup Entry ===
def render_matchup_entry():
    # only run if deck_data exists
    if st.session_state.deck_data:
        st.header("Add Matchup Info")
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
        In this section, you first define a name for the archetype you are sideboarding for,
        then search the cards you would like to remove from your mainboard and the cards
        you would like to add in from your sideboard. Then click **"Add Matchup>Confirm"**
        to add your choices to your sideboard guide.
        """

        # clear form fields if flagged
        if st.session_state.clear_fields:
            st.session_state.search_out = []
            st.session_state.search_in = []
            st.session_state.opponent_name = ""
            st.session_state.out_quantities = {}
            st.session_state.in_quantities = {}
            st.session_state.clear_fields = False

        # opponent name
        st.session_state.opponent_name = st.text_input(
            "Opposing Archetype Name",
            value=st.session_state.opponent_name,
            placeholder="e.g. Boros Energy",
        )

        # OUT cards
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

        # IN cards
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

        # Add / confirm buttons
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


# ========================


# === Render Export ===
@st.cache_data(show_spinner=False)
def render_matrix_figure(df: pd.DataFrame, card_labels: dict[str, str]) -> plt.Figure:
    """
    Render the sideboard matrix as a matplotlib Figure, caching the result
    so it only re-draws when `df` or `card_labels` change.
    """
    # flip rows so the first index is at the top
    df_export = df[::-1].copy()

    # build a matrix of text + background colors
    matrix = np.empty(df_export.shape, dtype=object)
    color_matrix = np.full(df_export.shape, "", dtype=object)
    for i in range(df_export.shape[0]):
        for j in range(df_export.shape[1]):
            val = df_export.iat[i, j]
            if isinstance(val, str):
                if val.startswith("+"):
                    matrix[i, j] = val[1:]
                    color_matrix[i, j] = "#b7e4c7"
                elif val.startswith("-"):
                    matrix[i, j] = val[1:]
                    color_matrix[i, j] = "#f4cccc"
                else:
                    matrix[i, j] = ""
            else:
                matrix[i, j] = ""

    # sizing
    fontsize = 12
    cell_size = fontsize * 0.1
    fig_width = df_export.shape[1] * cell_size
    fig_height = df_export.shape[0] * cell_size

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
    ax.set_xlim(0, matrix.shape[1])
    ax.set_ylim(0, matrix.shape[0])

    # draw colored rectangles + text
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i, j] and color_matrix[i, j]:
                ax.add_patch(
                    plt.Rectangle(
                        (j, matrix.shape[0] - i - 1), 1, 1, color=color_matrix[i, j]
                    )
                )
                ax.text(
                    j + 0.5,
                    matrix.shape[0] - i - 0.5,
                    matrix[i, j],
                    ha="center",
                    va="center",
                    fontsize=fontsize,
                )

    # labels
    ax.set_xticks(np.arange(len(df_export.columns)) + 0.5)
    ax.set_xticklabels(
        [card_labels.get(col, col) for col in df_export.columns],
        rotation=45,
        ha="right",
        fontsize=9,
    )
    ax.set_yticks(np.arange(len(df_export.index)) + 0.5)
    ax.set_yticklabels(df_export.index, fontsize=10)

    ax.set_title("Sideboard Guide", fontsize=14)
    ax.tick_params(left=True, bottom=True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # grid lines behind cells
    ax.set_xticks(np.arange(matrix.shape[1]), minor=True)
    ax.set_yticks(np.arange(matrix.shape[0]), minor=True)
    ax.grid(which="minor", color="black", linestyle="-", linewidth=1)
    ax.tick_params(which="minor", size=0)

    ax.invert_yaxis()
    plt.tight_layout()
    return fig


# ========================


# === Bug Reporting ===
def submit_bug_report(bug_text, include_session):
    report_text = bug_text
    if include_session:
        report_text += f"\n---\nDeck: {st.session_state.get('deck_data')}\nMatchups: {st.session_state.get('matchups')}"

    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSe3VRA_G7MRTM0PHKlErHYMlH3YxTmiL_GuQrw0WaUSwxle4Q/formResponse"
    form_data = {"entry.1096092479": bug_text, "entry.258759295": report_text}

    try:
        requests.post(form_url, data=form_data)
        st.success("Bug report submitted. Thank you!!")
    except Exception as e:
        st.error(
            f"Failed to submit bug report: {e}. Please create an issue on [GitHub](https://github.com/NBrichta/mtg-sideboarder) and I'll try to address it as soon as I can."
        )


# ========================


# === Reset Button ===
def render_hard_reset_button():
    st.sidebar.markdown("💔 Help, I've made a huge mistake!")

    if not st.session_state.get("confirm_reset", False):
        if st.sidebar.button(":red[Hard Reset All Data]", key="reset_confirm_button"):
            st.session_state.confirm_reset = True
            st.rerun()
    else:
        st.sidebar.warning("This will clear all session data. Are you sure?")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Yes, Reset", key="confirm_reset_yes"):
                st.session_state.clear()
                st.rerun()
        with col2:
            if st.button("Cancel", key="confirm_reset_cancel"):
                st.session_state.confirm_reset = False
                st.rerun()


# ========================
