# -*- coding: utf-8 -*-

import codecs
import shutil
import argparse

parser = argparse.ArgumentParser(description="Copy the selected seed files to the folder for fuzzing.")
parser.add_argument("program", help="The program to fuzz.")
parser.add_argument("seed_folder_for_fuzzing", help="The folder that contains seed files for fuzzing. Usually it is <bff folder>/seedfiles/examples/")
parser.add_argument("full_seed_folder", help="The folder that contains all seeds.  Usually it is <bff folder>/full_seeds/")
args = parser.parse_args()

prog = args.program
full_seed_list_path = args.full_seed_folder
seed_folder = args.seed_folder_for_fuzzing

# We could also hardcode these arguments...

#prog = "xpdf_3.02-2"
#prog  = "gif2png"
# prog = "a2mp3"
#prog = "mp3blaster"
#prog = "jpegtran" 
# prog = "eog"
#prog = "experiment"

seed_list_path = prog + "seeds.txt"
# seed_folder = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/UbuFuzz_2013_32_" + prog + "_folder/seedfiles/examples/"
# full_seed_list_path = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/UbuFuzz_2013_32_" + prog + "_folder/full_seeds/"

seed_list_file = codecs.open(seed_list_path, "r", "utf-8")

for line in seed_list_file:
    file = line.strip()
    fileName = file[file.rfind("/") +1:]
    shutil.copy(full_seed_list_path + fileName, seed_folder + fileName)

seed_list_file.close()

print("Done.")