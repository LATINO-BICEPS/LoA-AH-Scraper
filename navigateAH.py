import pyautogui
# from datetime import datetime
import datetime
import scrape
import os
from pyautogui import click
from time import sleep
from configuration import debugMode, screenshotPath, cSpeed, dryrun, debugTime, token, org, url
import shutil
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

pyautogui.FAILSAFE = True # move cursor to upper left to abort

def sendToInfluxDB(bucket, dataDict, rarity='empty', tier='empty'):  
  # if rarity has a value, that means it is engraving
  # if tier has a value, that means it is honing mats
  if(rarity != 'empty'):
    tagName = 'rarity'
    tagValue = rarity
  else:
    tagName = 'tier'
    tagValue = tier

  with InfluxDBClient(url, token, org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for item in dataDict:
      itemName = item
      avgDayPrice = dataDict[item][0]  
      recentPrice = dataDict[item][1] 
      lowestPrice = dataDict[item][2] 

      # add avgDayPrice data point
      avgDayPricePoint = Point(itemName) \
        .measurement(itemName) \
        .tag(tagName, tagValue) \
        .field('avgDayPrice', avgDayPrice) \
        .time(datetime.datetime.utcnow(), WritePrecision.NS)
      write_api.write(bucket, org, avgDayPricePoint)

      # add recentPrice data point
      recentPricePoint = Point(itemName) \
        .measurement(itemName) \
        .tag(tagName, tagValue) \
        .field('recentPrice', recentPrice) \
        .time(datetime.datetime.utcnow(), WritePrecision.NS)
      write_api.write(bucket, org, recentPricePoint)

      # add lowestPrice data point
      lowestPricePoint = Point(itemName) \
        .measurement(itemName) \
        .tag(tagName, tagValue) \
        .field('lowestPrice', lowestPrice) \
        .time(datetime.datetime.utcnow(), WritePrecision.NS)
      write_api.write(bucket, org, lowestPricePoint)

  return
  
def sortByHighestPrice():
  pyautogui.moveTo(1622,460,cSpeed)
  click()
  sleep(0.5)
  click()
  sleep(1)
  return
  
def openCloseStore():
  pyautogui.moveTo(1200,570,cSpeed)
  click()
  pyautogui.press('F4')

def openCloseMarket():
  pyautogui.moveTo(1200,570,cSpeed)
  click()
  pyautogui.hotkey("altleft", "y")
  sleep(2)

def selectTier(tier=1):
  """ give value [1,2,3] """
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
  elif(rarity == "gold" or rarity == "legendary"):
    pyautogui.moveRel(0,boxBelow*2,cSpeed)
    print('attempting scroll now')
    pyautogui.scroll(-100)
    pyautogui.moveRel(0,boxBelow*2,cSpeed)
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
  """ returns dict dataDict[productName] = [avgPrice, recentPrice, lowestPrice]

      takes screenshots of all available pages on a particular menu first 
      then processes them afterwards

      if batch=False, process the image in realtime
      description refers to specifics of the category -- greenEngravings for engravings"""

  try:
    print('-----------------------')
    print('Saving {0} now'.format(description))
    if(dryrun):
      print('This is a dryrun. No data will be saved. Change variable in `configuration.py`.')
    print('-----------------------')

    batchScreenshotIncompletePath = '{0}/{1}/incomplete'.format(screenshotPath, category)
    batchScreenshotCompletePath = '{0}/{1}/complete'.format(screenshotPath, category)
    # check if folder exists
    isIncompleteExist = os.path.exists(batchScreenshotIncompletePath)
    isCompleteExist = os.path.exists(batchScreenshotCompletePath)
    if not isIncompleteExist:
      os.makedirs(batchScreenshotIncompletePath)
      print('{0} Folder Created.'.format(batchScreenshotIncompletePath))
    if not isCompleteExist:
      os.makedirs(batchScreenshotCompletePath)
      print('{0} Folder Created.'.format(batchScreenshotCompletePath))

    itemDict = {} # stores all the data in this one particular instance
    # first delete all temp files in incomplete and logs from complete
    for existingImage in os.listdir(batchScreenshotIncompletePath):
      os.remove('{0}/{1}'.format(batchScreenshotIncompletePath, existingImage))
    for existingImage in os.listdir(batchScreenshotCompletePath):
      os.remove('{0}/{1}'.format(batchScreenshotCompletePath, existingImage))
    
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
      scrape.cv2.waitKey(debugTime)
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

    # batchScreenshotIncompletePath = '{0}/{1}/incomplete'.format(screenshotPath, category)
    # batchScreenshotCompletePath = '{0}/{1}/complete'.format(screenshotPath, category)
    print('Screenshot temp. directory: {0}'.format(batchScreenshotIncompletePath))
    
    # # remove existing files in both `batchScreenshotCompletePath`
    # for existingImage in os.listdir(batchScreenshotCompletePath):
    #   os.remove('{0}/{1}'.format(batchScreenshotCompletePath, existingImage))

    for screenshotFileName in os.listdir(batchScreenshotIncompletePath):
      # get page number by reading the last 3 chars (remember YYYY-MM-DD_HH-MM-SS_descriptionPageNum format)
      screenshotImage = scrape.cv2.imread(os.path.join(batchScreenshotIncompletePath, screenshotFileName))
      screenshotPageNumber = screenshotFileName[-7:-4]
      digitList = [char for char in screenshotPageNumber if char.isdigit()]
      screenshotPageNumber = int(''.join(str(digit) for digit in digitList))
      print('---------------------')
      print('Processing page:', screenshotPageNumber)
      print('---------------------')
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

def getEngravingData(green=True, blue=False, purple=False, gold=False):
  """ by default, only get the green books data 
  
  take multiple screenshots of engravings tab and save them in format
      [DD-MM-YYYY] XXXXXXX where XXXXX is the description of screenshot by default, 
      it will only take screenshots of ALL green book pages """
  try:
    openCloseMarket()
    # select engraving recipe
    pyautogui.moveTo(768,580,cSpeed)
    click()
    pyautogui.moveRel(0,40,cSpeed)
    click()
    sleep(1) # need delay while it loads
    category = 'engravings'
    influxDBBucket = 'lostArkEngravingRecipes'
    # get all green books
    if(green):
      selectRarity("green")
      sortByHighestPrice()
      description = "greenEngravings"
      greenEngravingsDict = batchProcessAllPages(description, category)
      if(not dryrun):
        sendToInfluxDB(influxDBBucket, greenEngravingsDict, 'green')
    # get all blue books
    if(blue):
      selectRarity("blue")
      sortByHighestPrice()
      description = "blueEngravings"
      blueEngravingsDict = batchProcessAllPages(description, category)
      if(not dryrun):
        sendToInfluxDB(influxDBBucket, blueEngravingsDict, 'blue')
    # get all purple books
    if(purple):
      selectRarity("purple")
      sortByHighestPrice()
      description = "purpleEngravings"
      purpleEngravingsDict = batchProcessAllPages(description, category)
      if(not dryrun):
        sendToInfluxDB(influxDBBucket, purpleEngravingsDict, 'purple')
    # get all gold books
    if(gold):
      selectRarity("gold")
      sortByHighestPrice()
      description = "goldEngravings"
      goldEngravingsDict = batchProcessAllPages(description, category)
      if(not dryrun):
        sendToInfluxDB(influxDBBucket, goldEngravingsDict, 'gold')

    pyautogui.press('esc') # close market menu
    
    return 
    
  except Exception as e:
    print('Getting engraving data failed.')
    print(e)
    pyautogui.press('esc')
    return  

def getGoldToCrystalsRate():
  """ returns a float of the rate from gold -> crystals """
  openCloseStore()
  currencyExchangeBox = (2200,1197,151,30)
  while True:
    currencyExchangeBoxImg = scrape.tempScreenshot(currencyExchangeBox)
    currencyExchangeBoxText = scrape.imageToText(currencyExchangeBoxImg)
    if(currencyExchangeBoxText == 'Currency Exchange'):
      pyautogui.moveTo(2200,1210,cSpeed)
      sleep(1)
      click()
      sleep(1)
      pyautogui.moveTo(1566,785,cSpeed)
      click()
      break
    sleep(1)
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
    scrape.cv2.waitKey(debugTime)
  goldCost = scrape.imageToDigits(curExchangeProcessed)

  # remove existing files first in `curExchangeCompletePath` to make room for the updated ones
  for oldImage in os.listdir(curExchangeCompletePath):
    os.remove('{0}/{1}'.format(curExchangeCompletePath, oldImage))
  # transfer all files to completed DIR
  for existingImage in os.listdir(curExchangeIncompletePath):
    
    shutil.move('{0}/{1}'.format(curExchangeIncompletePath, existingImage),
               '{0}/{1}'.format(curExchangeCompletePath, existingImage))
  print('-----------------------------------------------------------')
  print('It costs {0} gold per 95 crystals at {1} gold per crystal'.format(goldCost, goldCost/95))
  print('-----------------------------------------------------------')
  if(not dryrun):
  # send to influxdb
    bucket = 'currencyExchange'
    with InfluxDBClient(url, token, org) as client:
      write_api = client.write_api(write_options=SYNCHRONOUS)
      avgDayPricePoint = Point('goldToCrystalRate') \
        .measurement('goldToCrystalRate') \
        .field('goldToCrystalRate', goldCost/95) \
        .time(datetime.datetime.utcnow(), WritePrecision.NS)
      write_api.write(bucket, org, avgDayPricePoint)

  pyautogui.press('esc')
  sleep(1)
  return float(goldCost/95)
  
def getEnhancementMats(tier1=True, tier2=False, tier3=False):
  """ if tier1=True, get all data of tier 1 honing mats and send to influxdb"""
  try:
    openCloseMarket()
    # select enhancement mats
    pyautogui.moveTo(690,622,cSpeed)
    click()
    pyautogui.moveRel(0,40,cSpeed)
    click()
    sleep(1) # need delay while it loads
    category = 'enhancementMats'
    influxDBBucket = 'lostArkEnhancementMats'

    if(tier1):
      selectTier(1)
      sortByHighestPrice()
      search()
      description = "tier1Mats"
      tier1MatsDict = batchProcessAllPages(description, category)
      if(not dryrun):
        sendToInfluxDB(influxDBBucket, tier1MatsDict, tier=1)
    if(tier2):
      selectTier(2)
      sortByHighestPrice()
      search()
      description = "tier2Mats"
      tier2MatsDict = batchProcessAllPages(description, category)
      if(not dryrun):
        sendToInfluxDB(influxDBBucket, tier2MatsDict, tier=2)
    if(tier3):
      selectTier(3)
      sortByHighestPrice()
      search()
      description = "tier3Mats"
      tier3MatsDict = batchProcessAllPages(description, category)
      if(not dryrun):
        sendToInfluxDB(influxDBBucket, tier3MatsDict, tier=3)
    pyautogui.press('esc')
    sleep(1)

  except Exception as e:
    print('Exception Occured')
    print(e)
    pyautogui.press('esc')
    return  

if __name__ == '__main__':
  getGoldToCrystalsRate()