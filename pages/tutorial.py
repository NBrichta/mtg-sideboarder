import streamlit as st
import sideboarder_modular as sb_mod

st.set_page_config(
    page_title="Tutorial - SideBoarder",
    page_icon="./images/icon.ico",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "mailto:sideboarder.dev@gmail.com",
        "Report a bug": "https://github.com/NBrichta/mtg-sideboarder/issues",
        "About": "MTG Sideboarder is a passion project borne out of a frustration with clunky Excel spreadsheets and a love for Magic: The Gathering. I cannot express how thankful I am to everyone who has supported its development.",
    },
)

sb_mod.inject_css()
sb_mod.render_sidebar()
st.title("Getting Started with SideBoarder")
sb_mod.section_divider()
"Click on the tabs below to explore the various features of SideBoarder:"
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Guide Creation",
        "Export Formats",
        "Guide Editor",
        "Play/Draw",
        "Sample Data",
        "Contact",
    ]
)

with tab1:  # Guide creation
    st.header("Creating your first guide")
    st.markdown(
        """
    SideBoarder makes it easy to design complex sideboard guides in minutes.
    """
    )
    col1, col2, col3 = st.columns(3, border=True)
    with col1:
        st.header("Step 1.")
        st.subheader("Import decklist")
        sb_mod.section_divider()
        st.markdown(
            """
        From the main page or the sidebar, click the option with the :material/add_circle: icon to go to the deck importer.
        - Paste your 60-card mainboard and 15-card sideboard into the deck entry box.
            - Or, import from MTGGoldfish using a deck URL.
        - Click `Submit Deck` (or `Import from MTGGoldfish`) to lock it in.
        """
        )

    with col2:
        st.header("Step 2.")
        st.subheader("Add your matchups")
        sb_mod.section_divider()
        st.markdown(
            """
        - Give your matchup a name (e.g. Mono-Red Aggro).
        - Choose cards to take out of your mainboard.
        - Choose cards to bring in from your sideboard.
        - Click `Add Matchup`, then `Confirm` to save it.
        
        Add as many matchups as you like, and SideBoarder will tabulate them in a preview underneath.
        """
        )

    with col3:
        st.header("Step 3.")
        st.subheader("Export your guide")
        sb_mod.section_divider()
        st.markdown(
            """
        - Once you are satisfied with the matchups added, click `Export Options`
        - You will be prompted to save to a `JSON`, `PNG`, or `PDF`
        
        :red[Important:] It is recommended that you save your sideboard guide to a JSON **before** exporting to a PNG/PDF. See the Export Formats tab for more details.
        """
        )

with tab2:  # Export Formats
    st.header("Exporting your guide")
    st.markdown("""
    SideBoarder (currently) allows for explicit export in 3 formats (`JSON`, `PNG`, & `PDF`). You can also export to `CSV` directly from the preview matrix if you would prefer to use your own formatting for a sideboard guide.
    """)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("JSON")
        sb_mod.section_divider()
        st.markdown("""
        The `JSON` format stores all decklist and matchup data in your sideboard guide. It's basically just a text file with some code-friendly formatting to make extracting the data faster for editing guides in the future. It is recommended that you save your sideboard guide to a JSON file each time you create one, just in case you decide to edit it again in the future.

        At some point in the future, being able to save guides to a Google account (or storing them as am encrypted key) might be a better strategy. However, in the interest of making SideBoarder functional at minimum, exporting to JSON is easiest implementation I could think of. An added benefit is it makes it pretty easy to share with others, so there are advantages to this approach.
        """
        )

    with col2:
        st.subheader("PNG")
        sb_mod.section_divider()
        "The `PNG` format exports as a table at 300dpi. This makes it suitable for uploading to social media platforms, as well as copy/pasting into blank documents for printing at any size. An example of the exported sideboard guide using the sample_data.json file is shown here:"
        st.image("./images/readme/sideboard_demo.png", use_container_width=True)

    with col3:
        st.subheader("PDF")
        sb_mod.section_divider()
        "The `PDF` export option allows you to export your sideboard guide into a pretemplated, card-sized cutout ready for printing. Note that the image below is shrunk significantly to contain it on the page, and the true size is roughly 2.5 x 3.5in, roughly the size of a Magic card."
        st.image("./images/readme/pdf_demo.png", use_container_width=True)



