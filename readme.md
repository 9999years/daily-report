> I said hey, what's going on?
>
> — “What’s Up?” by 4 Non Blondes (1992, Interscope Records)

The Daily Report is a script to output a daily briefing — I’m hooking it up
to a cron job and a receipt printer to print out an agenda for me daily.

Usage:

    $ ./dailyreport.py

             good morning!
    today is sunday, july 30
    7:43PM                2017-07-30
    ════════════════════════════════
             60-82°F, 10%p
                 clear
    6:08AM ↑      14:14     8:22PM ↓
         ○ first quarter @ 53%
    ────────────────────────────────
    tomorrow: 65-85°F, 10%p
                 clear
    ════════════════════════════════
    84║   │    ···    │××××××××  ║ 8
    79║×  │  ··   ·  ××        ××║ 6
    74║ × │ ·      ·× │          ║ 4
    70║  ××¤×      ×· │         ·║ 3
    65║   │  ×××× ×   │        · ║ 1
    61║····      ×   ··········  ║ 0
    °F×9  12 3  6  9  12 3  6  9 ·%p
    ════════════════════════════════
    all day ║ summer break (day 43
            ║ of 60)
    ────────────────────────────────
    12:00PM ║ work at citysburg
    ────────────────────────────────
    [] get toothpaste
    ────────────────────────────────
      5 ║ visit jay (2017-08-04)
     28 ║ move in day (2017-08-27)
    148 ║ christmas (2017-12-25)
    274 ║ birthday (2018-04-30)


Make sure to read/edit `prefs.json`! It controls **all** of the program's
behavior, from weather location to output format. It is dense by design — I
believe you should be able to completely change the output format to suit you
without touching the code. Easy modifications for me are an advantage.

Potential usage with `cron`, to print daily at 6am:

    0 6 * * * cd /home/pi/daily-report && git pull && ./dailyreport.py | lpr -l

# Customization

See [`customization.md`][cust] for details on how to customize The Daily Report.

# Dependencies

The Daily Report has several dependencies, which you can find by attempting to
run `./dailyreport.py` and seeing what errors you get.

You will need *at least*:

* `google-api-python-client`
* `python-twitter`
* `requests`
* [`uni2esky`][uni2esky], my own library for converting Unicode strings to Esky
  POS-58 escape sequences. Only necessary if you’d like to print on a receipt
  printer.
* [`extendedformatter`][extformat], my library for formatting arbitrary strings
  as `f`-strings.
* `BeautifulSoup4`

Which you can install with

    pip install google-api-python-client python-twitter requests uni2esky extendedformatter beautifulsoup4

A larger barrier to entry will be the API keys:

# Functionality coming soon, maybe

* Stock module (hook up with Yahoo Finance?)
* Output like Unix `cal(1)`
* Gmail integration
* ???
* On this day in history
* Breaking headlines
* Birthdays

# APIs

Current APIs being used are [Weather Underground][wunderground], [Google
calendar][gcal], and [Twitter][twitter] (may see more use in the future).

## Limits

API          |Limits
-------------|---------------
Wunderground |500 / day
Google Cal   |1,000,000 / day
Twitter      |A Lot

## `keys.json`

`keys.json` should have the following keys:

* [`wunderground`][wunderground]
* [`twitter`][twitter], which should contain:
    * `consumer_key`
    * `consumer_secret`
    * `access_token`
    * `access_token_secret`

## Google

Ah, Google. The Blue Beast. Anyways, to get some Google credentials you'll need
to do a few things.

1. [Create a project][proj] in the Google Cloud Platform. There's a quota of
   like 12 projects but considering the calendar read limit of 1,000,000
   requests / day I think you'll be OK.
2. [Download your project's credentials][creds], listed under OAuth 2.0 client
   IDs, by clicking the download icon or the app name and then the download
   button. Google has the JSON prepared for you, there's no reason to mess with
   it.
3. Rename the downloaded file (something like
   `client_secret_{YOUR_CLIENT_ID}.apps.googleusercontent.com`) to
   `google_keys.json`, or whatever the value of `google_key_path` in
   `prefs.json` is.
4. Run `gen_credentials.py`, which will open your default browser, prompting
   you to log in. This generates the second set of OAuth keys, stored in
   `google_credentials.json` (`prefs.google_credential_path`). You’re done!

[wunderground]: https://www.wunderground.com/weather/api
[twitter]: https://apps.twitter.com/app/new
[gcal]: https://console.cloud.google.com/apis/dashboard
[creds]: https://console.cloud.google.com/apis/credentials
[proj]: https://console.cloud.google.com/projectcreate
[uni2esky]: https://pypi.python.org/pypi/uni2esky
[fmt-strings]: https://docs.python.org/3/library/string.html#format-string-syntax
[iso8601]: https://en.m.wikipedia.org/wiki/ISO_8601
[strftime]: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
[cust]: ./customization.md
[extformat]: https://github.com/9999years/extendedformatter
