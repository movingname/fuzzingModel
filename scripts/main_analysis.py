
import math
from scipy import special

from fuzzing_campaign_analysis import *
from fuzzying_sim import *


progs = ["xpdf_3.02-2", "mupdf", "convert", "ffmpeg", "autotrace", "jpegtran"]

prog_fuzz_info = {}

fuzz_info_list = ["alpha", "run_count", "max_crash", "crash_count", "bug_count", "k"]

for prog in progs:
    prog_fuzz_info[prog] = {}

draw_freq_dists(progs, prog_fuzz_info)

for prog in progs:
    k = getK(prog_fuzz_info[prog]["alpha"], prog_fuzz_info[prog]["max_crash"] / prog_fuzz_info[prog]["run_count"])
    prog_fuzz_info[prog]["k"] = k
    print(prog + " k = " + str(k))


estN(prog_fuzz_info["xpdf_3.02-2"], 30, 1000)
estN(prog_fuzz_info["mupdf"], 20, 400)
estN(prog_fuzz_info["convert"], 100, 1000)
estN(prog_fuzz_info["ffmpeg"], 30, 1000)
estN(prog_fuzz_info["autotrace"], 20, 1000)
estN(prog_fuzz_info["jpegtran"], 10, 1000)

drawBHUnique(prog_fuzz_info["xpdf_3.02-2"])

print(expected_find(1000, 1000, 1.8, 100))
print(expected_find(10000, 1000, 1.8, 100))
print(expected_find(100000, 1000, 1.8, 100))

# These are the same
print(special.zeta(1.26, 1))
print(special.zetac(1.26) + 1)

# We simulate 5 different discovery sequences of fuzzing the same program.
runSeqSim(222, 15, prog_fuzz_info["xpdf_3.02-2"])

drawExpectedFind(prog_fuzz_info["xpdf_3.02-2"]["alpha"], prog_fuzz_info["xpdf_3.02-2"]["k"], [42, 52, 62], 1, 10000)