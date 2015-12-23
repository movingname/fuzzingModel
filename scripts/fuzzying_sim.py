
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import powerlaw
from scipy import special

matplotlib.rc('xtick', labelsize=14) 
matplotlib.rc('ytick', labelsize=14)

progs = ["xpdf", "mupdf", "convert", "ffmpeg", "autotrace", "jpegtran"]

# These values are obtained from the fuzzing_campaign_analysis script.
prog_alpha = {"xpdf": 2.27, "mupdf": 1.98, "convert": 1.32,
              "ffmpeg": 1.66, "autotrace": 1.32, "jpegtran": 2.82}

prog_max_crash = {"xpdf": 64, "mupdf": 60, "convert": 3197,
                  "ffmpeg": 863, "autotrace": 593, "jpegtran": 30}

prog_total_crash = {"xpdf": 4065, "mupdf": 9184, "convert": 79636,
                    "ffmpeg": 3872, "autotrace": 2548, "jpegtran": 113}

prog_bug_count = {"xpdf": 34, "mupdf": 24, "convert": 134,
                  "ffmpeg": 96, "autotrace": 23, "jpegtran": 33}

prog_k = {}

# We have a discrete power law distribution.
# Given the alpha and a probability, we want to know the i
def getK(alpha, prob):

    return round(math.exp(math.log(prob * special.zeta(alpha, 1)) / -alpha))

for prog in progs:
    prog_k[prog] = getK(prog_alpha[prog], prog_max_crash[prog] / prog_total_crash[prog])
    print(prog + " k = " + str(prog_k[prog]))


def runModel(alpha, t, k):
    simDist = powerlaw.Power_Law(xmin=1, parameters=[alpha], discrete=True)
    
    simBugs = simDist.generate_random(t)
    
    D = {}
    seq = []
    
    for bug in simBugs:      
        bug = int(bug)
        
        # Filter out frequent bugs        
        if bug < k:
            continue

        if bug not in D:
            D[bug] = 0
            seq.append(bug)
        D[bug] += 1
    
    return seq


# Exp 1

def runSeqSim(n, seq_len):
    bugCount = {}
    seqs = []
    for i in range(0, 5):
        seq = runModel(prog_alpha["xpdf"], 10000, prog_k["xpdf"])
        
        _seq = []
        for bug in seq:
            if bug <= n:
                _seq.append(bug)
            if(len(_seq) >= seq_len):
                break
        
        seqs.append(_seq)
        
        for bug in _seq:
            if bug not in bugCount:
                bugCount[bug] = 0
            bugCount[bug] += 1
    
    
    for seq in seqs:
        output = ""
        for bug in seq:
            if bugCount[bug] > 1:
                output = output + " & " + str(bug)
            else:
                output = output + " & \\textbf{" + str(bug) + "}"
        print(output)
        print()


# Exp 2

def drawBHUnique():
    BHUniqueSizes = []
    BHUniqueSizes2 = []
    repeat = 30
    
    alpha2 = 2    
    
    CSizeBHUnique = [] 
    CSizeBHUnique2 = []
    CMax = 31
    
    for C in range(1, CMax):
        
        CSizeBHUnique.append([])   
        CSizeBHUnique2.append([])
        
        for i in range(0, repeat):
            seqComp = runModel(prog_alpha["xpdf"], 10000 * C, prog_k["xpdf"])
            seqBH = runModel(prog_alpha["xpdf"], 10000, prog_k["xpdf"])
            
            sizeBH = len(seqBH)
            sizeComp = len(seqComp)    
            sizeBHUnique = len(seqBH) - len(set(seqComp).intersection(seqBH))
            CSizeBHUnique[C - 1].append(sizeBHUnique)
            # print(str(sizeComp) + ", " + str(sizeBH) + ", " + str(sizeBHUnique)) 

            # Should be merged:
            seqComp = runModel(alpha2, 10000 * C, prog_k["xpdf"])
            seqBH = runModel(alpha2, 10000, prog_k["xpdf"])
            
            sizeBH = len(seqBH)
            sizeComp = len(seqComp)    
            sizeBHUnique = len(seqBH) - len(set(seqComp).intersection(seqBH))
            CSizeBHUnique2[C - 1].append(sizeBHUnique)

    
    stdList = []
    stdList2 = []
    for C in range(1, CMax):
        BHUniqueSizes.append(np.mean(CSizeBHUnique[C - 1]))
        stdList.append(np.std(CSizeBHUnique[C - 1]))
        BHUniqueSizes2.append(np.mean(CSizeBHUnique2[C - 1]))
        stdList2.append(np.std(CSizeBHUnique2[C - 1]))    

    fontSize = 18
    figWidth = 7
    figHeight = 5
    
    fig = plt.figure()
    
    ax = fig.add_subplot(111)
    
    ax.set_xlabel('Defender Resource Advantage (A)', fontsize=fontSize)
    ax.set_ylabel('# Unique Bugs by the B. H.', fontsize=fontSize)
    
    eb = plt.errorbar(np.arange(len(BHUniqueSizes2)) + 1, BHUniqueSizes2, yerr=stdList2, errorevery=3, label=r"$\alpha$ = 2")
    eb[-1][0].set_linestyle('--')
    
    eb = plt.errorbar(np.arange(len(BHUniqueSizes)) + 1, BHUniqueSizes, yerr=stdList, errorevery=3, label=r"$\alpha$ = 2.27")
    eb[-1][0].set_linestyle('--')

    ax.legend(loc=1)
    
    ax.set_ylim([0, ax.get_ylim()[1]])
    
    fig.tight_layout()
    
    fig.savefig("../output/bhUnique.pdf")


