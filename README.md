# Empirical Analysis and Modeling of Black-Box Mutational Fuzzing

This repository contains data and scripts for the work Empirical Analysis and Modeling of Black-Box Mutational Fuzzing. 

To reproduce our analysis and experiment, please follow the steps described in each section.

Please email us (muz127@ist.psu.edu) for any question.


## 1. Data

The fuzzing campaign data for analysis is contained in results/results.zip. We have pruned out some large and unnecessary files.
Please unzip the content to the results/ folder.

## 2. The Analysis

The scripts/ folder has all scripts used for data analysis. Among these scripts, the Jupyter notebook (IPython notebook) 
main_analysis.ipynb contains all results presented in Section 4, 5 and 6. You could directly view the notebook on Github. 

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
	
## 3. The Fuzzing Process

Below, we list all steps of our fuzzing experiment, from seed collection to running fuzzing.
NOTICE: We do not share seed files, because the size of the seed collection is too large (10GB+).

### 3.1 Prepare the Fuzzing Environment

(1) Download the VM image of BFF 2.7 and follow the installation guide.
https://www.cert.org/vulnerability-analysis/tools/bff.cfm?

(2) After launching the VM, install the target application using apt-get. We list program version numbers in the paper.

(3) Install the pincoverage tool we wrote. First, copy pincoverage/ to the bff shared folder in the host OS.
Then in the guest OS, enter pincoverage/ and do

    python make.py

### 3.2 Seed Collection

We briefly describe how to collect seed files from the Internet:

**Video**:

samples.mplayerhq.hu

**PDF**:

Google, Bing

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

(1) In the host OS, put all seed files for a target program into bff/full_seeds.

(2) Start code coverage data collection:

    python pincoverage/collect_cov.py

(3) Use the greedy algorithm to select seeds (on the host OS):

    python scripts/analyze_cov.py
	
(4) Copy selected seeds to the fuzzing folder (on the host machine):

    python copy_seeds.py

	
### 3.4 Run Fuzzing

(1) Increase the maximum number of backup logs. In bff.py, find the following line:

    # set up remote logging
    setup_logfile(cfg.output_dir, log_basename='bff.log', level=logging.INFO,
                  max_bytes=1e7, backup_count=5)
				  
Update the backup_count to 500.

(2) (Optional) To clear up all fuzzing campagin records:

    ./reset_bff.sh --remove-results

(3) Tell BFF the command used in fuzzing. In conf.d/bff.cg, update the following lines:

cmdline=<The command>

killprocname=<name of the target program>

## Commands Used for Fuzzing Programs:

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






