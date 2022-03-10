# What is this?
This is a script designed for the Lost Ark (NA/EU) release that monitors the in-game market to automatically transcribe the item names and return its corresponding prices. 

I consider myself a data-driven person who thrives on efficiency. Making spreadsheets on various aspects of games such as ability damage modifier % for the best DPS cycle, optimal routes to complete weeklies and dailies to save time, tracking in-game currency exchange rates to get the best bang for the buck.. you get the idea. 

Thus, birthed the idea of an auction house scraper for viewing item price history. I was not too satisfied with the limited options the in-game market offers for this idea _for obvious reasons_. As such, I decided to make my own sloppy implementation of market API.

# Usage
<p align="center"><img width=900 src="https://i.imgur.com/y5VhwsN.gif"></p>

1. Load into Lost Ark without any menus open
2. Modify function in `main.py` as needed
3. Run `main.py` 
4. Let it process the images for a few minutes
5. Log data to InfluxDB and manipulate data from there.

Some ideas include tracking the trend of an item to make a more informed decision on the market and/or create charts/graphs of multiple items to create meaningful data. Scraping other region's market for how much things are supposed to cost is another idea.

# Features
* `getGoldToCrystalsRate()` returns the going rate of 1 blue crystal to gold
* `getEngravingData()` returns `{'itemName': [avgPrice, recentPrice, lowestPrice], ...}`
* Shortest path from A -> B *WIP



# How does it work?
It takes screenshots of multiple areas of interests (e.g. Engraving Recipes, Enhancement Materials etc..) and extracts only the relevant information to return a dictionary of lists corresponding to the `Avg. Day Price`, `Recent Price` and `Lowest Price`. 

# Requirements
* openCV-Python
* pyautogui
* pytesseract
* influxdb-client

Ensure `tesseract.exe` is in `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`. Binaries are found [here](https://tesseract-ocr.github.io/tessdoc/Home.html#binaries).

# Limitations
## Optimized for 1440p, forced 21:9 AND 100% Hud Scaling ONLY
* All values are hardcoded to 1440p due to how it scrapes the data. Other resolutions could be supported by scaling it linearly but untested.