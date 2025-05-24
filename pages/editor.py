import streamlit as st
import json
import pandas as pd
from datetime import date
from PIL import Image
import io
import math
import sideboarder_modular as sb_mod

# Page setup
st.set_page_config(page_title="Edit - SideBoarder", layout="centered", page_icon="./images/icon.ico")
sb_mod.inject_css()
sb_mod.render_sidebar()
st.title("SideBoarder Editor")
st.markdown(
    """
    Edit your sideboard guide by following the steps below:
    """
)
st.header("Upload Data")
sb_mod.section_divider()

# Upload JSON (only load into session_state once)
uploaded = st.file_uploader("Upload your Sideboarder JSON file", type="json")
if uploaded and "deck_data" not in st.session_state:
    try:
        data = json.load(uploaded)
        st.success("✅ File loaded successfully.")
        st.session_state.deck_data   = data["deck_data"]
        st.session_state.matchups    = data["matrix"]
        st.session_state.card_labels = {
            key: key[3:]
            for zone in data["deck_data"].values()
            for key in zone
        }
    except Exception as e:
        st.error(f"❌ Failed to parse JSON: {e}")

# Confirmation state defaults
st.session_state.setdefault("confirm_action", None)
st.session_state.setdefault("pending_changes", None)
st.session_state.setdefault("pending_deletion", None)

