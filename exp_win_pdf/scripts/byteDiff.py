import math
import random
import string
import subprocess
import time
import os
import datetime
import codecs
import shlex


# If false, this script will only print out the difference between
# two binary files. Otherwise, it will start a simplification process.
doCrashSimplify = True

# These positions can guide us analyzing the pdf binary.
printDiffPositionsHex = True


# branch0weight / 10 indexes will be allocated for branch 0.
# So that we can have imbalanced binary search. 
branch0weight = 7


maxTrialNum = 5


fileOriginal = "J:/Data/pdfFuzzerTargets3/XeTeX-notes.pdf"
#fileFuzzed = "J:/Data/pdfFuzzerTemp/XeTeX-notes_crash_Nitro_simplify.pdf"

fileFuzzed = "J:/Data/pdfFuzzerDiagnosis/run0/XeTeX-notes_crash_Nitro_simplify.pdf"

outputFolder = "J:/Data/pdfFuzzerDiagnosis/"

fuzzOutput = outputFolder + "fuzz.pdf"

apps = [
    "\"C:/Program Files (x86)/Nitro/Reader 3/NitroPDFReader.exe\"",
    "E:/Software/SumatraPDF-3.0/SumatraPDF.exe"
]

appID = 0

waitTime = 10


bufOriginal = bytearray(open(fileOriginal, 'rb').read())
bufFuzzed = bytearray(open(fileFuzzed, 'rb').read())

assert len(bufOriginal) == len(bufFuzzed)

bufLen = len(bufOriginal)

# The diffCount roughly equals the fuzzFacotr. They are not identical
# because during fuzzing, the new byte and the old byte could be the same
# with the chance of 1 / 256.
diffCount = 0

diffPositions = []
fuzzByteValues = []

for i in range(bufLen):
    if bufOriginal[i] != bufFuzzed[i]:
        diffCount += 1
        diffPositions.append(i)
        fuzzByteValues.append(bufFuzzed[i])
        
print("diffCount = " + str(diffCount))

if printDiffPositionsHex:
    hexList = []
    for pos in diffPositions:
        hexList.append(hex(pos))
    print(hexList)

########################
# Start simplification #
########################

# Contains all possible indexes of diffPositions. Our goal is 
# to prune it to minimal.
indexes = []
for i in range(diffCount):
    indexes.append(i)

searchContinue = True

numberOfCrashes = 0

iterationCount = 0

# When the number of suspects is very small, we enter the rotation mode.
# Here, we try to exclude bytes one by one, from the last one.
# It seems that bytes in the beginning are usually more important.
rotationIndex = 10

while doCrashSimplify and searchContinue:

    print("Start a new simplification round.")
    print("There are " + str(len(indexes)) + " possible positions." )

    iterationCount += 1

    # We use a binary search to simplify the crash input.
    halfIndexes = []
    halfIndexes.append([])
    halfIndexes.append([])

    if len(indexes) <= 10:

        if rotationIndex > len(indexes) - 1:
            rotationIndex = len(indexes) - 1
        else:
            rotationIndex -= 1
            if rotationIndex < 0:
                print("rotation finished, cannot simplify more.")
                break
        # rotation mode
        for i in range(len(indexes)):
            if i != rotationIndex:
                halfIndexes[0].append(indexes[i])
            else:
                halfIndexes[1].append(indexes[i])
    else:    
        # randomly select half indexes for a branch.
        for i in indexes:
            dice = random.randrange(10)
            if dice < branch0weight:
                halfIndexes[0].append(i)
            else:
                halfIndexes[1].append(i)

    print("Branch 0 length = " + str(len(halfIndexes[0])))
    print("Branch 1 length = " + str(len(halfIndexes[1])))

    # 0 means no crash
    # 1 means crash
    branchResults = [0] * 2

    for branch in range(2):
        buf = bytearray(open(fileOriginal, 'rb').read())
        for j in range(len(halfIndexes[branch])):
            position = diffPositions[halfIndexes[branch][j]]
            buf[position] = fuzzByteValues[halfIndexes[branch][j]]

        f_fuzzOutput = open(fuzzOutput, 'wb')
        f_fuzzOutput.write(buf)
        f_fuzzOutput.close()

        app = apps[appID]

        cmd = app
        cmdArray = shlex.split(cmd)
        cmdArray.append(fuzzOutput)

        process = subprocess.Popen(cmdArray)

        time.sleep(waitTime)

        if process.poll() != None:
            # If the simplified input still crash the app, we save it.
            numberOfCrashes += 1
            appName = app.split("/")[len(app.split("/"))-1]
            print("Branch " + str(branch) + " crashed application: " + appName + " on file " + fileOriginal)
            f_crash_input = open(outputFolder + "crash_input" + str(numberOfCrashes) + ".pdf", "wb")
            f_crash_input.write(buf)
            f_crash_input.close()
            indexes = halfIndexes[branch]
            print("Number of possilbe positions is reduced to " + str(len(indexes)))
            branchResults[branch] = 1
            rotationIndex = len(indexes)
        else:
            print("Branch " + str(branch) + " did not crash the app.")
            process.terminate()
            branchResults[branch] = 0
        time.sleep(1)

    if branchResults[0] == 0 and branchResults[1] == 0:
        print("Both branches did not trigger a crash.")
        if iterationCount > maxTrialNum:
            searchContinue = False
    elif branchResults[0] == 1 and branchResults[1] == 1:
        print("Both branches triggered a crash. TODO: address it!")
        searchContinue = False
    else:
        iterationCount = 0
    
# The latest crash_input should be the smallest.



# We could start with a binary search. Basically,
# we randomly select half of the changes and create a input.pdf.
# Then, we run Nitro pdf and see if the input will cause a crash.
# If no, we choose the other half.
# If both half no, the binary search fails and we can either stop or
# switch to brute force search.
# If one half succeed, we can continue the binary search.
# At the end, we should find a small set of byte changes that can
# reproduce the crash.

    

