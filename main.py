import cv2
from cv2 import INTER_AREA
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
img = cv2.imread('img\\test.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# optimized for 1440p, used shareX alongside trial and error to find the points
# pixel positions are hardcoded but I don't bloody know how to do it otherwise
catalog = img[480:1050,930:1720]


# excerpt from https://www.youtube.com/watch?v=6DjFscX4I_c
def imageToText(img):
    # returns text from image
    boxes = pytesseract.image_to_data(img)
    textList = []
    for count,box in enumerate(boxes.splitlines()):
        if(count != 0):
            box = box.split()
            if(len(box) == 12):
                text = box[11].strip('@®')
                if(text != ''):
                    print("Appending:", text)
                    textList.append(text)
    text = ' '.join(textList)
    ## Alternate method
    # text = pytesseract.image_to_string(img)
    # print("Appending:", text)
    return text

def imageToDigits(img):
    conf = r'--oem 3 --psm 7 outputbase digits'
    boxes = pytesseract.image_to_data(img, config=conf)
    textList = []
    for count,box in enumerate(boxes.splitlines()):
        if(count != 0):
            box = box.split()
            if(len(box) == 12):
                text = box[11].strip('@®')
                if(text != ''):
                    print("Appending:", text)
                    textList.append(text)
    text = ' '.join(textList)
    return text

def getProduct(startY, startX):
    # returns [productName, endY, endX]
    height, productWidth = 60,300
    productName = catalog[startY:startY+height,startX:startX+productWidth]
    # cv2.imshow('cropped', productName)
    # cv2.waitKey(0)
    productName = imageToText(productName)
    productList = [productName, startY, startX+productWidth]
    return productList

def getPrices(startY, startX):
    # returns [Avg. Day Price, Recent Prices, Lowest Price]
    # pixel distance between product items and the 3 proceeding boxes
    height, subWidth = 60, 163
    priceList = []
    x = 0
    for i in range(3):
        priceImage = catalog[startY:startY+height,startX+x:startX+subWidth+x]
        y, x, _ = priceImage.shape 
        rightMargin = 33 # 33px off to the right cuts off the gold symbol
        removedGoldImage = priceImage[0:y,0:x-rightMargin] # crops only relevant parts
        removedGoldImage = preprocessImage(removedGoldImage)
        price = imageToDigits(removedGoldImage) 
        try:
            priceList.append(float(price))
            # cv2.imshow('price works', removedGoldImage)
            # cv2.waitKey(0)
        except:
            print("Bug:", price)
            cv2.imshow('bug', removedGoldImage)
            cv2.waitKey(0)
        x += subWidth
    return priceList

def resize(img, scale_percent=300):
    # automatically resizes it about 300% by default
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=INTER_AREA)
    return resized

def preprocessImage(img):
    # makes results more accurate - inspired from https://stackoverflow.com/questions/58103337/how-to-ocr-image-with-tesseract
    # another resource to improve accuracy - https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
    
    # converts to rgb to grayscale then enlarges it
    # applies gaussian blur
    # convert to b&w
    # invert black and white colours (white background, black text)
    grayscale = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    resized = resize(grayscale)
    blurred = cv2.GaussianBlur(resized, (5,5), 0)
    (thresh, blackAndWhite) = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
    invertedColours = cv2.bitwise_not(blackAndWhite)
    return invertedColours

def run():
    dataDict = {}
    startY, startX = 0,0
    cv2.imshow('catalog', catalog)
    for i in range(10): # all is 10
        # fetch product name
        productName, endY, endX = getProduct(startY,startX)
        productName = productName[:-26] # this slicing is only for engravings
        # fetch prices
        avgPrice, recentPrice, lowestPrice = getPrices(endY, endX)
        dataDict[productName] = [avgPrice, recentPrice, lowestPrice]
        # iterate one row after ~57px below
        startY += 57
    for item in dataDict:
        print(item, dataDict[item])

run()
