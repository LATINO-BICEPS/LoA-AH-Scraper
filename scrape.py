import cv2
import pytesseract
from configuration import debugMode, pyTesseractPath

pytesseract.pytesseract.tesseract_cmd = pyTesseractPath

# excerpt from https://www.youtube.com/watch?v=6DjFscX4I_c
def imageToText(img):
    # returns item name from image
    boxes = pytesseract.image_to_data(img)
    textList = []
    for count,box in enumerate(boxes.splitlines()):
        if(count != 0):
            box = box.split()
            if(len(box) == 12):
                text = box[11].strip('@®')
                if(text != ''):
                    textList.append(text)
    text = ' '.join(textList)
    ## Alternate method
    # text = pytesseract.image_to_string(img)
    # print("Appending:", text)
    return text

def imageToDigits(img):
    """ returns a float
    preprocess before passing through img """
    # imageToText() did not capture the digits accurately at times so I use this
    # possibly could merge the 2 functions to make code shorter
    conf = r'--oem 3 --psm 7 outputbase digits'
    boxes = pytesseract.image_to_data(img, config=conf)
    textList = []
    for count,box in enumerate(boxes.splitlines()):
        if(count != 0):
            box = box.split()
            if(len(box) == 12):
                text = box[11]
                if(text != ''):
                    print("Appending Product Price:", text) 
                    textList.append(text)
    text = ' '.join(textList)
    return float(text)

def getProduct(startY, startX, catalog):
    """ can preprocess before passing through catalog if desire accuracy"""
    # returns [productName, endY, endX]
    height, productWidth = 60,300
    productName = catalog[startY:startY+height,startX:startX+productWidth]
    if(debugMode):
        cv2.imshow('Product Name', productName)
        cv2.waitKey(200)
    productName = imageToText(productName)
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
        priceImageProcessed = preprocessImage(priceNoGoldImage, 500)
        price = imageToDigits(priceImageProcessed) 
        priceList.append(price)
        if(debugMode):
            cv2.imshow('priceImage', priceImage)
            # cv2.imshow('priceNoGoldImage', priceNoGoldImage)
            # cv2.imshow('priceImageProcessed', priceImageProcessed)
            cv2.waitKey(200)
    return priceList

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
        cv2.waitKey(200)
        rows = 10
    for i in range(rows): # all is 10
        # fetch product name
        productName, endY, endX = getProduct(startY,startX,catalog)
        if(category == 'engravings'):
            productName = productName[:-26] # exclusive to engravings. removes [Untradeable .. ]
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