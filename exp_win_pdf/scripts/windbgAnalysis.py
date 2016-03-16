# Python 2.7

import pykd
import os
import time
import hashlib

apps = [
    "\"C:/Program Files (x86)/Nitro/Reader 3/NitroPDFReader.exe\"",
    "E:/Software/SumatraPDF-3.0/SumatraPDF.exe"
]

testFile = "E:/Seagate1TB_backup/Data/pdfFuzzerResult/run1/wooyun_crash_Nitro.pdf"

resultFolder = "E:/Seagate1TB_backup/Data/pdfFuzzerResult/run"

summaryFile = "E:/Seagate1TB_backup/Data/pdfFuzzerResult/summary.txt"

runMin = 1
runMax = 6

fList = []

for i in range(runMin, runMax + 1):
    for root, subFolders, files in os.walk(resultFolder + str(i) + "/"):
        for f in files:
            if "pdf" not in f:
                continue
            if f == "??????- ????_crash_Nitro.pdf":
                print "WARNING: Skipped this file due to encoding"
                continue
            fList.append(os.path.join(root,f))

sumFile=open(summaryFile, "w")

for f in fList:

    print("File Name: " + f)
    
    sumFile.write("File Name: " + f)
    sumFile.write("\n")

    if f == "E:/Data/pdfFuzzerResult/run6/crash_input09.pdf":
        print "WARNING: Skip this file because it won't trigger a crash on my new laptop"
        sumFile.write("WARNING: Skip this file because it won't trigger a crash on my new laptop")
        sumFile.write("\n")
        sumFile.write("\n")
        continue

    pykd.startProcess(apps[0] + " " + f)

    pykd.go()

    # print information at crash site
    r_o = pykd.dbgCommand('r')
    # print r_o

    k_o = pykd.dbgCommand('k')
    #print k_o
    stackTrace = ""
    firstLine = True
    lines = k_o.split("\n")
    for line in lines:
        if firstLine:
            firstLine = False
            continue
        if line.strip() == "":
            continue
        stackTrace += line.split(" ")[2].split("+")[0]

    m = hashlib.md5()
    m.update(stackTrace)
    print("md5: " + str(m.hexdigest()))    
    sumFile.write("md5: " + str(m.hexdigest()))
    sumFile.write("\n")
        
    lines = r_o.split("\n")

    print lines[len(lines)-2]
    sumFile.write("Crash Inst: " + lines[len(lines)-2])
    sumFile.write("\n")

    # Need to use the full path
    loadRet = pykd.dbgCommand("!load E:/Security/msec.dll")
    expRet = pykd.dbgCommand("!exploitable")
    #print loadRet
    print expRet
    sumFile.write(expRet)
    sumFile.write("\n")

    eip = pykd.reg("eip")
    sumFile.write("eip: " + str(hex(eip)))
    sumFile.write("\n")
    sumFile.write("\n") 

    pykd.killAllProcesses()

    #break
    
    time.sleep(2)

sumFile.close()



#stackList = pykd.getStack()

#error = pykd.dbgCommand("!gle")
#print error

#lastDebugEvt = pykd.getLastEvent() 
#print lastDebugEvt

#lastException = pykd.getLastException()
#print lastException

#gRet = pykd.dbgCommand("g")
#print gRet