with tab3:  # Guide Editor
    st.header("Editing your guide")
    st.markdown("This section is unfinished, but will explain the process for editing your sideboard guide from a .JSON file.")
    # col1, col2, col3 = st.columns(3, border=True)
    # with col1:
    #     st.header("Step 1.")
    #     st.subheader("Import decklist")
    #     sb_mod.section_divider()
    #     st.markdown(
    #         """
    #     From the main page or the sidebar, click the option with the :material/add_circle: icon to go to the deck importer.
    #     - Paste your 60-card mainboard and 15-card sideboard into the deck entry box.
    #         - Or, import from MTGGoldfish using a deck URL.
    #     - Click `Submit Deck` (or `Import from MTGGoldfish`) to lock it in.
    #     """
    #     )

    # with col2:
    #     st.header("Step 2.")
    #     st.subheader("Add your matchups")
    #     sb_mod.section_divider()
    #     st.markdown(
    #         """
    #     - Give your matchup a name (e.g. Mono-Red Aggro).
    #     - Choose cards to take out of your mainboard.
    #     - Choose cards to bring in from your sideboard.
    #     - Click `Add Matchup`, then `Confirm` to save it.
        
    #     Add as many matchups as you like, and SideBoarder will tabulate them in a preview underneath.
    #     """
    #     )

    # with col3:
    #     st.header("Step 3.")
    #     st.subheader("Export your guide")
    #     sb_mod.section_divider()
    #     st.markdown(
    #         """
    #     - Once you are satisfied with the matchups added, click `Export Options`
    #     - You will be prompted to save to a `JSON`, `PNG`, or `PDF`
        
    #     :red[Important:] It is recommended that you save your sideboard guide to a JSON **before** exporting to a PNG/PDF. See the Export Formats tab for more details.
    #     """
    #     )

with tab4:  # Play/Draw
    st.header("On the play vs. on the draw")
    st.markdown(
        "For now, SideBoarder doesn't have explicit support for defining matchups on the play versus on the draw. This is a heavily requested feature, as your play patterns against certain decks may depend on who goes first. While we work on implementing this, the quick fix is to treat either scenario as a new matchup (e.g. Matchup 1: Boros Energy (OTP), Matchup 2: Boros Energy (OTD)). The export templates can handle many matchup rows without throwing out the automatic formatting, so it shouldn't affect the readability of the guide too drastically."
    )

with tab5:  # Sample Data
    st.header("Sample guide data")
    st.markdown(
        "Click the button below to download a .JSON file containing a sample decklist and matchup info. You can use this to test various features of the app."
    )
    sb_mod.download_sample_json()


with tab6:  # Help
    st.header("Bugs and feedback")
    st.markdown(
        "Although I have tried my best to keep SideBoarder bug-free, it is inevitable that things stop working properly at some point. There are multiple options for reporting any issues you may encounter:"
    )
    col1, col2, col3 = st.columns(3, border=True)
    with col1:
        st.header("Bug Reporting")
        sb_mod.section_divider()
        st.markdown(
            """
        The sidebar contains a bug report form that you can fill out and submit anonymously. You can also elect to send your session data (your decklist and currently saved matchups) which helps when trying to recreate the issue.

        When you click `Submit`, a form response is generated through Google Forms, which ends up in my Gmail inbox. I try to respond to these promptly, but please allow me some time to work on the issue.
        """
        )

    with col2:
        st.header("GitHub Issues")
        sb_mod.section_divider()
        st.markdown(
            """
        Sometimes a bug in the app's code will prevent the sidebar from rendering. SideBoarder is connected to my [GitHub repo](https://github.com/NBrichta/mtg-sideboarder), where the Issues tab has a pinned thread for bugs. I use this to track any ongoing issues with the app and update users on their fix status. 
        
        If you encounter a bug that cannot be reported in the conventional way, please post a comment in that thread alongside the actions you suspect might have caused it (screenshots help too!)
        """
        )

    with col3:
        st.header("Contact Me")
        sb_mod.section_divider()
        st.markdown(
            """
        If you have any questions, comments, feature requests, or just want to say hello, you can contact me directly:
        
        ![https://sideboarder.bsky.social](https://img.shields.io/badge/@sideboarder-0285FF?style=for-the-badge&logo=Bluesky&logoColor=white)

        ![https://x.com/SideBoarder](https://img.shields.io/badge/@sideboarder-%23000000.svg?style=for-the-badge&logo=X&logoColor=white)

        ![mailto:sideboard.dev@gmail.com](https://img.shields.io/badge/sideboarder.dev@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)

        Of course, you can support this project at the following link:

        ![https://ko-fi.com/sideboarder](https://img.shields.io/badge/sideboarder-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)

        """
        )
