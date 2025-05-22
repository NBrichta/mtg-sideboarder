import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import io

def inject_css(): # Any custom CSS gets loaded in with this function. Should be moved to a style.css when I have the time
    st.markdown(  # Differentiate fonts between inside vs. outside text entry boxes
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

def custom_info( # A custom info box container for color scheme purposes. Need to add some blank space between the box and the Confirm/Cancel buttons
    text: str,
    bg_color: str = "#9DC7C8",
    border_color: str = "#9DC7C8",
    text_color: str = "#3C3D37",
):
    st.markdown(
        f"""
        <div style="
            background-color: {bg_color};
            border-left: 4px solid {border_color};
            color: {text_color};
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
        ">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_divider():  # Just makes a red underline for section headers according to current color scheme
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


def initialize_session_state(defaults: dict): # First step -> sets up the default values for the session data
    """Initialize Streamlit session state with provided defaults."""
    for key, default in defaults.items():
        st.session_state.setdefault(key, default)


def get_dummy_matchups(): # DEV MODE ONLY -> saves having to enter matchups manually to test stuff
    # pull your actual keys out of session_state:
    mb = list(st.session_state.deck_data["mainboard"].keys())
    sb = list(st.session_state.deck_data["sideboard"].keys())
    return [
        {mb[0]: "-2", sb[0]: "+2", "Matchup": "Mono-Green Stompy"},
        {mb[1]: "-1", sb[1]: "+1", "Matchup": "Burn"},
        {mb[2]: "-2", sb[5]: "+2", "Matchup": "Blue Tempo"},  # re-uses sb[0]
        {mb[3]: "-1", sb[2]: "+1", "Matchup": "Gruul Midrange"},
        {mb[0]: "-3", sb[3]: "+3", "Matchup": "Tron Lands"},  # re-uses mb[0]
        {mb[4]: "-2", sb[4]: "+2", "Matchup": "UW Control"},
        {mb[1]: "-2", sb[2]: "+2", "Matchup": "Jund"},  # re-uses sb[2]
        {mb[2]: "-1", sb[1]: "+1", "Matchup": "Affinity"},  # re-uses sb[1]
        {mb[7]: "-2", sb[4]: "+2", "Matchup": "UW Control"},
        {mb[1]: "-2", sb[2]: "+2", "Matchup": "Jund"},  # re-uses sb[2]
        {mb[2]: "-1", sb[1]: "+1", "Matchup": "Affinity"},  # re-uses sb[1]
    ]


def render_deck_input_section(): # Renders the section for entering decklist text
    """Step 1: Deck input UI and submission logic."""
    st.header(
        "Import Decklist",
        help=(
            "Your decklist data **must** be in MTGO formatting (e.g. `4~Card~Name`)."
            "  Support for importing from URLs is a high priority once I figure out how APIs work."
        ),
    )
    section_divider()
    st.markdown(
        """
        This section lets you import your decklist in standard MTGO formatting.
        Once submitted, you can proceed to add matchup-sideboard choices.
        """
    )
    mainboard_text = st.text_area(
        "Mainboard", height=200,
        placeholder="4 Amulet of Vigor\n4 Primeval Titan\n3 Scapeshift\netc.",
    )
    sideboard_text = st.text_area(
        "Sideboard", height=100,
        placeholder="1 Boseiju, Who Endures\n2 Dismember\netc.",
    )
    if st.button("Submit Deck"):
        main_raw = parse_decklist(mainboard_text)
        side_raw = parse_decklist(sideboard_text)
        mainboard = {f"MB:{name}": qty for name, qty in main_raw.items()}
        sideboard = {f"SB:{name}": qty for name, qty in side_raw.items()}
        labels = {**{k: k[3:] for k in mainboard}, **{k: k[3:] for k in sideboard}}

        st.session_state.deck_data = {"mainboard": mainboard, "sideboard": sideboard}
        st.session_state.card_labels = labels
        st.toast("Decklist saved!")


@st.cache_data(show_spinner=False)
def parse_decklist(deck_text: str) -> dict[str, int]: # Parses the decklist text into mainboard and sideboard quantities
    """Parse MTGO‐style decklist into {card_name: quantity}."""
    deck = {}
    for line in deck_text.strip().splitlines():
        try:
            qty, name = line.strip().split(" ", 1)
            deck[name] = int(qty)
        except ValueError:
            continue
    return deck


def render_matchup_entry(): # Renders the section for entering matchup data 
    # only run if deck_data exists
    MAX_OPPONENT_NAME_LENGTH = 25 # prevent absurdly long deck names
    if st.session_state.deck_data:
        st.header("Add Matchup Info")

        section_divider()

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

        # ─── Opponent name input ───────────────────────────────────────────────
        name = st.text_input(
            f"Opposing Archetype Name (max {MAX_OPPONENT_NAME_LENGTH} chars)",
            value=st.session_state.opponent_name,
            placeholder="e.g. Boros Energy",
            key="opponent_name",
        )
        # (Streamlit auto-updates st.session_state.opponent_name for us)
        # ───────────────────────────────────────────────────────────────────────

        # OUT cards
        st.html('<h2>Card(s) to take <span style="color:#f7b2ad;">OUT</span>:</h2>')
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
        st.html('<h2>Card(s) to bring <span style="color:#9abca7;">IN</span>:</h2>')
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

        # ─── Add / confirm buttons ──────────────────────────────────────────────
        if not st.session_state.confirm_add:
            # always show the button, but validate on click
            if st.button("Add Matchup"):
                total_out = sum(st.session_state.out_quantities.values())
                total_in = sum(st.session_state.in_quantities.values())
                if not name.strip():
                    st.error("Please enter an opposing archetype name.")
                elif len(name) > MAX_OPPONENT_NAME_LENGTH:
                    st.error(
                        f"Archetype name exceeds {MAX_OPPONENT_NAME_LENGTH}-character limit.")
                elif total_out == 0 and total_in ==0:
                    st.error(
                        "You’ve entered a matchup name but haven’t selected any cards to remove or add. Please pick at least one card to proceed."
                    )
                else:
                    st.session_state.confirm_add = True
                    st.rerun()
        else:
            # ─── Quantity‐match check ─────────────────────────────────────────
            total_out = sum(st.session_state.out_quantities.values())
            total_in = sum(st.session_state.in_quantities.values())
            if total_out != total_in:
                st.warning(
                    f"Warning: you’re removing {total_out} card"
                    f"{'s' if total_out!=1 else ''} but adding {total_in} "
                    f"card{'s' if total_in!=1 else ''}. "
                    "This will result in a library with more or less than 60 cards. Click 'Cancel' if you'd like to change this."
                )

            # finalize or cancel
            custom_info("Click Confirm to finalize or Cancel to undo.")

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
                    st.session_state.clear_fields = True
                    st.rerun()
        # ───────────────────────────────────────────────────────────────────────


def render_matrix_section(): # Renders the preview matrix and download options
    """Step 3: Matrix preview and PNG download."""
    if not st.session_state.matchups:
        return
    st.header("Sideboard Matrix Preview")
    section_divider()
    st.markdown(
        """
        This section displays a sorted preview of your added matchups.
        Click **Download options** to export the matrix as a PNG.
        """
    )
    df = pd.DataFrame(st.session_state.matchups).set_index("Matchup")
    mb = sorted(st.session_state.deck_data.get("mainboard", {}).keys())
    sb = sorted(st.session_state.deck_data.get("sideboard", {}).keys())
    cols = [c for c in mb if c in df.columns] + [c for c in sb if c in df.columns]
    df = df[cols][::-1]
    df = df.loc[:, (df != "").any(axis=0)]
    st.dataframe(df)

    if st.button("Download options"):
        fig = render_matrix_figure(df, st.session_state.card_labels)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300)
        buf.seek(0)
        st.download_button(
            "Download matrix as PNG",
            data=buf,
            file_name="sideboard-matrix.png",
            mime="image/png",
            use_container_width=True,
        )
        plt.close(fig)


@st.cache_data(show_spinner=False)
def render_matrix_figure(df: pd.DataFrame, card_labels: dict[str, str]) -> plt.Figure: # Renders the image that gets exported
    """
    Render the sideboard matrix as a matplotlib Figure, caching the result
    so it only re-draws when `df` or `card_labels` change.
    """
    # flip rows so the first index is at the top
    df_export = df[::-1].copy()

    # build a matrix of text + background colors
    matrix = np.empty(df_export.shape, object)
    color_m = np.full(df_export.shape, "", object)
    for i in range(df_export.shape[0]):
        for j in range(df_export.shape[1]):
            v = df_export.iat[i, j]
            if isinstance(v, str) and v:
                matrix[i, j] = v.lstrip("+-")
                color_m[i, j] = "#9abca7" if v.startswith("+") else "#f7b2ad"
            else:
                matrix[i, j] = ""

    # ─── MAGIC CARD SIZING ─────────────────────────────────────────────────
    # force the figure to Magic card dimensions: 2.5" wide × 3.5" tall
    fig, ax = plt.subplots(figsize=(2.5, 3.5), constrained_layout=True)
    ax.set_aspect("auto")

    name_fontsize = 5

    # ────────────────────────────────────────────────────────────────────────────

    ax.set_xlim(0, matrix.shape[1])
    ax.set_ylim(0, matrix.shape[0])

    # draw cells + numbers
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i, j]:
                ax.add_patch(
                    plt.Rectangle(
                        (j, matrix.shape[0] - i - 1), 1, 1, color=color_m[i, j]
                    )
                )
                ax.text(
                    j + 0.5,
                    matrix.shape[0] - i - 0.5,
                    matrix[i, j],
                    ha="center",
                    va="center",
                    fontsize=6,
                )

    # ticks + labels
    ax.set_xticks(np.arange(df_export.shape[1]) + 0.5)
    ax.set_xticklabels(
        [card_labels.get(c, c) for c in df_export.columns],
        rotation=50,
        ha="right",
        fontsize=name_fontsize,
    )
    ax.set_yticks(np.arange(df_export.shape[0]) + 0.5)
    ax.set_yticklabels(df_export.index, fontsize=name_fontsize)

    # Title
    # ax.set_title("Sideboard Guide", fontsize=title_fontsize)

    # draw grid behind cells
    ax.set_xticks(np.arange(matrix.shape[1]), minor=True)
    ax.set_yticks(np.arange(matrix.shape[0]), minor=True)
    # ax.grid(which="minor", color="black", alpha=0.5, linestyle="-", linewidth=0.5)
    ax.tick_params(which="minor", size=0)
    for s in ax.spines.values():
        s.set_visible(True)
    # flip so the “first” row is at the top
    # ax.invert_yaxis()

    # ─── add a thin black border around the *whole* image ───────────────
    fig.patch.set_edgecolor("black")
    fig.patch.set_linewidth(1)
    # ─────────────────────────────────────────────────────────────────────

    return fig


def render_sidebar(): # Renders the sidebar text and options
    """Render sidebar links, badges, and bug-report expander."""
    st.sidebar.write(
        """
        Thanks for using **MTG Sideboarder!**

        Check out the changelogs or support development:
        """
    )
    st.sidebar.markdown(
        """
        <div style="display:flex;justify-content:space-between;width:100%;align-items:center;">
          <a href="https://github.com/NBrichta/mtg-sideboarder" target="_blank">
            <img src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white">
          </a>
          <a href="https://ko-fi.com/sideboarder" target="_blank">
            <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white">
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    with st.sidebar.expander("🐛🖥️  Submit a Bug Report"):
        bug = st.text_area("Describe the issue:", height=150)
        incl = st.checkbox("Include session state (deck + matchups)", value=True)
        if st.button("Submit Report"):
            submit_bug_report(bug, incl)


def submit_bug_report(bug_text, include_session): # Tells the app where to send bug reports
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


def render_hard_reset_button(): # Renders the session reset button
    st.sidebar.markdown("💔 Help, I've made a huge mistake!")

    if not st.session_state.get("confirm_reset", False):
        if st.sidebar.button(":red[Reset Session Data]", key="reset_confirm_button"):
            st.session_state.confirm_reset = True
            st.rerun()
    else:
        st.sidebar.warning(
            "This will clear your decklist and matchup matrix data. Are you sure?"
        )
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Yes, Reset", key="confirm_reset_yes"):
                st.session_state.clear()
                st.rerun()
        with col2:
            if st.button("Cancel", key="confirm_reset_cancel"):
                st.session_state.confirm_reset = False
                st.rerun()

