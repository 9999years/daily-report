#! /usr/local/bin/python3
import argparse
from sys import stdout
import re
import uni2esky

# local imports
import gen_credentials as creds
from prefdicts import prefs, keys
import prefhelpers
import misc

def report():
    prefs, keys = prefhelpers.get_prefs()
    return misc.format(prefs['format'])


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
