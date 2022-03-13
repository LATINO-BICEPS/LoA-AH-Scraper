debugMode = False # displays window tiles to live view the scanning/transcribing process
debugTime = 0 # set to 0 (ms) for the live window tiles to stay indefinitely until a key has been pressed - value of 200 is ideal
pyTesseractPath = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" 
screenshotPath = './img' # where to store the temp screenshots where it will process and delete it after
cSpeed = 0.2 # cursor speed - 0 is instant
dryrun = False # when set to True, it will not push to influxdb. debugMode must be set to False

# influxdb deets
token = "bHhdq3fzMemWaVm_5Dzliir1Higy644sFbkpBhuYzVXe3LUZfZwaMZGuMmNZvu8cgOX85BCPvWFV2CeIwxsk8w=="
org = "dev"
url = "http://192.168.1.244:8086" # influxdb url