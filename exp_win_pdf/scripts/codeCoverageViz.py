from matplotlib.pyplot import figure, show, cm
from numpy import where
from numpy.random import rand
from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time
import matplotlib.pyplot as plt
from operator import itemgetter


def getFileListByCreationDate(dirpath):

    # get all entries in the directory w/ stats
    entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
    entries = ((os.stat(path), path) for path in entries)

    # leave only regular files, insert creation date
    entries = ((stat[ST_CTIME], path)
        for stat, path in entries if S_ISREG(stat[ST_MODE]))
    #NOTE: on Windows `ST_CTIME` is a creation date 
    #  but on Unix it could be something else
    #NOTE: use `ST_MTIME` to sort by a modification date

    pathList = []
    
    for cdate, path in sorted(entries):
        # print(time.ctime(cdate) + " " +  os.path.basename(path))
        #print(path)
        pathList.append(path)
    
    return pathList

codeCoverageFolder = "J:/Data/pdfFuzzerCodeCoverage"

# codeCoverageFolder = "D:/Vulnerabilities/pdfFuzzerCodeCoverage"

#codeCoverageFolder = "D:/Vulnerabilities/sample_c_files/codeCoverage"

pdfreader = "SumatraPDF"

#pdfreader = "loop.exe"

file_list = getFileListByCreationDate(codeCoverageFolder)

codeMin = {}
codeMax = {}

minStart = int("0xffffffff", 16)
maxEnd = 0

bbls = set()

pivotSet = set()

bblsCount = {}

fileCount = 1

for file in file_list:

    #print(file)
    
    f = open(file)

    moduleNum = 0

    bblLocal = set()
    bblLocalCount = {}

    for line in f:
        if line.startswith("Module Table:"):
            moduleNum = int(line.split(' ')[2])
        elif line.startswith(" 0, "):
            assert pdfreader in line.split(' ')[3]
        elif line.startswith("module[  0]: "):
            startS = line.split(' ')[3][:len(line.split(' ')[1]) - 1]
            index = 4
            offset = line.split(' ')[index]
            while offset.strip() == '':
                index += 1
                offset = line.split(' ')[index].strip()

            start = int(startS, 16)
                
            end = start + int(offset)

            bbl = startS + ":" + offset

            if bbl not in bbls:
                bbls.add(bbl)

            if bbl not in bblLocal:
                bblLocal.add(bbl)
                bblLocalCount[bbl] = 0
            #else:
                # This else branch is for debugging only
                #if fileCount == 2:
                    #print(line)
            bblLocalCount[bbl] += 1

            if start < minStart:
                minStart = start
            if end > maxEnd:
                maxEnd = end

    #print(str(hex(minStart)) + ' ' + str(hex(maxEnd)))
    #print(str(minStart) + ' ' + str(maxEnd))

    #print(len(bbls))

    if fileCount == 2:
        pivotSet = bblLocal
    elif fileCount > 2:
        intersecSize = len(set.intersection(pivotSet, bblLocal))
        #print(str(intersecSize) + ":" + str(len(bblLocal)))

    if len(bblLocal) != 4232 and len(bblLocal) != 4230:
        print(file)
        print(str(len(bblLocal)))

    #idList = []
    #countList = []
    #nextID = 1
    #for pair in sorted(bblLocalCount.items(), key=itemgetter(1), reverse=True):
    #    idList.append(nextID)
    #    countList.append(pair[1])
    #    nextID += 1

    #ax = plt.gca()
    #plt.xlabel('Basic Blocks')
    #plt.ylabel('Count')
    #plt.scatter(idList, countList)
    #plt.show()

    #print(len(bblLocal))
    
    f.close()

    fileCount += 1

    #if fileCount > 500:
    #    break

    
    

# the bar
x = where(rand(500)>0.3, 1.0, 0.0)

axprops = dict(xticks=[], yticks=[])
barprops = dict(aspect='auto', cmap=cm.binary, interpolation='nearest')

fig = figure()

# a vertical barcode -- this is broken at present
#x.shape = len(x), 1
#ax = fig.add_axes([0.1, 0.3, 0.1, 0.6], **axprops)
#ax.imshow(x, **barprops)

x = x.copy()
# a horizontal barcode
x.shape = 1, len(x)
ax = fig.add_axes([0.3, 0.1, 0.6, 0.1], **axprops)
ax.imshow(x, **barprops)


show()
