#! /usr/local/bin/python3
import argparse
from sys import stdout
import re

# local imports
import gen_credentials as creds
import prefs
import weather
import dates
import misc
import twtr

def report(args=None):
    prefs.get_prefs()

    msg = '\n'.join(prefs.prefs['format'])

    def replace(txt, replacement):
        nonlocal msg
        txt = '{' + txt + '}'
        if txt in msg:
            if callable(replacement):
                # function for lazy eval.
                msg = msg.replace(txt, replacement())
            else:
                # string
                msg = msg.replace(txt, replacement)

    # by passing functions we don't evaluate unless included in
    # prefs['format'] --- no weather api calls if you don't want weather, etc.
    replacements = {
        ('hrule',          misc.hrule),
        ('today',          dates.today_date),
        ('iso_date',       dates.iso_date),
        ('short_forecast', weather.forecast),
        ('weather_graph',  weather.graph),
        ('calendar',       dates.events),
        ('countdown',      dates.today_countdowns),
        ('todo',           dates.today_todos),
        ('twitter',        twtr.last)
    }

    # not implemented:
    # valid:
    # {xxx:(...)}
    #    or
    # {xxx}
    # literal:
    # {{xxx}}

    for replacement, fn in replacements:
        replace(replacement, fn)

    # empty sections surrounded by hrules can look silly
    # make them one hrule instead
    msg = re.sub('(' + misc.hrule() + r'\n*){2,}', misc.hrule() + '\n', msg)

    return msg

def main():
    parser = argparse.ArgumentParser(
        description='Generates a daily report'
    )

    parser.add_argument('-e', '--encoding',  type=str, default='utf-8',
        help='Output encoding. Default is UTF-8.')

    args = parser.parse_args()

    msg = report()
    stdout.buffer.write(msg.encode(args.encoding, errors='replace'))

if __name__ == '__main__':
    main()
