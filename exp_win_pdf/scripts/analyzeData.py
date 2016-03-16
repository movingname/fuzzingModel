

import codecs
import math
import matplotlib.pyplot as plt
import numpy as np 
from scipy import stats
from scipy.stats import expon

#from scipy.stats import powerlaw

import powerlaw

log = codecs.open("..\data\log_combine.txt", "r", "utf-8")

summary = open("..\data\summary.txt", "r")

fileID = -1
bugID = -1

fileStackHash = []
hashBugID = {}
stackHashes = []

severity = None
title = None
stackHash = None

bugSeverity = []
bugTitle = []
bugFreq = []

# WARNING: we assume that eip is unique.
#          I think using stack hash would be more reliable.

for line in summary:
    if "File Name: " in line:
        fileID += 1
    if "WARNING: " in line:
        fileStackHash.append(None)
        print("WARNING found! So one file's bug cannot be determined.")
    elif "Exploitability Classification: " in line:
        severity = line[len("Exploitability Classification: "):]       
    elif "Recommended Bug Title: " in line:
        title = line[len("Recommended Bug Title: "):] 
    elif "md5: " in line:
        stackHash = line.split(" ")[1]
        fileStackHash.append(stackHash)
        if not stackHash in stackHashes:
            stackHashes.append(stackHash)
            bugID += 1
            bugSeverity.append(severity)
            bugTitle.append(title)
            bugFreq.append(0)
            #print(title)
            #print(stackHash)
            hashBugID[stackHash] = bugID    
        bugFreq[hashBugID[stackHash]] += 1

print("Crash file number " + str(fileID + 1))
print("Unique bug numbers " + str(bugID + 1))
print("Unique stack hash numbers " + str(len(stackHashes)))

ax = plt.axes()

pos = np.arange(len(bugFreq))
width = 1.0

ax = plt.axes()
#ax.set_xticks(pos + (width / 2))
#ax.set_xticklabels(list(progSorted))

plt.xlabel('Bugs', fontsize=14)
plt.ylabel('Count', fontsize=14)

plt.bar(pos, sorted(bugFreq, reverse=True), width, color='b')
plt.show()

print("Comments: This chart shows some characteristics of every bug.")
print("Particularly, it represents how easy they can be triggered by random inputs.")
print("The distribution seems to follow power law.")
print("So it shows that a few bugs are easy to trigger while most are hard to trigger.")





crashID = -1

lineCount = 0

numUniqueBug = 0

crashInterval = 0

crashIntervals = []

timeBinSize = 100

accuBugTimeline = []

bugTimeline = []

nonuniqueBugTimeline = []

bugs = []

for line in log:
    
    lineCount += 1    
    if (lineCount - 1) % 100 == 0:
        accuBugTimeline.append(0)
        if len(accuBugTimeline) >= 2:
            accuBugTimeline[len(accuBugTimeline) - 1] = accuBugTimeline[len(accuBugTimeline) - 2]
        bugTimeline.append(0)
        nonuniqueBugTimeline.append(0)
    
    if "crashed application" in str(line):
        #print(line)        
        crashID += 1
        
        fileHash = fileStackHash[crashID]
        if fileHash == None:
            continue
        
        bug = hashBugID[fileHash]
        if not bug in bugs:
            bugs.append(bug)
            accuBugTimeline[len(accuBugTimeline) - 1] += 1
            bugTimeline[len(bugTimeline) - 1] += 1
        
        nonuniqueBugTimeline[len(nonuniqueBugTimeline) - 1] += 1        
        
        crashIntervals.append(crashInterval)
        crashInterval = -1
    crashInterval += 1

print("Test number: " + str(lineCount))

print("Crash number: " + str(crashID + 1))

ax = plt.axes()

plt.xlabel('Time (* 100)', fontsize=14)
plt.ylabel('Count', fontsize=14)

plt.plot(bugTimeline, '-o')

plt.show()

ax = plt.axes()

plt.xlabel('Time (* 100)', fontsize=14)
plt.ylabel('Accumulative Count', fontsize=14)

plt.plot(accuBugTimeline, '-o')

plt.show()

ax = plt.axes()

plt.xlabel('Time (* 100)', fontsize=14)
plt.ylabel('Count', fontsize=14)

plt.plot(nonuniqueBugTimeline, '-o')

plt.show()

