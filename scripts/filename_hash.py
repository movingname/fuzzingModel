# -*- coding: utf-8 -*-

import hashlib

import codecs
import shutil
import os

folder = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/Seeds/mp3/"
folder_dst = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/UbuFuzz_2013_32_mp3blaster_folder/full_seeds/"

seeds = []

# We go through the folder and get the path of all files
for root, subFolders, files in os.walk(folder):
    for f in files:
        seeds.append(os.path.join(root,f))
        
for file in seeds:
    fileName = file[file.rfind("/") +1:]
    suffix = fileName[-4:]
    shutil.copy(folder + fileName, folder_dst + hashlib.sha224(fileName.encode('utf-8')).hexdigest() + suffix)