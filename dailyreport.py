#! /usr/local/bin/python3
import argparse
from sys import stdout
import re

# local imports
from prefs import prefs, keys
from formatter import extformat
import misc

def report():
    msg = extformat(prefs['format'])

    return misc.deduplicate_rules(msg)

def main():
    parser = argparse.ArgumentParser(description='Generates a daily report')

    parser.add_argument('-e', '--encoding', type=str, default='utf-8',
        help='Output encoding. Default is UTF-8. Irrelevant with --print')

    parser.add_argument('-p', '--print', action='store_true',
        help='Printing output --- converts codepoints to Esky escapes.')

    args = parser.parse_args()

    msg = report()
    stdout.buffer.write(msg.encode(args.encoding, errors='replace'))

if __name__ == '__main__':
    main()
