
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import powerlaw
from scipy import special

matplotlib.rc('xtick', labelsize=14) 
matplotlib.rc('ytick', labelsize=14)




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

def runSeqSim(n, seq_len, fuzz_info):
    bugCount = {}
    seqs = []
    for i in range(0, 5):
        seq = runModel(fuzz_info["alpha"], 10000, fuzz_info["k"])
        
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

def drawBHUnique(fuzz_info):
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
            seqComp = runModel(fuzz_info["alpha"], 10000 * C, fuzz_info["k"])
            seqBH = runModel(fuzz_info["alpha"], 10000, fuzz_info["k"])
            
            sizeBH = len(seqBH)
            sizeComp = len(seqComp)    
            sizeBHUnique = len(seqBH) - len(set(seqComp).intersection(seqBH))
            CSizeBHUnique[C - 1].append(sizeBHUnique)
            # print(str(sizeComp) + ", " + str(sizeBH) + ", " + str(sizeBHUnique)) 

            # Should be merged:
            seqComp = runModel(alpha2, 10000 * C, fuzz_info["k"])
            seqBH = runModel(alpha2, 10000, fuzz_info["k"])
            
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


# We have a discrete power law distribution.
# Given the alpha and a probability, we want to know the i
def getK(alpha, prob):
    return round(math.exp(math.log(prob * special.zeta(alpha, 1)) / -alpha))


# We need to manually select the upper and lower bound.
# We should see the diff changes from positive to negative.  
def estN(fuzz_info, low, up):

    t = fuzz_info["run_count"]
    alpha = fuzz_info["alpha"]
    k = fuzz_info["k"]
    d = fuzz_info["bug_count"]

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
