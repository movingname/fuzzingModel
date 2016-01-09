import codecs
import matplotlib.pyplot as plt
import numpy as np
import os
import powerlaw
from crasher_analysis import *
from lib import fit_powerlaw
from scipy.stats import pearsonr
from fuzzying_sim import *

titleDecor = {"xpdf": "", "mupdf": "", "convert": "",
              "ffmpeg": "", "autotrace": "", "gif2png": "",
              "feh": "", "mp3gain": "", "jpegtran": ""}

power_law_fit_xmin = {"xpdf": 8, "mupdf": 2, "convert": 11,
                      "ffmpeg": 11, "autotrace": 11, "jpegtran": 4}

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


def analyze_one_campaign(target, ax=None, chart="bar", alpha_cached=True):

    target_full = target
    if target == "xpdf":
        target_full = "xpdf_3.02-2"

	vm_folder = "../results/UbuFuzz_2013_32_" + target_full + "_folder/"
    # vm_folder = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/UbuFuzz_2013_32_" + target_full + "_folder/"

    bff_logs = []

    fuzz_info = {}

    # We go through the folder and get the path of all files
    for root, subFolders, files in os.walk(vm_folder + "/results"):
        for f in files:
            if "bff.log" in f:
                bff_logs.append(os.path.join(root, f))

    crash_infos = getCrashersInfo(vm_folder + "results/crashers/")

    hashes = set()
    hash_crash_runs = {}
    run_count = 0
    crash_count = 0
    bug_count = 0
    bug_count_accu = []
    seed_info = {"bugs": {}, "freq": {}}
    expCount = {}
    for exp in exps:
        expCount[exp] = 0

    for bff_log_path in sort_bff_logs(bff_logs):

        # print(bff_log_path)

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
                    bug_count_accu.append(bug_count)
                    # print(seed_file + " " + seeds + " " + seed_range)

                    if seed_file not in seed_info["freq"]:
                        seed_info["freq"][seed_file] = 0
                    seed_info["freq"][seed_file] += 1

            elif strs[1] == "uniq_crash" and strs[2] == "INFO":

                # A unique crash entry        

                crash_hash = strs[3][strs[3].find(" crash_id") + 10:strs[3].find(" seed")]
                seed_file = strs[3].split(" ")[0]

                if seed_file not in seed_info["bugs"]:
                    seed_info["bugs"][seed_file] = set()
                if crash_hash not in seed_info["bugs"][seed_file]:
                    seed_info["bugs"][seed_file].add(crash_hash)

                # if crash_hash == "df6e32f566de664a956b502f77041ccf":
                #    print("!!!!!!!!!!!!!!")

                if crash_hash not in hashes:
                    hashes.add(crash_hash)
                    hash_crash_runs[crash_hash] = []

                    expCount[crash_infos[crash_hash].exploitability] += 1

                    bug_count += 1
                    # print(crash_hash)
                else:
                    # print("WARNING: duplicated crash_hash!")
                    pass

            elif "INFO	seen in" in line:

                # A crash entry

                crash_hash = strs[1]
                # print(crash_hash + " at " + str(run_count) + " line: " + str(line_count))

                if crash_hash not in hash_crash_runs:
                    print("Warning: hash missing: " + crash_hash)
                    # if crash_hash == "df6e32f566de664a956b502f77041ccf":

                    # print(line_count)
                    # print(bff_log_path)
                    # pass
                else:

                    if run_count not in hash_crash_runs[crash_hash]:
                        hash_crash_runs[crash_hash].append(run_count)

                        crash_count += 1

                        if seed_file not in seed_info["bugs"]:
                            seed_info["bugs"][seed_file] = set()
                        if crash_hash not in seed_info["bugs"][seed_file]:
                            seed_info["bugs"][seed_file].add(crash_hash)

            line_count += 1
            # if line_count > 100:
            #    break

    # print(hash_crash_runs)

    # print("run_count = " + str(run_count))
    # print("crash_count = " + str(crash_count))
    # print("bug_count = " + str(bug_count))

    bff_log.close()

    crash_run_counts = {}
    crash_counts_sorted = []
    crash_exp_sorted = []
    crash_color_sorted = []
    for crash_hash in hash_crash_runs:
        crash_run_counts[crash_hash] = len(hash_crash_runs[crash_hash])

    bugs = []
    crash_to_id = {}
    i = 2
    for pair in sorted([(value, key) for (key, value) in crash_run_counts.items()], reverse=True):
        crash_hash = pair[1]
        crash_counts_sorted.append(crash_run_counts[crash_hash])
        crash_color_sorted.append(exp_color[crash_infos[crash_hash].exploitability])
        crash_exp_sorted.append(expToNum[crash_infos[crash_hash].exploitability])
        crash_to_id[crash_hash] = i
        bugs += [i] * pair[0]
        i += 1
    bugs += [1] * (run_count - crash_count)

    # if target == "mupdf":
    # print(bugs)

    max_crash_count = max(crash_counts_sorted)

    # print("max crash = " + str(max_crash_count))

    ###################################
    # Draw the distribution of bugs
    ###################################

    if ax is None:
        ax = plt.axes()

    pos = np.arange(len(crash_counts_sorted)) + 1
    ax.set_title(target + titleDecor[target], fontsize=14)
    ax.set_xlabel('Bugs', fontsize=12)
    ax.set_ylabel('Probability', fontsize=12)

    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    if chart == "bar":

        barlist = ax.bar(pos, np.array(crash_counts_sorted) / run_count, color='b')

        for i in range(0, len(crash_counts_sorted)):
            barlist[i].set_color(crash_color_sorted[i])

        # ax.set_xticks(pos + (width / 2))
        # ax.set_xticklabels(list(progSorted))

    elif chart == "log-log":
        ax.scatter(pos, sorted(np.array(crash_counts_sorted) / run_count, reverse=True))
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set_xlim([1, 200])
    else:
        assert False

    # plt.show()

    # alpha_2, sigma_2, C_2 = fit_powerlaw(bugs, discrete=True)

    # print("alpha_2: " + str(alpha_2))
    # print("sigma_2: " + str(sigma_2))

    # Create a list of values in the best fit line
    # fit_2_values = []
    # for i in range(1, 200):
    #   fit_2_values.append(C_2 * math.pow(i, -alpha_2))


    # Several issues:
    # - If we do not have "discrete=True", the lognormal fit seems incorrect.
    #   And the data is indeed discrete.
    # - Forcing the xmin = 1 can increase the data size and sometime makes
    #   distribution comparison more significant.

    # I tried to manually set the xmin by looking at the log-log graph.
    # However, the data size them becomes very small.
    # fit = powerlaw.Fit(sorted(crash_counts_sorted, reverse=True), discrete=True, xmin=power_law_fit_xmin[target])

    # We can also fit the raw data. However, the result does not make sense at all
    # fit = powerlaw.Fit(bugs, discrete=True, xmin=1)

    # Fit a continuous distribution
    # The power law fit is stable for some programs.
    # fit = powerlaw.Fit(crash_counts_sorted + [run_count - crash_count], xmin=1)

    # fit = powerlaw.Fit(crash_counts_sorted + [run_count - crash_count], discrete=True)
    # print(str(fit.alpha) + ", " + str(fit.sigma) + ", " + str(fit.xmin))
    # print(fit.distribution_compare('power_law', 'exponential'))
    # print(fit.distribution_compare('power_law', 'lognormal'))
    # print(fit.lognormal.parameter1)
    # print(fit.lognormal.parameter2)

    # if chart == "log-log":
    #     fit.power_law.plot_pdf(ax=ax)
    #    ax.plot(fit_2_values)

    # print(expCount)

    # Obtained using simulation with n=1000
    # prog_alpha_cached = {"xpdf": 2.43, "mupdf": 2.95, "convert": 2.38,
    #                     "ffmpeg": 2.20, "autotrace": 2.97, "jpegtran": 3.55}

    # Obtained using simulation with n=infinite
    prog_alpha_cached = {"xpdf": 2.38, "mupdf": 2.88, "convert": 2.38,
                         "ffmpeg": 2.20, "autotrace": 3.25, "jpegtran": 3.53}

    # Obtained using the discrete MLE estimator
    # I feel that this is not correct.
    # prog_alpha_cached = {"xpdf": 2.32, "mupdf": 2.39, "convert": 1.63,
    #                      "ffmpeg": 1.92, "autotrace": 2.23, "jpegtran": 2.44}

    if alpha_cached:
        fuzz_info["alpha"] = prog_alpha_cached[target]
    else:
       #fuzz_info["alpha"] = fit.alpha
        fuzz_info["alpha"] = get_alpha_sim(bug_count, run_count)
    fuzz_info["bug_count"] = bug_count
    fuzz_info["max_crash"] = max_crash_count
    fuzz_info["run_count"] = run_count
    fuzz_info["crash_count"] = crash_count

    for exp in expCount:
        # print(exp + ": " + str(expCount[exp]) + ", " + str(expCount[exp] / bug_count))
        fuzz_info[exp] = "{0:.2f}".format(expCount[exp] / bug_count)

    return [crash_counts_sorted, crash_exp_sorted], fuzz_info, bug_count_accu, seed_info


