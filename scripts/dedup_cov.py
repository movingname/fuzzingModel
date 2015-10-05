import os
from operator import itemgetter



cov_folder = "E:/Fuzzing/UbuFuzz_2013_32_xpdf_3.02-2_folder/pincoverage/results"

covs = []

# We go through the folder and get the path of all files
for root, subFolders, files in os.walk(cov_folder):
    for f in files:
        covs.append(os.path.join(root,f))


addr_count_total = {}

i = 0

for cov_file in covs:
    
    for line in open(cov_file):
        
        if(line.strip() == ""):
            continue              
        
        addr = int(line.split(": ")[0].strip())
        count = int(line.split(": ")[1].strip())

        if addr not in addr_count_total:
            addr_count_total[addr] = 0
        addr_count_total[addr] += 1
        
    i += 1
    if i % 100 == 0:
        print(i)
        
print("There are " + str(len(addr_count_total)) + " bbls.")

bbl_sorted = []
bbl_count_sorted = []

for pair in sorted(addr_count_total.items(), key=itemgetter(1), reverse=True):
    bbl_sorted.append(pair[0])
    bbl_count_sorted.append(pair[1])

dup_lists = []

# We create a duplicate set if there are more than dup_th bbls
# have the same count
dup_th = 5    

first_occur = 0
last_count = bbl_sorted[0]

for i in range(1, len(bbl_sorted)):
    count = bbl_count_sorted[i]
    if count != last_count:
        if i - first_occur > dup_th:
            dup_list = []
            for j in range(first_occur, i + 1):
                dup_list.append(bbl_sorted[j])
            dup_lists.append(dup_list)
        first_occur = i
        last_count = count

print(len(dup_lists))

# TODO

