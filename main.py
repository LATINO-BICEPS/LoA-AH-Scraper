import navigateAH
import scrape
import pyautogui
import os
from time import sleep
from configuration import cSpeed

def shutdown():
  print('Shutting PC Down now.')
  os.system("shutdown /s /t 1")
  return

def isInMemoryChamber():
  """ run this for first init. 
      this function is not used but may be looked into in the  future"""
  pyautogui.press('esc')
  sleep(1)
  pyautogui.moveTo(1092, 613,cSpeed)
  pyautogui.click()
  sleep(1)
  pyautogui.moveTo(1219,792,cSpeed)
  pyautogui.click()
  sleep(1)
  while True:
    if(detectsCombatText):
      print("User is in Memory Chamber.")
      sleep(10)
      pyautogui.rightClick(975, 489)
      sleep(4)
      return True
    sleep(5)

def detectsEnterButton():
  print('Detecting Enter Button..')
  enterButtonBox = (1236,1087,70,30)
  enterButtonImg = scrape.tempScreenshot(enterButtonBox)
  enterButtonText = scrape.imageToText(enterButtonImg)
  if(enterButtonText == 'Enter'):
    print('Detected enter button. Proceeding now.')
    pyautogui.moveTo(1236,1087,cSpeed)
    pyautogui.click()
    return True
  print('Enter Button Not Detected.')

def detectsLaunchButton():
  print('Detecting Launch Button..')
  launchButtonBox = (1133,1173,100,40)
  launchButtonImg = scrape.tempScreenshot(launchButtonBox)
  launchButtonText = scrape.imageToText(launchButtonImg)
  if(launchButtonText == 'Launch'):
    pyautogui.moveTo(1133,1173,cSpeed)
    pyautogui.click()
    return True
  print('Launch Button Not Detected.')

def detectsCombatText():
  print('Detecting Blue Combat Text..')
  combatBox = (30,1227,57,18)
  combatBoxImg = scrape.cv2.imread(scrape.tempScreenshot(combatBox)) 
  processedCombatBoxImg = scrape.preprocessImage(combatBoxImg)
  combatBoxText = scrape.imageToText(processedCombatBoxImg)
  if(combatBoxText == 'Combat'):
    return True
  print('Combat Text Not Detected.')

def isNowInGame():
  """ returns True when all the char. is already in-game and able to 
      open the market/store. this function launches the game directly from desktop shortcut
      if it doesn't detect that ur char. is in-game already """
  # case 1
  if(detectsEnterButton()):
    while True:
      if(detectsLaunchButton()):
        break
      sleep(5)    
    while True:
      if(detectsCombatText()):
        break
      sleep(5)
    return True
  # case 2
  elif(detectsLaunchButton()):
    while True:
      if(detectsCombatText()):
        break
      sleep(5)
    return True
  # case 3 (if char is already in-game but not in memory chamber)
  elif(detectsCombatText()):
    return True
  else:
    # opens the game from desktop
    print('-----------------------------------------------------')
    print('Game is not open. Launching game from desktop now.')
    print('-----------------------------------------------------')
    pyautogui.moveTo(30, 158, cSpeed)
    pyautogui.click()
    pyautogui.click()
    sleep(150) # this is approximately how long it takes for my game to open
    # looks for 'Enter' button every 10s
    while True:
      if(detectsEnterButton()):
        break
      sleep(5)
      # need to do a check in case of queue
    if(True):
      pass
    # # clicks launch button when ready every 5 seconds
    while True:
      if(detectsLaunchButton()):
        break
      sleep(5)
    # detects when finally in-game by checking bottom left if the blue "Combat" text is shown
    while True:
      if(detectsCombatText()):
        return True
      sleep(5)

def run():
  if(isNowInGame()):
    print('---------------------')
    print('Now fully in-game.')
    print('---------------------')
    # navigateAH.getEngravingData(green=1, blue=1, purple=1,gold=1)
    navigateAH.getEnhancementMats(tier1=True, tier2=True, tier3=True)
    navigateAH.getGoldToCrystalsRate()
    print('Closing game in 10 seconds.')
    sleep(10)
    pyautogui.hotkey("altleft", "f4") # quit game when finished
    shutdown()

run()