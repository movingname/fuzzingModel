import codecs
import matplotlib.pyplot as plt
import numpy as np 
import os
import powerlaw

from crasher_analysis import *
from lib import fit_powerlaw
from scipy.stats import pearsonr

titleDecor = {"xpdf_3.02-2": "", "mupdf": "", "convert": "",
              "ffmpeg": "", "autotrace": "", "gif2png": "",
              "feh": "", "mp3gain": "", "jpegtran": ""}


def sort_bff_logs(bff_logs):
    
    sorted_logs = []
    
    num = len(bff_logs)
    
    for i in range(0, num):
        sorted_logs.append("")
        
    for log in bff_logs:
        log = log.strip()
        if log.endswith(".log"):
            sorted_logs[num - 1] = log
        else:
            i = int(log[log.rfind(".") + 1:])
            sorted_logs[num - i - 1] = log
    return sorted_logs


def analyze_one_campaign(target, ax=None):

    vm_folder = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/UbuFuzz_2013_32_" + target + "_folder/"
    
    bff_logs = []

    fuzz_info = {}
    
    # We go through the folder and get the path of all files
    for root, subFolders, files in os.walk(vm_folder + "/results"):
        for f in files:
            if "bff.log" in f:
                bff_logs.append(os.path.join(root,f))
            
    crash_infos = getCrashersInfo(vm_folder + "results/crashers/")
        
    hashes = set()
    hash_crash_runs = {}
    run_count = 0
    crash_count = 0
    bug_count = 0
    expCount = {}
    for exp in exps:
        expCount[exp] = 0
    
    for bff_log_path in sort_bff_logs(bff_logs):
    
        #print(bff_log_path)
    
        bff_log = open(bff_log_path, "r")
        
        line_count = 0
        
        for line in bff_log:
            strs = line.split("\t")
            if strs[1] == "bff" and strs[2] == "INFO":
                
                # A fuzzing run entry        
                
                if strs[3].startswith("Fuzzing"): 
                    _strs = strs[3].split(" ")
                    seed_file = _strs[1][_strs[1].rfind("/") + 1:]
                    seeds = _strs[2][_strs[2].rfind("=") + 1:]
                    seed_range = _strs[3][_strs[3].rfind("=") + 1:]
                    run_count += 1
                    #print(seed_file + " " + seeds + " " + seed_range)
            elif strs[1] == "uniq_crash" and strs[2] == "INFO": 
                
                # A unique crash entry        
                
                crash_hash = strs[3][strs[3].find(" crash_id") + 10:strs[3].find(" seed")]
                
                #if crash_hash == "df6e32f566de664a956b502f77041ccf":
                #    print("!!!!!!!!!!!!!!")
                
                if crash_hash not in hashes:
                    hashes.add(crash_hash)
                    hash_crash_runs[crash_hash] = []

                    expCount[crash_infos[crash_hash].exploitability] += 1
                    
                    bug_count += 1
                    #print(crash_hash)
                else:            
                    #print("WARNING: duplicated crash_hash!")
                    pass
            elif "INFO	seen in" in line:
                
                # A crash entry
        
                crash_hash = strs[1]
                #print(crash_hash + " at " + str(run_count) + " line: " + str(line_count))
            
                if crash_hash not in hash_crash_runs:
                    print("Warning: hash missing: " + crash_hash)
                    #if crash_hash == "df6e32f566de664a956b502f77041ccf":
                    
                        #print(line_count)
                        #print(bff_log_path)
                    #pass
                else:
            
                    if run_count not in hash_crash_runs[crash_hash]:
                        hash_crash_runs[crash_hash].append(run_count)
                        
                        crash_count += 1
                    
            line_count += 1
            #if line_count > 100:
            #    break
    
    #print(hash_crash_runs)
    
    print("run_count = " + str(run_count))
    print("crash_count = " + str(crash_count))
    print("bug_count = " + str(bug_count))

    bff_log.close()
    
    crash_run_counts = {}
    crash_counts_sorted = []
    crash_exp_sorted = []
    crash_color_sorted = []
    for crash_hash in hash_crash_runs:
        crash_run_counts[crash_hash] = len(hash_crash_runs[crash_hash])
        
    for pair in sorted([(value,key) for (key,value) in crash_run_counts.items()], reverse = True):
        crash_counts_sorted.append(crash_run_counts[pair[1]])
        crash_color_sorted.append(exp_color[crash_infos[pair[1]].exploitability])
        crash_exp_sorted.append(expToNum[crash_infos[pair[1]].exploitability])

    max_crash_count = max(crash_counts_sorted)

    print("max crash = " + str(max_crash_count))

    ###################################
    # Draw the distribution of bugs
    ###################################
    
    if ax is None:
        ax = plt.axes()
    
    pos = np.arange(len(crash_counts_sorted))
    #width = 1.0

    #ax.set_xticks(pos + (width / 2))
    #ax.set_xticklabels(list(progSorted))
    
    ax.set_xlabel('Bugs', fontsize=14)
    ax.set_ylabel('Frequency', fontsize=14)
    
    ax.set_title(target + titleDecor[target], fontsize=14)    
    
    barlist = ax.bar(pos, sorted(crash_counts_sorted, reverse=True), color='b')
    
    for i in range(0, len(crash_counts_sorted)):
        barlist[i].set_color(crash_color_sorted[i])

    #plt.show()
    
    fit_powerlaw(sorted(crash_counts_sorted, reverse=True))

    # Several issues:
    # - If we do not have "discrete=True", the lognormal fit seems incorrect.
    #   And the data is indeed discrete.
    # - Forcing the xmin = 1 can increase the data size and sometime makes
    #   distribution comparison more significant.
    
    fit = powerlaw.Fit(sorted(crash_counts_sorted, reverse=True), discrete=True, xmin=1.0)
    print(str(fit.alpha) + ", " + str(fit.sigma) + ", " + str(fit.xmin))
    print(fit.distribution_compare('power_law', 'exponential'))
    print(fit.distribution_compare('power_law', 'lognormal'))
    print(fit.lognormal.parameter1)
    print(fit.lognormal.parameter2)

    #print(expCount)
    for exp in expCount:
        print(exp + ": " + str(expCount[exp]) + ", " + str(expCount[exp] / bug_count))

    fuzz_info["alpha"] = fit.alpha
    fuzz_info["bug_count"] = bug_count
    fuzz_info["max_crash"] = max_crash_count
    fuzz_info["run_count"] = run_count
    fuzz_info["crash_count"] = crash_count

    return [crash_counts_sorted, crash_exp_sorted], fuzz_info