def expected_find(n, t, alpha, k):
        
    sumP = 0    
    
    denom = special.zeta(alpha, 1)
        
    for i in range(k, n):
        sumP += math.exp(- math.pow(i, -alpha) / denom * t)

    return n - sumP - k       


def drawExpectedFind(alpha, discovered, n_list, step, runs):
    fig = plt.figure()
    
    ax = fig.add_subplot(111)
    
    ax.set_xlabel('t (Fuzzing Runs)', fontsize=14)
    ax.set_ylabel('Exp. Bugs', fontsize=14)
    
    for n in n_list:
        expected_bugs = []
        
        for t in range(0, runs, step): 
            expected_bugs.append(int(round(expected_find(n, t, alpha, discovered))))
            
        plt.plot(np.arange(len(expected_bugs)) + 1, expected_bugs, label="n=" + str(n))

    #expected_bugs = []
    #for t in range(100, 100000, 100): 
    #    expected_bugs.append(int(round(expected_find(222, t, 2, discovered))))
            
    #plt.plot(np.arange(len(expected_bugs)) + 1, expected_bugs, label="n=" + str(n) + ", alpha=2")
        
    ax.set_ylim([0, ax.get_ylim()[1]])
    ax.legend(loc=2)
    
    fig.tight_layout()
    
    fig.savefig("../output/expectedBugs.pdf")


def getExpTimeSingle(alpha, i):
    
    print(1 / (math.pow(i, -alpha) / special.zeta(alpha, 1)) )

#getExpTimeSingle(1.26, 7)
#getExpTimeSingle(1.26, 8)
#getExpTimeSingle(1.26, 10000)
#getExpTimeSingle(1.26, 100000)
#getExpTimeSingle(1.26, 1000000)


# We need to manually select the upper and lower bound.
# We should see the diff changes from positive to negative.  
def estN(t, d, k, alpha, low, up):
    
    minDiff = None 
    opN = None
    
    seePos = False
    seeNeg = False

    for n in range(low, up, 1):
        
        _d = expected_find(n, t, alpha, k)
        # print(_d)
        diff = d - _d
        
        if diff > 0:
            seePos = True
        if diff < 0:
            seeNeg = True
            
        diff = abs(diff)
        
        if minDiff is None or diff < minDiff:
            minDiff = diff
            opN = n
        # if n % 10 == 0:
        #    print(str(n) + ", " + str(d - _d))

    assert seePos and seeNeg
    
    print("opN = " + str(opN))
    print("minDiff = " + str(minDiff))
    return opN

estN(prog_total_crash["xpdf"], prog_bug_count["xpdf"], prog_k["xpdf"], prog_alpha["xpdf"], 30, 1000)
estN(prog_total_crash["mupdf"], prog_bug_count["mupdf"], prog_k["mupdf"], prog_alpha["mupdf"], 20, 400)
estN(prog_total_crash["convert"], prog_bug_count["convert"], prog_k["convert"], prog_alpha["convert"], 100, 1000)
estN(prog_total_crash["ffmpeg"], prog_bug_count["ffmpeg"], prog_k["ffmpeg"], prog_alpha["ffmpeg"], 30, 1000)
estN(prog_total_crash["autotrace"], prog_bug_count["autotrace"], prog_k["autotrace"], prog_alpha["autotrace"], 20, 1000)
estN(prog_total_crash["jpegtran"], prog_bug_count["jpegtran"], prog_k["jpegtran"], prog_alpha["jpegtran"], 10, 1000)

drawBHUnique()

print(expected_find(1000, 1000, 1.8, 100))
print(expected_find(10000, 1000, 1.8, 100))
print(expected_find(100000, 1000, 1.8, 100))

# These are the same
print(special.zeta(1.26, 1))
print(special.zetac(1.26) + 1)

# We simulate 5 different discovery sequences of fuzzing the same program.
runSeqSim(222, 15)

drawExpectedFind(prog_alpha["xpdf"], prog_k["xpdf"], [42,52,62], 1, 10000)