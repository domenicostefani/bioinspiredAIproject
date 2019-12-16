#!/bin/sh
rm -rf out
mogrify -format gif *.bmp
rm -rf ./gif/
mkdir gif
mv *.gif ./gif
mkdir out
cd gif/
gifsicle --delay=40 *.gif > anim.gif
mv anim.gif ./../out/
gifsicle --delay=40 --loop *.gif > animloop.gif
mv animloop.gif ./../out/
cd ./../
rm -r gif/