# Edit matchups with tabs
if st.session_state.get("matchups"):
    st.header("Edit Matchups")
    sb_mod.section_divider()

    mb_keys = st.session_state.deck_data["mainboard"].keys()
    sb_keys = st.session_state.deck_data["sideboard"].keys()
    tabs = st.tabs([m["Matchup"] for m in st.session_state.matchups])

    for idx, tab in enumerate(tabs):
        with tab:
            # Choose whether to show the original or the pending-changes version
            if st.session_state.confirm_action == f"save_{idx}" and st.session_state.pending_changes:
                matchup = st.session_state.pending_changes
            else:
                matchup = st.session_state.matchups[idx]

            # Matchup name input
            name_key = f"edit_name_{idx}"
            st.text_input("Matchup Name", value=matchup["Matchup"], key=name_key)

            # Parse existing in/out values
            mb_out = {
                k: int(str(matchup[k]).lstrip("-"))
                for k in mb_keys
                if k in matchup and isinstance(matchup[k], str) and matchup[k].startswith("-")
            }
            sb_in = {
                k: int(str(matchup[k]).lstrip("+"))
                for k in sb_keys
                if k in matchup and isinstance(matchup[k], str) and matchup[k].startswith("+")
            }

            # Build a new row dict from user inputs
            updated_name = st.session_state.get(name_key, matchup["Matchup"])
            new_row = {"Matchup": updated_name}
            total_out = total_in = 0

            left_col, right_col = st.columns(2)

            # Mainboard adjustments
            with left_col:
                st.markdown("**<span style='color:#f7b2ad;'>Mainboard:</span>**", unsafe_allow_html=True)
                for card in mb_keys:
                    if card in mb_out:
                        key = f"edit_out_{idx}_{card}"
                        qty = st.number_input(
                            st.session_state.card_labels[card],
                            min_value=0,
                            max_value=st.session_state.deck_data["mainboard"][card],
                            value=mb_out[card],
                            key=key,
                        )
                        if qty:
                            new_row[card] = f"-{qty}"
                            total_out += qty
                with st.expander("Show other mainboard cards:"):
                    for card in mb_keys:
                        if card not in mb_out:
                            key = f"edit_out_{idx}_{card}"
                            qty = st.number_input(
                                st.session_state.card_labels[card],
                                min_value=0,
                                max_value=st.session_state.deck_data["mainboard"][card],
                                value=0,
                                key=key,
                            )
                            if qty:
                                new_row[card] = f"-{qty}"
                                total_out += qty

            # Sideboard adjustments
            with right_col:
                st.markdown("**<span style='color:#9abca7;'>Sideboard:</span>**", unsafe_allow_html=True)
                for card in sb_keys:
                    if card in sb_in:
                        key = f"edit_in_{idx}_{card}"
                        qty = st.number_input(
                            st.session_state.card_labels[card],
                            min_value=0,
                            max_value=st.session_state.deck_data["sideboard"][card],
                            value=sb_in[card],
                            key=key,
                        )
                        if qty:
                            new_row[card] = f"+{qty}"
                            total_in += qty
                with st.expander("Show other sideboard cards:"):
                    for card in sb_keys:
                        if card not in sb_in:
                            key = f"edit_in_{idx}_{card}"
                            qty = st.number_input(
                                st.session_state.card_labels[card],
                                min_value=0,
                                max_value=st.session_state.deck_data["sideboard"][card],
                                value=0,
                                key=key,
                            )
                            if qty:
                                new_row[card] = f"+{qty}"
                                total_in += qty

            # Totals and mismatch warning
            st.markdown(f"**Total OUT:** :red[{total_out}]   **Total IN:** :green[{total_in}]")
            if total_out != total_in:
                st.warning("⚠️ Number of cards being taken OUT does not match number being brought IN.")

            # Action buttons / confirm dialogs
            confirm = st.session_state.confirm_action
            col1, col2 = st.columns(2)

            # — Save path —
            with col1:
                if confirm == f"save_{idx}":
                    # Show changelog & confirm/cancel
                    original = st.session_state.matchups[idx]
                    changes = []
                    # Name change?
                    if new_row["Matchup"] != original["Matchup"]:
                        changes.append(f"🆕 Renamed '{original['Matchup']}' to '{new_row['Matchup']}'")
                    # Card diffs
                    all_cards = set(original.keys()).union(new_row.keys()) - {"Matchup"}
                    for card in sorted(all_cards):
                        o = original.get(card, "")
                        n = new_row.get(card, "")
                        if isinstance(o, float) and math.isnan(o): o = ""
                        if o != n:
                            old_n = int(o.lstrip("+-")) if o else 0
                            new_n = int(n.lstrip("+-")) if n else 0
                            delta = new_n - old_n
                            if delta:
                                sign = "+" if delta > 0 else "-"
                                label = st.session_state.card_labels.get(card, card)
                                changes.append(f"{sign}{abs(delta)} {label}")
                    if changes:
                        st.markdown("### Changes to Apply:")
                        for c in changes:
                            st.markdown(f"- {c}")
                    sb_mod.custom_info("Confirm to apply these changes or cancel to continue editing.")
                    if st.button("✅ Confirm Save", key=f"confirm_save_{idx}"):
                        st.session_state.matchups[idx] = new_row
                        # cleanup inputs
                        for k in list(st.session_state.keys()):
                            if k.startswith(f"edit_out_{idx}_") or k.startswith(f"edit_in_{idx}_") or k.startswith(name_key):
                                del st.session_state[k]
                        st.session_state.confirm_action  = None
                        st.session_state.pending_changes = None
                        st.rerun()
                    if st.button("❌ Cancel", key=f"cancel_save_{idx}"):
                        st.session_state.confirm_action  = None
                        st.session_state.pending_changes = None
                        st.rerun()
                elif confirm == f"delete_{idx}":
                    # Hide Save during delete confirm
                    pass
                else:
                    if st.button(f"Save Changes to {matchup['Matchup']}", key=f"save_btn_{idx}"):
                        st.session_state.pending_changes = new_row
                        st.session_state.confirm_action  = f"save_{idx}"
                        st.rerun()

            # — Delete path —
            with col2:
                if confirm == f"delete_{idx}":
                    sb_mod.custom_info("Are you sure you want to delete this matchup?")
                    if st.button("✅ Confirm Delete", key=f"confirm_delete_{idx}"):
                        deleted = st.session_state.matchups.pop(idx)
                        # cleanup inputs
                        for k in list(st.session_state.keys()):
                            if k.startswith(f"edit_out_{idx}_") or k.startswith(f"edit_in_{idx}_") or k.startswith(name_key):
                                del st.session_state[k]
                        st.toast(f"Deleted matchup: {deleted['Matchup']}")
                        st.session_state.confirm_action   = None
                        st.session_state.pending_deletion = None
                        st.rerun()
                    if st.button("❌ Cancel", key=f"cancel_delete_{idx}"):
                        st.session_state.confirm_action   = None
                        st.session_state.pending_deletion = None
                        st.rerun()
                elif confirm == f"save_{idx}":
                    # Hide Delete during save confirm
                    pass
                else:
                    if st.button(f":red[Delete {matchup['Matchup']} Matchup]", key=f"delete_btn_{idx}"):
                        st.session_state.pending_deletion = idx
                        st.session_state.confirm_action   = f"delete_{idx}"
                        st.rerun()

# Export section
if st.session_state.get("matchups"):
    sb_mod.section_divider()
    st.subheader("Export Updated Sideboard Guide")
    df = pd.DataFrame(st.session_state.matchups).set_index("Matchup")
    mb_keys = sorted(st.session_state.deck_data["mainboard"].keys())
    sb_keys = sorted(st.session_state.deck_data["sideboard"].keys())
    columns = [c for c in mb_keys if c in df.columns] + [c for c in sb_keys if c in df.columns]
    df = df[columns].loc[:, (df != "").any(axis=0)]
    fig = sb_mod.render_matrix_figure(df, st.session_state.card_labels)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    buf.seek(0)
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

    payload = {
        "deck_data": st.session_state.deck_data,
        "matrix": df.reset_index().to_dict(orient="records")
    }
    json_str = json.dumps(payload, indent=2)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Save as JSON",
            data=json_str,
            file_name=f"sideboarder_{date.today()}.json",
            mime="application/json",
            use_container_width=True,
            icon=":material/save:",
            type="primary",
        )
    with col2:
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
            "Print-ready PDF",
            data=buf_pdf,
            file_name=f"sideboarder_{date.today()}.pdf",
            mime="application/pdf",
            use_container_width=True,
            icon=":material/insert_drive_file:",
            type="secondary"
        )