def drawCorr(corrData):
    X = []
    Y = []
    ID = []
    logX = []

    count = 1
    for i in range(0, len(corrData[0])):

        if not corrData[1][i]:
            continue

        X.append(corrData[0][i])
        logX.append(math.log(corrData[0][i]))
        Y.append(corrData[1][i])
        ID.append(count)

        count += 1

    # print(logX)
    # print(Y)
    r, p = pearsonr(logX, Y)
    print("Correlation between virility and exploitability")
    print("r = " + str(r))
    print("p = " + str(p))


def draw_freq_dists(targets, prog_fuzz_info, prog_fuzz_bug_accu, prog_seed_info):
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

            progCorrData[target], prog_fuzz_info[target], prog_fuzz_bug_accu[target], prog_seed_info[target] = analyze_one_campaign(target, ax, chart="bar")

    fig.tight_layout()

    fig.savefig("../output/distributions.pdf")

    fig = plt.figure()

    numRow = 2
    numCol = 3

    # fig, axes = plt.subplots(nrows=numRow, ncols=numCol,
    #                             sharex=False, sharey=False)

    # fig.set_size_inches(numCol * 3, numRow * 2.5)

    for i in range(0, numCol):
        for j in range(0, numRow):
            # if numRow > 1:
            #    ax = axes[j][i]
            # else:
            #    ax = axes[i]

            target = targets[j * numCol + i]

            print(target)

            drawCorr(progCorrData[target])

            # fig.tight_layout()

            # fig.savefig("expFreqCorr.pdf")

            # fig=plt.figure()

# drawResults("convert")
