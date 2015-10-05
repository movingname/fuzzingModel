# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 10:05:09 2015

@author: rvlfl_000
"""

import codecs
import shutil

#prog = "xpdf_3.02-2"
#prog  = "gif2png"
#prog = "mp3gain"
#prog = "mp3blaster"
#prog = "jpegtran" 
prog = "eog"

seed_list_path = prog + "seeds.txt"
seed_folder = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/UbuFuzz_2013_32_" + prog + "_folder/seedfiles/examples/"
full_seed_list_path = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/UbuFuzz_2013_32_" + prog + "_folder/full_seeds/"

seed_list_file = codecs.open(seed_list_path, "r", "utf-8")

for line in seed_list_file:
    file = line.strip()
    fileName = file[file.rfind("/") +1:]
    shutil.copy(full_seed_list_path + fileName, seed_folder + fileName)

seed_list_file.close()