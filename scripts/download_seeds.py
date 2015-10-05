
import csv
import codecs
import urllib.request
from os import listdir 
from os.path import isfile, join 


seedFolder = "seeds/"

files = [ f for f in listdir(seedFolder) if isfile(join(seedFolder,f)) ]

fileSet = set(files)

listFile = codecs.open("mp3_pdf_list.csv", "r", "utf-8")

reader = csv.reader(listFile)

suffixes = ["pdf", "mp3"]

unknownSuffixCount = 0
totalCount = 0

exceptionCount = 0

for row in reader:

    totalCount += 1    
    
    url = row[3]
    
    #fileName = url[url.rfind('/')+1:]
    
    fileName = url
    
    if not fileName.endswith("pdf") and not fileName.endswith("mp3"):
        unknownSuffixCount += 1
        continue

    fileName = url.replace('/', '_')
    fileName = fileName.replace(':', '_')
    
    if fileName in fileSet:
        continue
    
    try:
        urllib.request.urlretrieve(url,  seedFolder + fileName)
    except:
        print("Exception!")
        exceptionCount += 1

print("unknownSuffixCount = " + str(unknownSuffixCount))
print("totalCount = " + str(totalCount))
print("exceptionCount = " + str(exceptionCount))
    