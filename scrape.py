import cv2
import pytesseract
import pyautogui
import os
from configuration import debugMode, pyTesseractPath, debugTime

pytesseract.pytesseract.tesseract_cmd = pyTesseractPath

# excerpt from https://www.youtube.com/watch?v=6DjFscX4I_c
def imageToText(img):
    # returns item name from image, preprocess if needed
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
    ## Alternate method
    # text = pytesseract.image_to_string(img)
    # print("Name:", text)
    return text

def imageToDigits(img):
    """ returns a float value of the scanned image
    !!preprocess before passing through img !! """
    # imageToText() did not capture the digits accurately at times so I used this
    # possibly could merge the 2 functions to make code shorter
    conf = r'--oem 3 --psm 7 outputbase digits'
    boxes = pytesseract.image_to_data(img, config=conf)
    numList = []
    for count,box in enumerate(boxes.splitlines()):
        if(count != 0):
            box = box.split()
            if(len(box) == 12):
                text = box[11] # the 12th column contains the text
                if(text != ''):
                    if(text == '-'): # if it is an invalid value (i.e. "-"), set it to 0 dollars
                        text = '0'
                    print("Appending Product Price:", text)
                    numList.append(text)
    # for some damn reason it does not detect some numbers like 7.1 Gold for Green grudge engraving 
    if(len(numList) == 0): 
        numList.append('0')
    num = numList[0]
    # occasionally there will be inaccuracies
    # i.e. 1050 will be misinterpreted as 1.050
    # check from right to left for every 3 digits if there's a period
    # if there is, that is ONE thousand
    # else, leave as it is
    if(len(num) >= 5):
        if(num[-4:-3] == '.'):
            num = num[:-4] + num[-3:]
    return float(num)

def getProduct(startY, startX, catalog):
    """ returns the product name of a listing """
    # returns [productName, endY, endX]
    height, productWidth = 60,300
    productName = catalog[startY:startY+height,startX:startX+productWidth]

    # modified threshold of preprocessImage() from 127 to 60 for the algo. to discern more clearly
    # increases accuracy of product name
    grayscale = cv2.cvtColor(productName, cv2.COLOR_RGB2GRAY)
    resized = resize(grayscale)
    blurred = cv2.GaussianBlur(resized, (5,5), 0)
    (thresh, blackAndWhite) = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY) # value of 80 is good for gold books
    invertedColours = cv2.bitwise_not(blackAndWhite)

    if(debugMode):
        cv2.imshow('Product Name', productName)
        cv2.imshow('Processed Product Name', invertedColours)
        cv2.waitKey(debugTime)
    productName = imageToText(invertedColours)
    print('The product name is: {0}'.format(productName))
    productList = [productName, startY, startX+productWidth]
    return productList

def getPrices(startY, startX, catalog):
    # returns [Avg. Day Price, Recent Prices, Lowest Price]
    # pixel distance between product items and the 3 proceeding boxes
    height, subWidth = 60, 163 
    priceList = []
    rightMargin = 33 # 33px off to the right cuts off the gold symbol
    for i in range(3):
        priceImage = catalog[startY:startY+height,startX+subWidth*i:startX+subWidth+subWidth*i] # cut into 3 subgrids
        if(i == 0): # on first run, get dimension of the subgrids
            y, x, _ = priceImage.shape 
        # removes the gold symbol to avoid tesseract misinterpreting it as a 0 (e.g 3 O can be seen as 30)
        priceNoGoldImage = priceImage[0:y,0:x-rightMargin]
        priceImageProcessed = preprocessImage(priceNoGoldImage, 500, 50) # changed thresh to 60 for accuracy
        price = imageToDigits(priceImageProcessed) 
        priceList.append(price)
        if(debugMode):
            cv2.imshow('priceImage', priceImage)
            # cv2.imshow('priceNoGoldImage', priceNoGoldImage)
            cv2.imshow('priceImageProcessed', priceImageProcessed)
            cv2.waitKey(debugTime)
    return priceList

def resize(img, scale_percent=300):
    # automatically resizes it about 300% by default
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized

def preprocessImage(img, scale=300, threshhold = 127):
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
    (thresh, blackAndWhite) = cv2.threshold(blurred, threshhold, 255, cv2.THRESH_BINARY)
    invertedColours = cv2.bitwise_not(blackAndWhite)
    return invertedColours

def transcribeCatalog(img, category='default'):
    """ transcribes the fed full sized image, crops it to fit then returns dictionary
    corresponding to the `Avg. Day Price`, `Recent Price` and `Lowest Price` of all items on the page. 
    optimized for 1440p, used shareX alongside trial and error to find the points
    pixel positions are hardcoded but I don't bloody know how to do it otherwise """

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
    catalog = img[480:1050,930:1720] # crops fullscreen screenshot to just shop elements
    dataDict = {}
    startY, startX, rows = 0,0,10
    if(debugMode):
        cv2.imshow('catalog', catalog)
        cv2.waitKey(debugTime)
    for i in range(rows):
        # fetch product name
        productName, endY, endX = getProduct(startY,startX,catalog)
        # fix misspellings
        if(productName == 'Harmony Shard Pouct (L)'):
            productName = 'Harmony Shard Pouch (L)'
        if(productName == 'Harmony Shard Poucr (M)'):
            productName = 'Harmony Shard Pouch (M)'
        if(productName == 'Metallurgy: Basic Foldirg'):
            productName = 'Metallurgy: Basic Folding'
        # exclusive to engravings. removes [Untradeable .. ] category
        if(category == 'engravings'):
            productName = productName[:-26]

        # stops if there are no more entries
        if(productName == ''):
            print("There are no more items to be transcribed.")
            break

        # fetch prices
        avgPrice, recentPrice, lowestPrice = getPrices(endY, endX, catalog)
        dataDict[productName] = [avgPrice, recentPrice, lowestPrice]
        print(productName, dataDict[productName])
        # iterate one row after ~57px below
        startY += 57

    return dataDict

def tempScreenshot(roi=(0,0,2560,1440)):
  """ returns the file path of the newly created temp screenshot
      by default, takes screenshot of whole screen. specify Region Of Interest with syntax below
      region = (left, top, width, height) """

  screenshotPath = "./img/temp"
  isPathExist = os.path.exists(screenshotPath)
  if not isPathExist:
    os.makedirs(screenshotPath)
    print('{0} Folder Created.'.format(screenshotPath))
  filename = 'temp'
  screen = pyautogui.screenshot(region=roi) 
  # Save as PNG - more accurate than JPG but almost 10x file size
  screenshotImagePath = "{0}/{1}.png".format(screenshotPath, filename)
  screen.save(screenshotImagePath)
  return screenshotImagePath