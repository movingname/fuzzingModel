# Empirical Analysis and Modeling of Black-Box Mutational Fuzzing

This repository contains data and scripts for the work Empirical Analysis and Modeling of Black-Box Mutational Fuzzing. 

Please email us (muz127@ist.psu.edu) for any question.


## 1. Data

## 2. The Analysis

## 3. The Fuzzing Process

NOTICE: The fuzzing process described in the paper cannot be reproduced using data provided here.
One reason is that we do not provide seed files, because the size of the collection is very large (10GB+).
However, here we list all steps of our fuzzing experiment, from seed collection to running fuzzing.

### 3.1 Prepare the fuzzing environment

(1) Download the VM image of BFF 2.7 and follow the installation guide.
https://www.cert.org/vulnerability-analysis/tools/bff.cfm?

(2) After launching the VM, install the target application using apt-get. We list program version numbers in the paper.

(3) Install the pincoverage tool we wrote. First, copy pincoverage/ to the bff shared folder in the host OS.
Then in the guest OS, enter pincoverage/ and do make

### 3.2 Seed Collection

### 3.3 Collect and Analyze Coverage Data

### 3.4 Run Fuzzing

*Commands used for fuzzing programs*:

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






