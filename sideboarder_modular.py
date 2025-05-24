# sideboarder_modular.py = sb_mod
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import io
import re
from hashlib import sha1
import json
from datetime import date
from PIL import Image


def inject_css():  # Any custom CSS gets loaded in with this function. Should be moved to a style.css when I have the time
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


def custom_info(  # A custom info box container for color scheme purposes. Need to add some blank space between the box and the Confirm/Cancel buttons
    text: str,
    bg_color: str = "#9abca7",
    border_color: str = "#3C3D37",
    text_color: str = "#181C14",
):
    st.markdown(
        f"""
        <div style="
            background-color: {bg_color};
            border-left: 8px solid {border_color};
            color: {text_color};
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
        ">
            {text}
        </div>
        <div style='height:1rem'></div>
        """,
        unsafe_allow_html=True,
    )


def splash_buttons():
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        st.link_button(
            "Generate a new sideboard guide",
            "/create",
            type="primary",
            icon=":material/open_in_new:",
            use_container_width=True,
        )
    col4, col5, col6 = st.columns([0.2, 0.6, 0.2])
    with col5:
        st.link_button(
            "Edit a saved sideboard guide",
            "/editor",
            type="secondary",
            icon=":material/edit:",
            use_container_width=True,
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


def initialize_session_state(
    defaults: dict,
):  # First step -> sets up the default values for the session data
    """Initialize Streamlit session state with provided defaults."""
    for key, default in defaults.items():
        st.session_state.setdefault(key, default)


@st.cache_data
def import_deck_from_goldfish(url: str) -> dict[str, dict[str, int]]:
    """
    Given a MTGGoldfish deck URL, returns a dict:
    {
      'mainboard': { card_name: count, … },
      'sideboard': { card_name: count, … }
    }
    """
    # 1. pull the numeric ID from the URL
    m = re.search(r"/deck/(\d+)", url)
    if not m:
        st.error(
            "❌ Couldn't parse a deck from that URL. Make sure your link contains `.../deck/[deck_id]`. "
        )
        return {}
    deck_id = m.group(1)

    # 2. hit Goldfish’s download endpoint
    download_url = f"https://www.mtggoldfish.com/deck/download/{deck_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(download_url, headers=headers)
    if resp.status_code != 200:
        st.error(f"❌ Failed to fetch deck (HTTP {resp.status_code}).")
        return {}

    # 3. split into lines, track mainboard vs sideboard
    text = resp.text.strip()
    lines = text.splitlines()
    deck = {"mainboard": {}, "sideboard": {}}
    zone = "mainboard"
    for line in lines:
        line = line.strip()
        if not line:
            # if there's a blank line, switch to sideboard
            zone = "sideboard"
            continue
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        count, name = parts
        try:
            deck[zone][name.strip()] = int(count)
        except ValueError:
            # skip malformed lines
            continue

    # ─── namespace cards so MB and SB entries never collide ─────────────────
    deck["mainboard"] = {f"MB:{name}": cnt for name, cnt in deck["mainboard"].items()}
    deck["sideboard"] = {f"SB:{name}": cnt for name, cnt in deck["sideboard"].items()}

    return deck


def get_dummy_matchups():  # DEV MODE ONLY -> saves having to enter matchups manually to test stuff

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


def render_deck_input_section():  # Renders the section for entering decklist text
    """Step 1: Deck input UI and submission logic."""
    st.header(
        "Import Decklist",
        help=(
            "For this section to work properly, your decklist data **must** be in MTGO formatting for the parser to interpret the values (e.g. `4 Llanowar Elves`). Currently, importing from URLs only works for MTGGoldfish but I plan to add more deckbuilding sites (Moxfield, CubeCobra, Scryfall, etc.) in the future."
        ),
    )
    section_divider()
    # a) Goldfish import
    gf_url = st.text_input(
        "Paste MTGGoldfish deck URL",
        placeholder="e.g. https://www.mtggoldfish.com/deck/[deck_id]#paper",
        key="gf_url",
    )
    if st.button("Import Goldfish deck"):
        with st.spinner("Importing…"):
            imported = import_deck_from_goldfish(gf_url)
        if imported:
            st.session_state.deck_data = {
                "mainboard": imported["mainboard"],
                "sideboard": imported["sideboard"],
            }
            labels = {key: key[3:] for key in imported["mainboard"].keys()}
            labels.update({key: key[3:] for key in imported["sideboard"].keys()})
            st.session_state.card_labels = labels
            st.success("✅ Deck imported!")
            st.rerun()

    st.markdown(
        """
        or copy-paste your decklist in standard MTGO formatting:
        """
    )
    mainboard_text = st.text_area(
        "Mainboard",
        height=200,
        placeholder="4 Amulet of Vigor\n4 Primeval Titan\n3 Scapeshift\netc.",
    )
    sideboard_text = st.text_area(
        "Sideboard",
        height=100,
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
        st.success("✅ Deck saved!")
        st.rerun()


@st.cache_data(show_spinner=False)
def parse_decklist(
    deck_text: str,
) -> dict[str, int]:  # Parses the decklist text into mainboard and sideboard quantities
    """Parse MTGO‐style decklist into {card_name: quantity}."""
    deck = {}
    for line in deck_text.strip().splitlines():
        try:
            qty, name = line.strip().split(" ", 1)
            deck[name] = int(qty)
        except ValueError:
            continue
    return deck


def _slug_key(prefix: str, name: str) -> str:
    """Generate a consistent, URL-safe key for a widget based on its name."""
    return f"{prefix}_{sha1(name.encode()).hexdigest()[:8]}"


def _clear_temporary_state():
    """Remove all temporary matchup state and rerun to reset the UI."""
    for key in list(st.session_state.keys()):
        if (
            key.startswith("tmp_")
            or key.startswith("tmp_qty_out")
            or key.startswith("tmp_qty_in")
            or key == "confirm_add"
        ):
            del st.session_state[key]
    st.rerun()


def render_matchup_entry():
    """Renders the section for entering matchup data, with robust quantity handling and clear/cancel support."""
    MAX_OPPONENT_NAME_LENGTH = 25

    # Only show if deck_data exists
    if not st.session_state.get("deck_data"):
        return

    st.header("Add Matchup Info")
    section_divider()

    # Ensure our temporary keys exist
    st.session_state.setdefault("tmp_opponent_name", "")
    st.session_state.setdefault("tmp_search_out", [])
    st.session_state.setdefault("tmp_search_in", [])
    st.session_state.setdefault("confirm_add", False)

    # Opponent name input
    name = st.text_input(
        f"Opposing Archetype Name (max {MAX_OPPONENT_NAME_LENGTH} chars)",
        value=st.session_state.tmp_opponent_name,
        placeholder="e.g. Boros Energy",
        key="tmp_opponent_name",
    )

    # OUT cards
    st.html('<h2>Card(s) to take <span style="color:#f7b2ad;">OUT</span>:</h2>')
    search_out = st.multiselect(
        "Search:",
        options=list(st.session_state.deck_data["mainboard"].keys()),
        format_func=lambda k: st.session_state.card_labels.get(k, k),
        key="tmp_search_out",
    )
    # Render quantity inputs directly, keyed by slug
    for card in search_out:
        key_out = _slug_key("tmp_qty_out", card)
        st.number_input(
            f"Quantity to take out: {st.session_state.card_labels.get(card, card)}",
            min_value=1,
            max_value=st.session_state.deck_data["mainboard"][card],
            key=key_out,
        )

    # IN cards
    st.html('<h2>Card(s) to bring <span style="color:#9abca7;">IN</span>:</h2>')
    search_in = st.multiselect(
        "Search:",
        options=list(st.session_state.deck_data["sideboard"].keys()),
        format_func=lambda k: st.session_state.card_labels.get(k, k),
        key="tmp_search_in",
    )
    for card in search_in:
        key_in = _slug_key("tmp_qty_in", card)
        st.number_input(
            f"Quantity to bring in: {st.session_state.card_labels.get(card, card)}",
            min_value=1,
            max_value=st.session_state.deck_data["sideboard"][card],
            key=key_in,
        )

    # Compute totals from widget keys
    total_out = sum(
        st.session_state.get(_slug_key("tmp_qty_out", c), 0) for c in search_out
    )
    total_in = sum(
        st.session_state.get(_slug_key("tmp_qty_in", c), 0) for c in search_in
    )

    # Validation flags
    valid_name = bool(name.strip()) and len(name) <= MAX_OPPONENT_NAME_LENGTH
    valid_cards = total_out > 0 or total_in > 0
    can_submit = valid_name and valid_cards

    # Inline validation messages
    if name and not name.strip():
        st.error("Name cannot be empty.")
    if len(name) > MAX_OPPONENT_NAME_LENGTH:
        st.error(f"Archetype name exceeds {MAX_OPPONENT_NAME_LENGTH} characters.")
    if valid_name and not valid_cards:
        st.info("Select at least one card to remove or add.")

    # Add Matchup button
    if st.button("Add Matchup", disabled=not can_submit, key="add_matchup"):
        st.session_state.confirm_add = True

    # Confirmation step: warn and give Confirm/Cancel
    if st.session_state.confirm_add:
        if total_out != total_in:
            st.warning(
                f"Warning: removing {total_out} card"
                f"{'s' if total_out != 1 else ''} but adding {total_in} card"
                f"{'s' if total_in != 1 else ''}. This will change deck size."
            )
        custom_info("Click Confirm to finalize or Cancel to undo.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm", key="confirm_matchup"):
                # Build the matchup row from current widget state
                used = set(search_out) | set(search_in)
                row = {c: "" for c in used}
                for c in search_out:
                    qty = st.session_state.get(_slug_key("tmp_qty_out", c), 0)
                    row[c] = f"-{qty}"
                for c in search_in:
                    qty = st.session_state.get(_slug_key("tmp_qty_in", c), 0)
                    row[c] = f"+{qty}"
                row["Matchup"] = name

                st.session_state.matchups.append(row)
                st.success(f"Matchup '{name}' added!")

                # Clear all temporary state
                _clear_temporary_state()

        with col2:
            # Cancel clears temporary state via callback
            st.button(
                "Cancel",
                key="cancel_matchup",
                on_click=_clear_temporary_state,
            )
        # ───────────────────────────────────────────────────────────────────────


def render_matrix_section():  # Renders the download options
    if not st.session_state.matchups:
        return
    st.header("Sideboard Matrix Preview")
    section_divider()
    st.markdown(
        """
        This section displays a sorted preview of your added matchups.
        Click **Export Options** once you are finished to save your sideboard guide and/or export it to a printable file.
        """
    )
    df = pd.DataFrame(st.session_state.matchups).set_index("Matchup")
    mb = sorted(st.session_state.deck_data.get("mainboard", {}).keys())
    sb = sorted(st.session_state.deck_data.get("sideboard", {}).keys())
    cols = [c for c in mb if c in df.columns] + [c for c in sb if c in df.columns]
    df = df[cols][::-1]
    df = df.loc[:, (df != "").any(axis=0)]
    st.dataframe(df)

    if st.button("Export Options"):
        st.markdown("Select which format you would like to download.")

        st.warning(
            "‼️ If you would like to edit your sideboard guide at a later date, it is recommended to download a :primary[JSON file] as Sideboarder does not store any user data server-side."
        )

        # st.markdown("Select which format you would like to download.") :red[If you would like to edit your sideboard guide at a later date, it is recommended to download a JSON file as Sideboarder does not store any user data server-side.]")
        # PNG Render
        fig = render_matrix_figure(df, st.session_state.card_labels)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300)
        buf.seek(0)
        # PDF Render
        card = Image.open(buf)
        dpi = 300
        page_w, page_h = int(8.27 * dpi), int(11.69 * dpi)
        page = Image.new("RGB", (page_w, page_h), "white")
        x = (page_w - card.width) // 2
        y = (page_h - card.height) // 2
        page.paste(card, (x, y))
        buf_pdf = io.BytesIO()
        page.save(buf_pdf, "PDF", resolution=dpi)
        buf_pdf.seek(0)
        # JSON Render
        records = df.reset_index().to_dict(
            orient="records"
        )  # serialize to list of records
        json_str = json.dumps(records, indent=2)
        matrix_records = df.reset_index().to_dict(orient="records")
        payload = {
            "deck_data": st.session_state.deck_data,
            "matrix": matrix_records
        }
        json_str = json.dumps(payload, indent=2)
        col1, col2, col3 = st.columns(3)
        with col1:
            # JSON Download
            st.download_button(
                label="Save as JSON",
                data=json_str,
                file_name=f"sideboarder_{date.today()}.json",
                mime="application/json",
                use_container_width=True,
                icon=":material/save:",
                type="primary",
            )
        with col2:
            # PNG Download
            st.download_button(
                "Download as PNG",
                data=buf,
                file_name=f"sideboarder_{date.today()}.png",
                mime="image/png",
                use_container_width=True,
                icon=":material/image:",
                type="secondary",
            )
        with col3:
            st.download_button(
                label="Print-ready PDF",
                data=buf_pdf,
                file_name=f"sideboarder_{date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True,
                icon=":material/insert_drive_file:",
                type="secondary",
            )
            # now we can close the figure
            plt.close(fig)


@st.cache_data(show_spinner=False)
def render_matrix_figure(
    df: pd.DataFrame, card_labels: dict[str, str]
) -> plt.Figure:  # Renders the image that gets exported
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
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)
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


