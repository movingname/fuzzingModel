# fuzzingModel

This is the project folder for the work Empirical Analysis and Modeling of Black-Box Mutational Fuzzing. 

If there are information missing in the repo, please email us at muz127@ist.psu.edu.


## Commands used for fuzzing programs:

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






