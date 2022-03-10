import cv2
import pytesseract
import pyautogui
import os
import time

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" 
screenshotPath = './hpPotsTemp'
potHeals = 2000 # how much pot heals for
potHotkey = '7' # my pot is on the number 7

def imageToText(img):
    # returns item name from image
    boxes = pytesseract.image_to_data(img)
    num = []
    for count,box in enumerate(boxes.splitlines()):
        if(count != 0):
            box = box.split()
            if(len(box) == 12):
                text = box[11].strip('@®')
                if(text != ''):
                    num.append(text)
    text = ' '.join(num)
    return text

def resize(img, scale_percent=300):
    # automatically resizes it about 300% by default
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized

def preprocessImage(img, scale=300):
    """ input RGB colour space """
    # makes results more accurate - inspired from https://stackoverflow.com/questions/58103337/how-to-ocr-image-with-tesseract
    # another resource to improve accuracy - https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
    
    # converts from rgb to grayscale then enlarges it
    # applies gaussian blur
    # convert to b&w
    # invert black and white colours (white background, black text)
    grayscale = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    resized = resize(grayscale, scale)
    blurred = cv2.GaussianBlur(resized, (5,5), 0)
    (thresh, blackAndWhite) = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
    invertedColours = cv2.bitwise_not(blackAndWhite)
    return invertedColours

def screenshot():
  """ returns the file path of the newly created screenshot"""
  isPathExist = os.path.exists(screenshotPath)
  if not isPathExist:
    os.makedirs(screenshotPath)
    print('{0} Folder Created.'.format(screenshotPath))
  filename = 'tempHP'
  screen = pyautogui.screenshot(region=(970,1137,160,16))
  # Save as PNG - more accurate than JPG but almost 10x file size
  screenshotImagePath = "{0}/{1}.png".format(screenshotPath, filename)
  screen.save(screenshotImagePath)

  return screenshotImagePath

def getCurrentHP():
  """ returns an int list currentAndMaxHP = [currentHP, maxHP] """
  # currentHPImg = cv2.imread(screenshot())[1137:1153,970:1130]
  currentHPImg = cv2.imread(screenshot())
  currentHPImg = cv2.cvtColor(currentHPImg, cv2.COLOR_BGR2RGB) 
  # cv2.imshow('currentHP', currentHPImg)
  # cv2.waitKey(200)
  currentHP = imageToText(preprocessImage(currentHPImg))
  currentAndMaxHP = currentHP.split('/')
  currentAndMaxHP[0] = int(currentAndMaxHP[0])
  currentAndMaxHP[1] = int(currentAndMaxHP[1])
  return currentAndMaxHP

def isPotUsed():
  """ returns True if pot has already been used """

def run():
  while True:
    try:
      currentHP, maxHP = getCurrentHP()
      print('CurrentHP: {0} | MaxHP: {1}'.format(currentHP, maxHP))
      difference = maxHP-currentHP
      if(difference >= potHeals and currentHP != 0):
        pyautogui.press(potHotkey)
        print('Healing now.')
        time.sleep(17)
      else: 
        time.sleep(2)
    except:
      time.sleep(2)
      pass

run()