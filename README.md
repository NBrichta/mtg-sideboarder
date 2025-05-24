# SideBoarder
A lightweight web app for designing and exporting Magic: The Gathering sideboard guides.
Built using Python 3.1 and Streamlit 1.45.0.

### What this app does
This app allows you to quickly design a printable, deckbox divider-sized sideboard guide for use in competitive MTG tournaments. [Section 2.11](https://blogs.magicjudges.org/rules/mtr2-11/) in the MTR states that the consultation of 'brief' notes in-between games is permitted, and so having a compact pre-planned list of cards to take out/bring in for certain matchups can be useful to save time if you are expecting an assortment of different strategies. 

The app works through a simple form-based interface which should be fairly intuitive to use, and can produce easy to read sideboard guides in a variety of formats.

### What this app won't do
This app does not (**and will not**) magically improve your match win percentage in a competitive setting. Sideboarding is rarely straightforward, and often depends entirely on your assessment of the metagame going into a tournament. This tool is for people who are fed-up with using clunky Excel spreadsheets, or lack the prerequisite knowledge to code/design their own sideboarding guide template.

## How do I use it?
1. On the main page, choose whether you want to generate a new guide, or edit a saved one.

2. Paste your decklist into their respective mainboard and sideboard sections and submit.

3. Add your matchup information, which includes the opposing deck archetype, and which cards to take out/bring in from the MB and SB respectively. Once finished, adding the matchup will spawn a preview matrix of the data entered so far.

4. Once all matchups have been added, clicking the Download Options button will enable you to save the matrix in a variety of formats and sizes, ready for printing.

## What formats can I save in?
As of `v1.0.0`, MTG Sideboarder lets you **explicitly** save in 3 formats (JSON, PNG, PDF), and implicitly allows you to download a CSV file of your matchup matrix:
- The JSON file is used for saving decklists/matchups and editing them later. 
- The PNG image can be copy/pasted into online formats or scaled to a desired print size.
- The PDF exports as a ready-to-print document, with cut lines to ensure you can fit it in an outer sleeve if you prefer.
- The CSV file is available through the download button on the matrix itself, in case you prefer using your own template in Excel or otherwise.

## Example Guide
The JSON file `./images/readme/blast_cutter.json` is a sample decklist and matchup info file that was used to create the following sideboard guide:

![blast cutter sb guide](https://github.com/NBrichta/mtg-sideboarder/blob/release/v1.0.0/images/readme/sideboard_demo.png)

Using the PDF export feature, we can automatically scale this down to card size:

![pdf](https://github.com/NBrichta/mtg-sideboarder/blob/release/v1.0.0/images/readme/pdf_demo.png)

## Planned Features (in rough priority list)
- Edit or delete matchups after adding
    - Users should be able to customise the order they are displayed to their liking
- Paste a hyperlink to a decklist for automatic importing: 
    - MTGGoldfish <- `supported as of v1.0.0`
    - Moxfield
    - CubeCobra
    - Scryfall
    - TappedOut
    - Archidekt

- Implement some form of smart abbreviation for commonly used words or phrases 
- Colored vs. printer-friendly export options
- Different thematic choices for export image
- Differentiating on-the-play vs. on-the-draw (how would this even work?)
