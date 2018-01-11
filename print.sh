#! /bin/sh

git pull --no-edit > /dev/null
./dailyreport.py | lpr -o cpi=15 -o lpi=8
