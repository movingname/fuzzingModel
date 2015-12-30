
import codecs
import matplotlib.pyplot as plt
import numpy as np 
import os
import math

exps = {"EXPLOITABLE", "PROBABLY_EXPLOITABLE", "PROBABLY_NOT_EXPLOITABLE",
        "NOT_EXPLOITABLE", "UNKNOWN"}

exp_color = {"EXPLOITABLE": "red",
             "PROBABLY_EXPLOITABLE": "blue",
             "PROBABLY_NOT_EXPLOITABLE": "yellow",
             "NOT_EXPLOITABLE": "green",
             "UNKNOWN": "grey"}

expToNum = {"EXPLOITABLE": 3,
             "PROBABLY_EXPLOITABLE": 2,
             "PROBABLY_NOT_EXPLOITABLE": 1,
             "NOT_EXPLOITABLE": 0,
             "UNKNOWN": None}


class Bug(object):

    count = 0

    def __init__(self, _id, exploitability, crasher):
        
        # One can use hash or ip to identify a vulnerability.
        # It seems that the hash is unique for every crash,
        # so we use ip now.
        self.id = _id
        self.exploitability = exploitability
        self.crasher = crasher


def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))


def getCrashersInfo(crashers_folder):
    crashers = sorted_ls(crashers_folder)
    
    bugs = {}
    
    for crasher in crashers:
        crasher_folder = crashers_folder + crasher + "/"
        crasher_files = os.listdir(crasher_folder)
        gdb_file = ""
        log_file = ""
        _hash = None
        for file in crasher_files:
            if file.endswith(".gdb"):
                gdb_file = crasher_folder + file
            elif file.endswith(".log"):
                log_file = crasher_folder + file
        if gdb_file == "":
            print("WARNING: gdb file not found")
            continue
        assert log_file != ""
        
        line_count = 0
        
        # print(gdb_file)

        for line in codecs.open(gdb_file, "r", "utf-8"):
    
            line_count += 1        
            
            if line_count == 3:
                location = line.strip()
            elif line.startswith("Hash: "):
                # This hash seems useless
                _hash = line.strip().split(": ")[1]
                #print(_hash)
                    
            elif line.startswith("Exploitability Classification: "):
                exploitability = line.strip().split(": ")[1]
    
        for line in codecs.open(log_file, "r", "utf-8"):
            if line.startswith("PC="):
                pc = line.strip().split("=")[1]
    
        bugs[crasher] = Bug(crasher, exploitability, crasher)
        
    return bugs        









