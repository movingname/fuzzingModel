# The original code is obtained here:
# http://forums.udacity.com/questions/100231307/my-two-fuzzers-for-pdf-readers-foxit-reader-and-adobe-acroreader-and-for-potplayer-mp3-files#cs258

import math
import random
import string
import subprocess
import time
import os
import datetime
import codecs
import shlex



#####################
# Files and folders #
#####################

apps = [
    "\"C:/Program Files (x86)/Nitro/Reader 3/NitroPDFReader.exe\"",
    "E:/Software/SumatraPDF-3.0/SumatraPDF.exe"
]

dynamoRioPath = "D:/Vulnerabilities/DynamoRIO-Windows-5.0.0-9/"

codeCoverageLog = "J:/Data/pdfFuzzerCodeCoverage"

codeCoverageCmd32 = "{0}bin32/drrun.exe -c {0}tools/lib32/release/drcov.dll -logdir {1} -dump_text -- {2}"

# pdfFuzzerTargets2 is the full pdf file collection
fuzz_input_dir = "J:/Data/pdfFuzzerTargets2"

# pdfFuzzerTargets3 is a small selected collection
#fuzz_input_dir = "J:/Data/pdfFuzzerTargets3"

fuzz_output = "J:/Data/pdfFuzzerTemp/fuzz.pdf"

fuzz_output_folder = "J:/Data/pdfFuzzerTemp/"

fuzz_log = codecs.open("J:/Data/pdfFuzzerLog/log_" + time.strftime("%Y%m%d%H%M%S.txt"), "w", "utf-8", buffering=0)

file_list = []

for root, subFolders, files in os.walk(fuzz_input_dir):
    for file in files:
        file_list.append(os.path.join(root,file))

#######################
# Now some parameters #
#######################

# In the training mode, we go through each file and record the code coverge info.
# We don't do fuzzing.
trainingMode = False

appID = 0

num_tests = 4500

if trainingMode:
    num_tests = len(file_list)

numberOfCrashes=0

#So the fuzz factor controls the number of bytes to be changed
#The lower the factor, the more bytes that will be modified.
FuzzFactor = 250

randFuzzFactor = True
maxFuzzFactor = 500
minFuzzFactor = 1

# In seconds
waitTime = 10
if trainingMode:
    waitTime = 15

fuzz_log.write("Fuzzing " + apps[appID] + '\n')
fuzz_log.write("Starts at " + str(datetime.datetime.now()) + '\n')

for i in range(num_tests):

    file_choice = random.choice(file_list)

    if trainingMode:
        file_choice = file_list[i]
    
    #app = random.choice(apps)

    app = apps[appID]

    if randFuzzFactor:
        FuzzFactor = random.randint(minFuzzFactor,maxFuzzFactor)

    buf = bytearray(open(file_choice, 'rb').read())

    if not trainingMode:

        numwrites = random.randrange(math.ceil((float(len(buf)) / FuzzFactor))) + 1

        for j in range(numwrites):
            rbyte = random.randrange(256)
            rn = random.randrange(len(buf))
            buf[rn] = rbyte

    f_fuzz_output = open(fuzz_output, 'wb')
    f_fuzz_output.write(buf)
    f_fuzz_output.close()

    fuzz_log.write("File " + file_choice + ": ")

    cmd = app

    if trainingMode:
        cmd = codeCoverageCmd32.format(dynamoRioPath, codeCoverageLog, app)

    #print(cmd)

    # see https://docs.python.org/2/library/shlex.html#shlex.split
    cmdArray = shlex.split(cmd)
    cmdArray.append(fuzz_output)

    process = subprocess.Popen(cmdArray)

    # Strangely, the first instance will fail to be terminated.
    # So the following code skips the first instance by launching the process again.
    if i == 0 and trainingMode:
        process.terminate()
        time.sleep(5)
        process = subprocess.Popen(cmdArray)

    time.sleep(waitTime)

    

    # If the return code is not None, then the process crashed.
    procStat = process.poll()

    if trainingMode:
        # The following code waits for the pdf reader to finish.
        # However, this works for SumatraPDF.exe, but not for NitroPDFReader.exe
        #while procStat != 1:
        #    time.sleep(1)
        #    procStat = process.poll()
        #    print(procStat)

        # So we simply kill the reader after certain amount of time.
        process.terminate()
        fuzz_log.write("\n")

    else:
        if procStat != None:

            numberOfCrashes += 1

            appName = app.split("/")[len(app.split("/"))-1]
            print(str(numberOfCrashes) + " crashed application: " + appName + " on file " + file_choice)
            fuzz_log.write(str(numberOfCrashes) + " crashed application: " + appName + "\n")

            # save this crash input for later forensics
            f_crash_input = open(fuzz_output_folder + "crash_input" + str(numberOfCrashes) + ".pdf", "wb")
            f_crash_input.write(buf)
            f_crash_input.close()
        else:
            process.terminate()
            fuzz_log.write("\n")
    
    time.sleep(1)

print ("The number of crashes is %s of %s"%(numberOfCrashes, num_tests))
fuzz_log.write("The number of crashes is %s of %s"%(numberOfCrashes, num_tests) + "\n")
fuzz_log.write("Ends at " + str(datetime.datetime.now()))
fuzz_log.close()
