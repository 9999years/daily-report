#! /bin/sh

git pull --no-edit
./dailyreport.py | lpr -o cpi=15 -o lpi=8
