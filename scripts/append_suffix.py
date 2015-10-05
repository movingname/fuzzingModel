# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 10:15:37 2015

@author: rvlfl_000
"""

import codecs
import shutil
import os

suffix = ".gif"

folder = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/UbuFuzz_2013_32_gif2png_folder/full_seeds/"

seeds = []

# We go through the folder and get the path of all files
for root, subFolders, files in os.walk(folder):
    for f in files:
        seeds.append(os.path.join(root,f))
        
for file in seeds:
    if file.endswith(suffix):
        continue
    shutil.copy(file, file + suffix)