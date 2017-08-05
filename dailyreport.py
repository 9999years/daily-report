#! /usr/local/bin/python3
import argparse
from sys import stdout
import re
import uni2esky

# local imports
import gen_credentials as creds
from prefs import prefs, keys
import misc
from extendedformatter import formatter, extformat
import weather
import dates
import misc
import twtr
import maze

def report():
    # refresh prefs
    prefs.refresh()
    keys.refresh()

    # Tab /=\|\./l1r1r0l0

    formatter.extend_env(
        hrule           =    misc.hrule,
        thinhrule       =    misc.thinhrule,
        center          =    misc.center,
        right           =    misc.right,
        left_pad        =    misc.right,
        align           =    misc.align,
        fill            =    misc.fill,
        today           =   dates.today_date,
        now_hm          =   dates.now_hm,
        iso_date        =   dates.iso_date,
        calendar        =   dates.events,
        countdown       =   dates.today_countdowns,
        todo            =   dates.today_todos,
        work            =   dates.today_work,
        twitter         =    twtr.last,
        maze            =    maze.from_prefs,
        forecast        = weather.today_forecast,
        tmrw_forecast   = weather.tomorrow_forecast,
        conditions      = weather.conditions,
        tmrw_conditions = weather.tomorrow_conditions,
        weather_graph   = weather.graph,
        sun             = weather.suntimes,
        moon            = weather.moon,
    )

    msg = extformat(prefs['format'])

    return misc.deduplicate_rules(msg)

def main():
    parser = argparse.ArgumentParser(
        description='Generates a daily report'
    )

    parser.add_argument('-e', '--encoding', type=str, default='utf-8',
        help='Output encoding. Default is UTF-8. Irrelevant with --print')

    parser.add_argument('-p', '--print', action='store_true',
        help='Printing output --- converts codepoints to Esky escapes.')

    args = parser.parse_args()

    msg = report()
    if args.print:
        msg = b'\x1b\x33\x18' + uni2esky.encode(msg)
        stdout.buffer.write(msg)
    else:
        stdout.buffer.write(msg.encode(args.encoding, errors='replace'))

if __name__ == '__main__':
    main()
