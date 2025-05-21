import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np
import requests

# === Utility Functions ===
@st.cache_data(show_spinner=False)
def parse_decklist(deck_text: str) -> dict[str,int]:
    """Parse MTGO‐style decklist into {card_name: quantity}."""
    deck = {}
    for line in deck_text.strip().splitlines():
        try:
            qty, name = line.strip().split(" ", 1)
            deck[name] = int(qty)
        except ValueError:
            continue
    return deck

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
    color_matrix = np.full(df_export.shape, '', dtype=object)
    for i in range(df_export.shape[0]):
        for j in range(df_export.shape[1]):
            val = df_export.iat[i, j]
            if isinstance(val, str):
                if val.startswith('+'):
                    matrix[i, j] = val[1:]
                    color_matrix[i, j] = '#b7e4c7'
                elif val.startswith('-'):
                    matrix[i, j] = val[1:]
                    color_matrix[i, j] = '#f4cccc'
                else:
                    matrix[i, j] = ''
            else:
                matrix[i, j] = ''

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
                        (j, matrix.shape[0] - i - 1),
                        1, 1,
                        color=color_matrix[i, j]
                    )
                )
                ax.text(
                    j + 0.5,
                    matrix.shape[0] - i - 0.5,
                    matrix[i, j],
                    ha="center", va="center",
                    fontsize=fontsize
                )

    # labels
    ax.set_xticks(np.arange(len(df_export.columns)) + 0.5)
    ax.set_xticklabels(
        [card_labels.get(col, col) for col in df_export.columns],
        rotation=45, ha="right", fontsize=9
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
    ax.grid(which='minor', color='black', linestyle='-', linewidth=1)
    ax.tick_params(which='minor', size=0)

    ax.invert_yaxis()
    plt.tight_layout()
    return fig

def submit_bug_report(bug_text, include_session):
    report_text = bug_text
    if include_session:
        report_text += f"\n---\nDeck: {st.session_state.get('deck_data')}\nMatchups: {st.session_state.get('matchups')}"

    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSe3VRA_G7MRTM0PHKlErHYMlH3YxTmiL_GuQrw0WaUSwxle4Q/formResponse"
    form_data = {
        "entry.1096092479": bug_text,
        "entry.258759295": report_text
    }

    try:
        requests.post(form_url, data=form_data)
        st.success("Bug report submitted. Thank you!!")
    except Exception as e:
        st.error(f"Failed to submit bug report: {e}. Please create an issue on [GitHub](https://github.com/NBrichta/mtg-sideboarder) and I'll try to address it as soon as I can.")

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