def drawCorr(corrData):
    
    X = []
    Y = []
    ID = []
    logX = []
    
    count = 1
    for i in range(0, len(corrData[0])):
        
        if corrData[1][i] == None:
            continue
        
        X.append(corrData[0][i])
        logX.append(math.log(corrData[0][i]))
        Y.append(corrData[1][i])
        ID.append(count)
        
        count += 1
    
    #print(logX)
    #print(Y)
    r,p = pearsonr(logX, Y)
    print("Correlation between expected reward and bug number")
    print("r = " + str(r))
    print("p = " + str(p))


def draw_freq_dists(targets, prog_fuzz_info):
    # Draw n * 3 figures
    
    numRow = 2
    numCol = 3
    
    fig, axes = plt.subplots(nrows=numRow, ncols=numCol, 
                             sharex=False, sharey=False)
    
    progCorrData = {}    
    
    fig.set_size_inches(numCol * 3, numRow * 2.5)
    
    for i in range(0, numCol):
        for j in range(0, numRow):
            if numRow > 1:
                ax = axes[j][i]
            else:
                ax = axes[i]
            
            target = targets[j * numCol + i]

            print(target)
            
            progCorrData[target], prog_fuzz_info[target] = analyze_one_campaign(target, ax)
            
    fig.tight_layout()
    
    fig.savefig("../output/distributions.pdf")



    fig=plt.figure()

    numRow = 1
    numCol = 3

    #fig, axes = plt.subplots(nrows=numRow, ncols=numCol,
#                             sharex=False, sharey=False)

    #fig.set_size_inches(numCol * 3, numRow * 2.5)
    
    for i in range(0, numCol):
        for j in range(0, numRow):
            #if numRow > 1:
            #    ax = axes[j][i]
            #else:
            #    ax = axes[i]
            
            target = targets[j * numCol + i]

            print(target)
            
            drawCorr(progCorrData[target])
            
    #fig.tight_layout()
    
    #fig.savefig("expFreqCorr.pdf")       
       
    #fig=plt.figure()

#drawResults("convert")


