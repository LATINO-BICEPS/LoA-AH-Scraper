import pyautogui
import datetime
import scrape
import os
from pyautogui import click
from time import sleep
from configuration import debugMode, screenshotPath, cSpeed
import shutil

pyautogui.FAILSAFE = True # move cursor to upper left to abort

def resetCursor(seconds=3):
  """ return to original mouse position before running the script """
  sleep(seconds)
  x, y = pyautogui.position()
  pyautogui.moveTo(x,y,0)
  return
  
def openCloseStore():
  pyautogui.moveTo(1200,570,cSpeed)
  click()
  pyautogui.press('F4')

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

def screenshot(desc, category, page):
  """ saves file in ./img directory in `YYYY-MM-DD_HH-MM-SS_descriptionPageNum` format
      also returns a string of the file path
      desc: if it is an epic engraving recipe, it is purpleEngraving """
  # make folders if doesn't exist
  pathIncomplete = "{0}/{1}/incomplete".format(screenshotPath, category)
  pathComplete = "{0}/{1}/complete".format(screenshotPath, category)
  isIncompleteExist = os.path.exists(pathIncomplete)
  isCompleteExist = os.path.exists(pathComplete)
  if not isIncompleteExist:
    os.makedirs(pathIncomplete)
    print('{0} Folder Created.'.format(pathIncomplete))
  if not isCompleteExist:
    os.makedirs(pathComplete)
    print('{0} Folder Created.'.format(isCompleteExist))

  timestamp = str(datetime.datetime.now())[:-7].replace(":",'-').replace(" ",'_')
  filename = timestamp + '_{0}{1}'.format(desc, str(page))
  screen = pyautogui.screenshot()

  # # save in JPG but massively reduces accuracy
  # screenshotImagePath = "{0}/{1}.jpg".format(path, filename)
  # screen.save(screenshotImagePath)
  # return screenshotImagePath

  # Save as PNG - more accurate than JPG but almost 10x file size
  screenshotImagePath = "{0}/{1}.png".format(pathIncomplete, filename)
  screen.save(screenshotImagePath)
  return screenshotImagePath
  
def batchProcessAllPages(description, category, batch=True):
  """ takes screenshots of all available pages on a particular menu first 
      then processes them afterwards
      if batch=False, process the image in realtime"""
  try:
    print('-----------------------')
    print('Saving {0} now'.format(description))
    print('-----------------------')
    itemDict = {} # stores all the data in this one particular instance
    # take screenshot of the first page and return the file path 
    page1Dir = screenshot(description, category, 1)
    # get number of pages by cropping the page number and getting the digit
    page1Image = scrape.cv2.imread(page1Dir)
    allPagesImage = page1Image[1070:1090,1370:1420] # this captures all (1/22 for 22 total pages) 
    pagesImageProcessed = scrape.preprocessImage(allPagesImage)
    pages = scrape.imageToText(pagesImageProcessed) 
    print("Total number of pages: {0}".format(pages))
    if(pages == ''): # if it accidentally closes the AH menu for some reason and captures the air, delete it immediately
      raise KeyboardInterrupt
    if(debugMode):
      scrape.cv2.imshow('Total Pages Only', pagesImageProcessed)
      scrape.cv2.waitKey(1000)
      scrape.cv2.destroyWindow('Total Pages Only')
    # (1/1) is occasionally detected as 111. realistically page numbers will never go above 100 so it is hardcoded
    if(pages == '111'):
      print('Detected wrong transcribe. Transcribed as 111; corrected to 1/1')
      pages = '1/1'
    page, pages = pages.split('/') 
    page, pages = int(page), int(pages)
    print("There are in total {0} page/s".format(pages))
    for p in range(page,pages+1): # if there are 7 pages, it will click 6 times
      if(p == page): 
        print("Scanning Page:", p)
        if(not batch): # since already took screenshot of first page, go straight to transcribing if batch=False
          scrape.transcribeCatalog(page1Image)
      else:
        print("Scanning Page:", p)
        pagepImage = screenshot(description, category, p)
        if(not batch):
          pagepImage = scrape.cv2.imread(pagepImage)
          scrape.transcribeCatalog(pagepImage)
      if(p != pages): # this case is so it doesn't click one last time at the last page
        # clicks next page
        pyautogui.moveTo(1466,1080,cSpeed)
        click()
        sleep(0.5)
      
    print('-----------------------')
    print('Processing Images Now')
    print('-----------------------')
    batchScreenshotIncompletePath = '{0}/{1}/incomplete'.format(screenshotPath, category)
    batchScreenshotCompletePath = '{0}/{1}/complete'.format(screenshotPath, category)
    print('Screenshot temp. directory: {0}'.format(batchScreenshotIncompletePath))
    
    # remove existing files in `batchScreenshotCompletePath`
    for existingImage in os.listdir(batchScreenshotCompletePath):
      os.remove('{0}/{1}'.format(batchScreenshotCompletePath, existingImage))

    for screenshotFileName in os.listdir(batchScreenshotIncompletePath):
      # get page number by reading the last 3 chars (remember YYYY-MM-DD_HH-MM-SS_descriptionPageNum format)
      screenshotImage = scrape.cv2.imread(os.path.join(batchScreenshotIncompletePath, screenshotFileName))
      screenshotPageNumber = screenshotFileName[-7:-4]
      digitList = [char for char in screenshotPageNumber if char.isdigit()]
      screenshotPageNumber = int(''.join(str(digit) for digit in digitList))
      print('Processing page:', screenshotPageNumber)
      dataDict = scrape.transcribeCatalog(screenshotImage, category)
      itemDict = dataDict | itemDict # combine all transcribed catalog into a single dict

      # move all files to completed DIR
      shutil.move('{0}/{1}'.format(batchScreenshotIncompletePath, screenshotFileName),
                '{0}/{1}'.format(batchScreenshotCompletePath, screenshotFileName))

  except KeyboardInterrupt:
    print('CANCELLED')
    # delete all files inside of temp folder on cancel
    batchScreenshotIncompletePath = '{0}/{1}/incomplete'.format(screenshotPath, category)
    print(batchScreenshotIncompletePath)
    for existingImage in os.listdir(batchScreenshotIncompletePath):
      os.remove('{0}/{1}'.format(batchScreenshotIncompletePath, existingImage))

  # Display final results 
  print('-------------------------------------------------------------------------------')
  print('Finished Batch Project. There are in total {0} records. Showing all saved items:'.format(len(itemDict)))
  print('-------------------------------------------------------------------------------')
  for item in itemDict:
    print(item, itemDict[item])
  print('-------------------------------------------------------------------------------')
  print('\n\n')
  return itemDict

