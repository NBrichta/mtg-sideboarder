# Magic: The Gathering Sideboarder
A lightweight web app for designing and exporting Magic: The Gathering sideboard guides.
Built using Python 3.1 and Streamlit.

## What this app does
This app allows you to quickly design a printable sideboard for use in competitive MTG tournaments. [Section 2.11](https://blogs.magicjudges.org/rules/mtr2-11/) in the MTR states that the consultation of 'brief' notes in-between games is permitted, and so having a compact pre-planned list of cards to take out/put in in certain matchups can be useful to save time if you are expecting an assortment of different strategies. 

The app works through a simple form-based interface which prompts you to paste in your mainboard and sideboard. The list of cards is then carried through to the Matchup section, where you are then prompted to name your opposing deck, and dictate which cards to take out of your mainboard and bring in from your sideboard. This is then appended to a dataframe which stores this information as a simple matrix. Once you are finished adding matchups, you can then export this table as a PNG for printing purposes.

## Planned Features
- Paste a hyperlink to a decklist for automatic importing (MTGGoldfish, Moxfield, etc.)
- Edit or delete matchups after compiling
- Colored vs. printer-friendly export options
- Different aesthetic choices for export image
- Integrate autocomplete cardnames from [MTGJSON](https://mtgjson.com)
- Save user profiles (login through Google?)
- Download in printer-ready autoscaled PDF or SVG format
