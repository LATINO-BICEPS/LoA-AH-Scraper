import pyautogui
from pyautogui import click
from time import sleep
import datetime
import scrape

cSpeed = 0.2
pyautogui.FAILSAFE = True # move cursor to upper left to abort

def resetCursor(seconds=3):
  """ this is for my personal purposes remove for release
  resets back to play button after 4 seconds """
  sleep(seconds)
  pyautogui.moveTo(3887,98,0)
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

def screenshot(desc="debugDesc", type="debugType", page='unknown'):
  """ saves file in ./img directory in `YYYY-MM-DD_HH-MM-SS_description` format"""
  timestamp = str(datetime.datetime.now())[:-7].replace(":",'-').replace(" ",'_')
  filename = timestamp + '_{0}{1}'.format(desc, page)
  screen = pyautogui.screenshot()
  screen.save("./img/{0}/{1}.png".format(type, filename))

def nextPage():
  """ try to make this function loop through all pages """
  pyautogui.moveTo(1466,1080,cSpeed)
  click()

def getEngravingScreenshot(green=1, blue=0, purple=0):
  """ take multiple screenshots of engravings tab and save them in format
  [DD-MM-YYYY] XXXXXXX where XXXXX is the description of screenshot
  by default, it will only take screenshots of ALL green book pages """
  type = 'Engravings'
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

    # get number of pages
    scrape.cv2.imread
    # loop through all pages
    pages = int()
    for page in range(pages-1): # if there are 7 pages, it will click 6 times
      screenshot(description, type, page)

  # get all blue books
    if(blue == 1):
      pass
  # get all purple books
    if(purple == 1):
      pass

  openCloseAH()


  resetCursor(1) # remove when finished debugging


""" debugging """
if __name__ == "__main__":
  getEngravingScreenshot()
  