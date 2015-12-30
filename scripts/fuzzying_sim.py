
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import powerlaw
from scipy import special

matplotlib.rc('xtick', labelsize=12)
matplotlib.rc('ytick', labelsize=12)


def expected_find(n, t, alpha):

    sumP = 0

    denom = special.zeta(alpha, 1)

    for i in range(2, n):
        sumP += math.exp(- math.pow(i, -alpha) / denom * t)

    return int(round(n - sumP - 1))


def expected_find_sim(n, t, alpha, k=2):

    dist = powerlaw.Power_Law(xmin=1, parameters=[alpha], discrete=True)

    bugs = set()

    # generate t bugs
    _bugs = dist.generate_random(t)

    bugs_accu = []
    seq = []

    for bug in _bugs:

        bug = int(bug)

        # Here, we skip bug = 1 because we use that to represent nothing happened in a fuzzing run
        if (n is not None and bug > n) or bug < k:
            bugs_accu.append(len(bugs))
            continue

        if bug not in bugs:
            seq.append(bug)

        bugs.add(bug)
        bugs_accu.append(len(bugs))

    return bugs, bugs_accu, seq


def get_alpha_sim(bug_count, t):

    alpha_min = 1.2
    alpha_max = 4
    alpha = alpha_min
    op_alpha = None
    step = 0.01
    min_diff = 1000000

    while alpha < alpha_max:
        results = []
        for i in range(0, 10):
            bugs, bugs_accu, seq = expected_find_sim(None, t, alpha)
            results.append(len(bugs))
        _diff = bug_count - np.mean(results)
        diff = abs(_diff)
        if diff < min_diff:
            min_diff = diff
            op_alpha = alpha

        alpha += step

    print(op_alpha)
    if math.isclose(op_alpha, alpha_min, rel_tol=1e-6) or math.isclose(op_alpha, alpha_max, rel_tol=1e-6):
        print("WARNING: the range of alpha might not be enough for the fitting.")
    return op_alpha


# def runModel(alpha, t, k):
#    simDist = powerlaw.Power_Law(xmin=1, parameters=[alpha], discrete=True)
    
#    simBugs = simDist.generate_random(t)
    
#    D = {}
#    seq = []
    
#    for bug in simBugs:
#        bug = int(bug)
        
        # Filter out frequent bugs        
#        if bug < k:
#            continue

#        if bug not in D:
#            D[bug] = 0
#            seq.append(bug)
#        D[bug] += 1
    
#    return seq


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



