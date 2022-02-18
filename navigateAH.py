import pyautogui
from pyautogui import click
from time import sleep
import datetime
import scrape
import os

cSpeed = 0.2
pyautogui.FAILSAFE = True # move cursor to upper left to abort

def resetCursor(seconds=3):
  """ return to original mouse position before running the script """
  sleep(seconds)
  x, y = pyautogui.position()
  pyautogui.moveTo(x,y,0)
  return
  
def openCloseAH():
  pyautogui.moveTo(1200,570,cSpeed)
  click()
  pyautogui.hotkey("altleft", "y")

def selectTier(tier=1):
  boxBelow = 40
  pyautogui.moveTo(913,422,cSpeed)
  click()
  if(tier == 1):
    pyautogui.moveRel(0,boxBelow*1.5,cSpeed)
    click()
  elif(tier == 2):
    pyautogui.moveRel(0,boxBelow*2,cSpeed)
    click()
  elif(tier == 3):
    pyautogui.moveRel(0,boxBelow*3,cSpeed)
    click()

def selectRarity(rarity):
  """ green for uncommon
  blue for rare
  purple for epic  """
  boxBelow = 40
  pyautogui.moveTo(1100,422,cSpeed)
  click()
  if(rarity == "green" or rarity == "uncommon"):
    pyautogui.moveRel(0,boxBelow*2,cSpeed)
    click()
    search()
  elif(rarity == "blue" or rarity == "rare"):
    pyautogui.moveRel(0,boxBelow*3,cSpeed)
    click()
    search()
  elif(rarity == "purple" or rarity == "epic"):
    pyautogui.moveRel(0,boxBelow*4,cSpeed)
    click()
    search()

def search():
  pyautogui.moveTo(1920,420,cSpeed)
  click()
  sleep(1)

def screenshot(desc, type, page):
  """ saves file in ./img directory in `YYYY-MM-DD_HH-MM-SS_description` format
  also returns a string of the file path"""
  # make folder if doesn't exist
  path = "./img/{0}".format(type)
  isExist = os.path.exists(path)
  if not isExist:
    os.makedirs(path)
    print('Directory Created.')

  timestamp = str(datetime.datetime.now())[:-7].replace(":",'-').replace(" ",'_')
  filename = timestamp + '_{0}{1}'.format(desc, str(page))
  screen = pyautogui.screenshot()
  # More accurate than JPG but almost 10x file size
  screen.save("./img/{0}/{1}.png".format(type, filename))
  return "./img/{0}/{1}.png".format(type, filename)
  # # save in JPG but massively reduces accuracy
  # screen.save("./img/{0}/{1}.jpg".format(type, filename))
  # return "./img/{0}/{1}.jpg".format(type, filename)

def screenshotAllPages(description, type):
  """ takes screenshots of all available pages on a particular menu """
  # take screenshot of the first page and return the file path 
  page1Dir = screenshot(description, type, 1)
  # get number of pages by cropping the page number and getting the digit
  page1Image = scrape.cv2.imread(page1Dir)
  allPagesImage = page1Image[1070:1090,1370:1420] # this captures all (1/22 for 22 total pages) 
  pagesImageProcessed = scrape.preprocessImage(allPagesImage)
  pages = scrape.imageToText(pagesImageProcessed) 
  page, pages = pages.split('/') # could go for a while loop if using the page variable
  page, pages = int(page), int(pages)
  print("There are totally {0} pages".format(pages))
  ## debug
  # scrape.cv2.imshow('pagesImage', pagesImage)
  # scrape.cv2.imshow('pagesImageProcessed', pagesImageProcessed)
  # scrape.cv2.waitKey(0) 
  for p in range(page,pages+1): # if there are 7 pages, it will click 6 times
    if(p == page):
      print("Page:", p)
      scrape.transcribeCatalog(page1Image)
    else:
      print("Page:", p)
      pagepImage = screenshot(description, type, p)
      pagepImage = scrape.cv2.imread(pagepImage)
      scrape.transcribeCatalog(pagepImage)
    if(p != pages): # this case is so it doesn't click one last time at the last page
      # clicks next page
      pyautogui.moveTo(1466,1080,cSpeed)
      click()
      sleep(0.5)

def getEngravingScreenshot(green=1, blue=0, purple=0):
  """ take multiple screenshots of engravings tab and save them in format
  [DD-MM-YYYY] XXXXXXX where XXXXX is the description of screenshot
  by default, it will only take screenshots of ALL green book pages """
  try:
    openCloseAH()
    # select engraving recipe
    pyautogui.moveTo(768,580,cSpeed)
    click()
    pyautogui.moveRel(0,40,cSpeed)
    click()
    sleep(0.5) # need delay while it loads

    # get all green books
    if(green == 1):
      selectRarity("green")
      description = "greenEngravings"
      type = 'Engravings'
      screenshotAllPages(description, type)

    # get all blue books
    if(blue == 1):
      selectRarity("blue")
      description = "blueEngravings"
      type = 'Engravings'
      screenshotAllPages(description, type)

    # get all purple books
    if(purple == 1):
      selectRarity("purple")
      description = "purpleEngravings"
      type = 'Engravings'
      screenshotAllPages(description, type)

    openCloseAH()
    resetCursor(1)

  except:
    openCloseAH()
    resetCursor(1) # remove when finished debugging


""" debugging """
# if __name__ == "__main__":
  

  # description = "purpleEngravings"
  # type = 'Engravings'
  # screenshotAllPages(description, type)