def getEngravingData(green=1, blue=0, purple=0):
  """ take multiple screenshots of engravings tab and save them in format
      [DD-MM-YYYY] XXXXXXX where XXXXX is the description of screenshot by default, 
      it will only take screenshots of ALL green book pages """
  allEngravingData = {} # to be filled later
  try:
    openCloseAH()
    # select engraving recipe
    pyautogui.moveTo(768,580,cSpeed)
    click()
    pyautogui.moveRel(0,40,cSpeed)
    click()
    sleep(0.5) # need delay while it loads
    category = 'engravings'
    # get all green books
    if(green == 1):
      selectRarity("green")
      description = "greenEngravings"
      allEngravingData = allEngravingData | batchProcessAllPages(description, category)

    # get all blue books
    if(blue == 1):
      selectRarity("blue")
      description = "blueEngravings"
      allEngravingData = allEngravingData | batchProcessAllPages(description, category)

    # get all purple books
    if(purple == 1):
      selectRarity("purple")
      description = "purpleEngravings"
      allEngravingData = allEngravingData | batchProcessAllPages(description, category)
    print('returned Data: \n', allEngravingData)
    pyautogui.press('esc')
    return
  except:
    pyautogui.press('esc')
    return

def getGoldToCrystalsRate():
  """ returns a float of the rate from gold -> crystals """
  openCloseStore()
  sleep(0.5)
  pyautogui.moveTo(2266,1210,cSpeed)
  click()
  pyautogui.moveTo(1566,785,cSpeed)
  click()
  description = 'goldToCrystal'
  category = 'store'
  curExchangeImgPath = screenshot(description, category, '')

  print('-----------------------')
  print('Processing Images Now')
  print('-----------------------')
  curExchangeIncompletePath = '{0}/{1}/incomplete'.format(screenshotPath, category)
  curExchangeCompletePath = '{0}/{1}/complete'.format(screenshotPath, category)
  print('Screenshot temp. directory: {0}'.format(curExchangeIncompletePath))
  print('Reading {0} now'.format(curExchangeImgPath))
  curExchange = scrape.cv2.imread(curExchangeImgPath)[950:1000, 1650:1740]
  curExchangeProcessed = scrape.preprocessImage(curExchange)
  if(debugMode):
    scrape.cv2.imshow('Currency Exchange', curExchangeProcessed)
    scrape.cv2.waitKey(200)
  goldCost = scrape.imageToDigits(curExchangeProcessed)

  # remove existing files first in `curExchangeCompletePath` to make room for the updated ones
  for oldImage in os.listdir(curExchangeCompletePath):
    os.remove('{0}/{1}'.format(curExchangeCompletePath, oldImage))
  # transfer all files to completed DIR
  for existingImage in os.listdir(curExchangeIncompletePath):
    
    shutil.move('{0}/{1}'.format(curExchangeIncompletePath, existingImage),
               '{0}/{1}'.format(curExchangeCompletePath, existingImage))
  print('It costs {0} gold per 95 crystals at {1} gold per crystal'.format(goldCost, goldCost/95))
  pyautogui.press('esc')
  return float(goldCost/95)
  