def render_sidebar():  # Renders the sidebar text and options
    """Render sidebar links, badges, and bug-report expander."""
    st.sidebar.page_link("splash.py", label="Back to the main page", icon=":material/home:")

    st.sidebar.page_link("pages/create.py", label="Create a new guide", icon=":material/open_in_new:")
    st.sidebar.page_link("pages/editor.py", label="Edit a saved guide", icon=":material/edit:")
    st.sidebar.markdown("---")
    st.sidebar.write(
        """
        Thanks for using **SideBoarder!**

        Follow these links to say hello, support development, or check out the changelogs:
        """
    )
    st.sidebar.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.sidebar.markdown(
        """
        <div style="display:flex;justify-content:space-between;width:100%;align-items:center;">
          <a href="https://sideboarder.bsky.social" target="_blank">
            <img src="https://img.shields.io/badge/Bluesky-0285FF?style=for-the-badge&logo=bluesky&logoColor=fff">
          </a>
          <a href="https://ko-fi.com/sideboarder" target="_blank">
            <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white">
          </a>
          <a href="https://github.com/NBrichta/mtg-sideboarder" target="_blank">
            <img src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white">
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    with st.sidebar.expander("👾&emsp;Submit a Bug Report"):
        bug = st.text_area("Describe the issue:", height=150)
        incl = st.checkbox("Include session state (deck + matchups)", value=True)
        if st.button("Submit Report"):
            submit_bug_report(bug, incl)



def submit_bug_report(
    bug_text, include_session
):  # Tells the app where to send bug reports
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


def render_hard_reset_button():  # Renders the session reset button
    st.sidebar.markdown("")

    if not st.session_state.get("confirm_reset", False):
        if st.sidebar.button(
            "❌&emsp;:red[Reset Session Data]", key="reset_confirm_button"
        ):
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
