# Magic: The Gathering Sideboarder
A lightweight web app for designing and exporting Magic: The Gathering sideboard guides.
Built using Python 3.1 and Streamlit.

### What this app does
This app allows you to quickly design a printable sideboard for use in competitive MTG tournaments. [Section 2.11](https://blogs.magicjudges.org/rules/mtr2-11/) in the MTR states that the consultation of 'brief' notes in-between games is permitted, and so having a compact pre-planned list of cards to take out/bring in for certain matchups can be useful to save time if you are expecting an assortment of different strategies. 

The app works through a simple form-based interface which should be fairly intuitive to use, and can produce easy to read sideboard guides in a variety of formats.

### What this app won't do
This app does not (*and will not*) magically improve your match win percentage in a competitive setting. Sideboarding is rarely straightforward, and often depends entirely on your assessment of the metagame going into a tournament. This tool is for people who are fed-up with using clunky Excel spreadsheets, or lack the prerequisite knowledge to code/design their own sideboarding guide template.

## How do I use it?
1. Paste in your decklist in MTGO format (e.g. 4 Lightning Bolt) into their respective mainboard and sideboard sections and submit.
2. Add your matchup information, which includes the opposing deck archetype, and which cards to take out/bring in from the MB and SB respectively. Once finished, adding the matchup will spawn a preview matrix of the data entered so far.
3. Once all matchups have been added, clicking the Download Options button will enable you to save the matrix in a templated table in PNG format, ready for printing.

## Planned Features (in rough priority list)
- Edit or delete matchups after adding
- Paste a hyperlink to a decklist for automatic importing (MTGGoldfish, Moxfield, etc.)
- Download sideboard guide in printer-ready autoscaled PDF or SVG format (divider size, A4 size, etc.)
- Alert the user if their maindeck total will be under 60 cards post-sideboard 
- Bug reporting button
- Colored vs. printer-friendly export options
- Different thematic choices for export image
- Integrate autocomplete cardnames from [MTGJSON](https://mtgjson.com) (is this even necessary?)
    - Possible use case: Displaying deck stats (number of cards, avg. CMC, etc. after submitting decklist)
- Save user profiles (login through Google?)