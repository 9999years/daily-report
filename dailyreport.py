#! /usr/local/bin/python3

import argparse

# local imports
import gen_credentials as creds
import prefs
import weather
import dates
import misc

global prefs
global keys

def main():
    msg = '\n'.join(prefs.prefs['format'])

    def replace(txt, replacement):
        nonlocal msg
        if txt in msg:
            if callable(replacement):
                # function for lazy eval.
                msg = msg.replace(txt, replacement())
            else:
                # string
                msg = msg.replace(txt, replacement)

    replace('{hrule}', misc.hrule)
    replace('{today}', dates.today_date)
    replace('{iso_date}', dates.iso_date)
    replace('{short_forecast}', weather.forecast)
    replace('{calendar}', dates.events)

    print(msg)

if __name__ == '__main__':
    prefs.get_prefs()
    main()
