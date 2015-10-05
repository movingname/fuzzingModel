import os
import subprocess
import signal
import time

prog = "gif2png"

prog_timeout = 15

seed_folder = "../full_seeds"
result_folder = "results/"

seeds = []


exclude_str = "pin"
def get_proc_pid(name):
	p = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if name in line and (exclude_str not in line):
			items = line.split(" ")
			for i in range(1, len(items)):
				if items[i].strip() == "":
					continue
				pid = int(items[i])
				return int(pid)
	return -1

def kill_proc_by_string(name):
	while(True):
		pid = get_proc_pid(name)
		if pid == -1:
			return
		os.kill(pid, signal.SIGINT)
		print("Kills pid " + str(pid))
		time.sleep(2)
   

# We go through the folder and get the path of all files
for root, subFolders, files in os.walk(seed_folder):
    for f in files:
        seeds.append(os.path.join(root,f))
        print(f)
        
cov_files = set()
# We go through the folder and get the path of all files
for root, subFolders, files in os.walk(result_folder):
    for f in files:
        cov_files.add(f)

pin = os.path.expanduser('~/pin/pin')
pintool = './coverage.so'

for seed in seeds:
	strs = seed.split("/")
	full_name = strs[len(strs) - 1]
	suffix = full_name[full_name.rfind(".") + 1:]
	name = full_name[:full_name.rfind(".")]
	print(name + "." + suffix)
 
	cov_file_name = name + "_" + suffix + ".dat"
  
	if cov_file_name in cov_files:
		print(cov_file_name + " already exists!")
		continue
	
	args = [pin, '-injection', 'child', '-t',  pintool, '-o',  result_folder + cov_file_name, '--', prog, "-r", "-h", "-f", "-O", seed]
	proc = subprocess.Popen(args)	
	time.sleep(prog_timeout)
	kill_proc_by_string(prog)
	