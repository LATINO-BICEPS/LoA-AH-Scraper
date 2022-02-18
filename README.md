# What is this?
It's a script designed for the Lost Ark (NA/EU) release that monitors the in-game auction house to automatically transcribe the item names and return its corresponding prices. 

I consider myself a data-driven person who thrives on efficiency. Making spreadsheets on various aspects of games such as ability damage modifier % for the best DPS cycle, optimal routes to complete weeklies and dailies to save time, tracking in-game currency exchange rates to get the best bang for the buck.. you get the idea. 

Thus, birthed the idea of an auction house scraper for viewing item price history. I was not too satisfied with the limited options the in-game AH offers for this idea _for obvious reasons_. As such, I decided to make my own sloppy implementation of an AH API.

## Uses
* Track the trend of an item to make a more informed decision on AH
* Create charts/graphs of multiple items to create meaningful data ()

# How does it work?
It takes screenshots* of multiple areas of interests (e.g. Engraving Recipes, Enhancement Materials etc..) and extracts only the relevant information to return a dictionary of lists corresponding to the `Avg. Day Price`, `Recent Price` and `Lowest Price`. 

*WIP: currently it only grabs information from a single screenshot - not multiple.

## Example snippet
<p align="center">
<img width=800 src="https://i.imgur.com/fquXVdY.png">
</p>

## Returns relevant information 
In format `dataDict[itemName] = {[Avg. Day Price, Recent Prices, Lowest Price], ...}`.
<p align="center">
<img width=600 src="https://i.imgur.com/qLK11tl.png?1">
</p>