print("This graph should show crashes are evenly distributed overtime.")
print("If not, it means that there are some biases in our experiment.")
print("The current result looks ok, although it seems you have more in the beginning.")
print("Do you have ways of testing this hypothesis?")
#print(crashIntervals)


# Array Creation
# http://docs.scipy.org/doc/numpy/user/basics.creation.html
data = np.array(crashIntervals)

#print(sorted(data, reverse=True))


# We now try to fit an exponential distribution to the data.

# This will print detailed information of this function!
# print(expon.fit.__doc__)


# http://stackoverflow.com/questions/21610034/fitting-distribution-with-fixed-parameters-in-scipy/
# http://stackoverflow.com/questions/25085200/scipy-stats-expon-fit-with-no-location-parameter

loc, scale = expon.fit(data, floc=0)

print(loc)

print(scale)



# Now, we want to test how well the exponential distribution 
# fits to the data.

# TODO: study more on the kstest
#       try examples in the doc
#       read Wiki page
#       http://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test
#       also some related posts
#       http://stats.stackexchange.com/questions/110272/a-naive-question-about-the-kolmogorov-smirnov-test

# print(stats.kstest.__doc__)



d, p = stats.kstest(data, 'expon')

print("D = " + str(d) + ", p-value = " + str(p))


fig, ax = plt.subplots()

ax.hist(crashIntervals, bins=10)
plt.title("Histogram")
plt.xlabel("Interval")
plt.ylabel("Frequency")


# We draw an exponential pdf in the figure.
# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.expon.html

x = np.linspace(0, 1800, 20)

# This 6500 is manually tuned. We should have an automatic normalization.
# TODO: http://scikit-learn.org/stable/modules/preprocessing.html

y = expon.pdf(x, 0, scale) * 6500

ax.plot(x, y, 'r-', lw=5, alpha=0.6, label='expon pdf')

plt.show()

log.close()






print("We now do some theoretical analysis.")


# The power law distribution in Python
# https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.stats.powerlaw.html

k = 100

#print(dir(powerlaw.Distribution))

#print(dir(powerlaw))

dist = powerlaw.Power_Law(parameters = [2])

lambdas = dist.generate_random(k)

for i in range(0, k):
    lambdas[i] = (lambdas[i] - 1) / 350000

    
# print(sorted(lambdas))

# Plot the power law we generated
fig, ax = plt.subplots()

ax.plot(sorted(lambdas, reverse=True))

plt.title("Distribution of simulated lambdas")
plt.xlabel("Lambdas")
plt.ylabel("Value")

plt.show()

# Plot a simulated exponential distribution
#fig, ax = plt.subplots()

#ax.plot(sorted(np.random.exponential(scale = 10, size=100), reverse=True))

#plt.show()

discoverTimes = []

for i in range(0,k):
    discoverTimes.append(np.random.exponential(scale = 1 / lambdas[i]))

#print(sorted(discoverTimes))

# Plot the simulated discovery times
fig, ax = plt.subplots()

ax.plot(sorted(discoverTimes, reverse=True))

plt.title("Simulated Vulnerability Discovery Times")
plt.xlabel("Vulnerabilities")
plt.ylabel("Discovery Time")

plt.show()


fuzzTime = 17300


#TODO: this is probably wrong.
# We should use 1 / lambda as the expected discovery time.

simulatedFreq = []

for i in range(0,k):
    if discoverTimes[i] <= fuzzTime:
        simulatedFreq.append(math.ceil(fuzzTime * lambdas[i]))

print(simulatedFreq)

ax = plt.axes()

pos = np.arange(len(simulatedFreq))
width = 1.0

plt.title("Simulated Bug Freq Distribution")
plt.xlabel('Bugs', fontsize=14)
plt.ylabel('Count', fontsize=14)

plt.bar(pos, sorted(simulatedFreq, reverse=True), width, color='b')

plt.show()


fuzzGain = []
step = 1000
longestBug = max(discoverTimes)

stepNum = int(longestBug / step)

for i in range(0, stepNum):
    fuzzGain.append(0)
    
for time in discoverTimes:
    for i in range(int(time / step), stepNum):
        fuzzGain[i] += 1

fig, ax = plt.subplots()

ax.plot(fuzzGain)

plt.title("Fuzz Gain Overtime")
plt.xlabel("Time Spent")
plt.ylabel("Vul. discovered")

plt.show()