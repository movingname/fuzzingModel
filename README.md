# Empirical Analysis and Modeling of Black-Box Mutational Fuzzing

This repository contains data and scripts for the work Empirical Analysis and Modeling of Black-Box Mutational Fuzzing. 

To reproduce our analysis, please follow the steps described Section 1 and 2.
To redo the fuzzing, please follow the steps in Section 3. **Notice**: We do not share seed files directly, 
because (1) the size of the seed collection is too large (10GB+), (2) we have used some PDF seed files containing some 
private information, and (3) some seed files collected from the search engines might be associated with copyright that 
prevents sharing. However, we list the sources of seed files and tools we used in Section 3.1.
Some seed files can be directly downloaded from websites, while others need to be collected from search engines such as Bing
and Google.

Please email us (muz127@ist.psu.edu) for any question. Thank you!

## 1. Data

The fuzzing campaign data for analysis is contained in fuzzing_logs/results.zip. We have pruned out some large and unnecessary files.
Please unzip the content to the fuzzing_logs/ folder.

## 2. Analysis

The scripts/ folder has all scripts used for data analysis. Among these scripts, the Jupyter notebook (IPython notebook) 
**main_analysis.ipynb** contains all results presented in Section 4, 5 and 6 of the paper. 
**You could directly view the notebook on Github**. 

To run the notebook locally, please first install the following packages:

(1) Python 3

A simple way to set up the environment is to install Anaconda. By doing this, you can skip (2) and (3).
	
https://www.continuum.io/downloads

(2) The latest Jupyter Notebook

http://jupyter.org/
  
(3) Some common data analysis packages such as matplotlib, scipy, etc. 

(4) The powerlaw package

https://pypi.python.org/pypi/powerlaw

Then launch Jupyter notebook and play with the main_analysis.ipynb.
	
## 3. Fuzzing

Below, we list all steps of our fuzzing experiment, from seed collection to running fuzzing.

### 3.1 Prepare the Fuzzing Environment

(1) Download the VM image of BFF 2.7 and follow the installation guide.

https://www.cert.org/vulnerability-analysis/tools/bff.cfm

(2) After launching the VM, install the target application using apt-get. We list program version numbers in the paper.

(3) Install the pincoverage tool we wrote. First, copy pincoverage/ to the bff shared folder.
Then on the guest OS 

	cd pincoverage/
    python make.py

### 3.2 Seed Collection

Here are the sources and tools we used for each type of seed files.

**Video**:

samples.mplayerhq.hu

**PDF**:

Bing, Google

https://github.com/veraPDF/veraPDF-corpus

http://www.pdfa.org/2011/08/isartor-test-suite/

**MP3**:

Bing. We use [GoogleScraper](https://github.com/NikolaiT/GoogleScraper)

    GoogleScraper -s "bing" -q "filetype:mp3" -p 100

**PNG**:

http://www.schaik.com/pngsuite/

https://code.google.com/p/imagetestsuite/wiki/PNGTestSuite

**GIF**:

https://github.com/dvyukov/go-fuzz/tree/master/examples/gif/corpus

https://code.google.com/p/imagetestsuite/downloads/list

Google Image Downloader

**JPEG**:

https://code.google.com/p/imagetestsuite/downloads/detail?name=imagetestsuite-jpg-1.00.tar.gz&amp;can=2&amp;q=

Google Image Downloader

**Bitmap**:

http://bmptestsuite.sourceforge.net/

### 3.3 Collect and Analyze Coverage Data

(1) Copy all seed files for a target program into bff/full_seeds.

(2) In pincoverage/collect_cov.py, find the following line:

	args = [pin, '-injection', 'child', '-t',  pintool, '-o',  result_folder + cov_file_name, '--', prog, "-r", "-h", "-f", "-O", seed]

and replace items after '--' with the right command. Please see the last section for all commands.
	
(3) Start code coverage data collection (on the guest OS):

    python pincoverage/collect_cov.py

(4) Use the greedy algorithm to select seeds (on the host OS):

    python scripts/analyze_cov.py
	
(5) Copy selected seeds to the fuzzing folder (on the host OS):

    python copy_seeds.py

	
### 3.4 Run Fuzzing

**More information can be find in the README file of BFF.**

(1) Increase the maximum number of backup logs. In bff.py, find the following line:

    # set up remote logging
    setup_logfile(cfg.output_dir, log_basename='bff.log', level=logging.INFO,
                  max_bytes=1e7, backup_count=5)
				  
Update the backup_count to 500.

(2) To clear up all previous fuzzing campagin records:

    ./reset_bff.sh --remove-results

You will receive an error message if no previous records exist. This is fine.
	
(3) Tell BFF the command used in fuzzing. In conf.d/bff.cg, update the following lines:

cmdline=[The command]

killprocname=[name of the target program]

We list all commands in the last section of this file.

(4) Run a fuzzing campagin:

    ./batch.sh

This executes forever so please stop at some point. Also, the fuzzing campagin can be resumed after a stop.

(5) Copy the UbuFuzz_* folder to fuzzing_logs/. To save space, please only keep UbuFuzz_*/results/.

(6) Analyze the fuzzing campagin data described in Section 2.

## 4. Commands Used for Fuzzing Programs:

autotrace:

    autotrace $SEEDFILE > test.pdf

convert:

    ~/convert $SEEDFILE /dev/null

feh: 

    feh $SEEDFILE

ffmpeg: 

    ffmpeg -i $SEEDFILE -f rawvideo -y /dev/null

gif2png:

    gif2png -r -f -h -O $SEEDFILE

gifsicle:

    gifsicle -i < $SEEDFILE > /dev/null

jpegtran:

    jpegtran $SEEDFILE

mp3gain:

    mp3gain $SEEDFILE

mupdf:

    mupdf $SEEDFILE

Outside In Viewer: 

    <Directory>/sdk/demo/simple $SEEDFILE

xpdf:

    xpdf $SEEDFILE






