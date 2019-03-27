# Indefinite archival notice
Due to a few combined circumstances:
  - [Weather Underground shut down their API][wunderground]
  - I don’t use this script at the moment because I realized that printing a
    receipt every day just to throw it out is pretty wasteful
  - I realized that the [`extendedformatter`][extformat] library I created is a
    glorified `eval()` and is probably a pretty terrible idea (even in this
    case, where user input is assumed (??) to be trusted)
  - [Google deprecated the `oauth2client` library][oauth2client] this project
    uses to interface with Google Calendar (etc.)
Development on this project is halted for the time being. There’s a chance I’ll
touch it up in the future, but I’m pretty busy right now.

# The Daily Report

> I said hey, what's going on?
>
> — “What’s Up?” by 4 Non Blondes (1992, Interscope Records)

The Daily Report is a script to output a daily briefing designed for use with a
receipt printer (and cron-job / Raspberry Pi).

Usage / sample output:

    $ ./dailyreport.py

             good morning!
       today is thursday, aug 10
    5:29PM                2017-08-10
    ════════════════════════════════
             65-81°F, 60%p
        chance of a thunderstorm
    6:48AM ↑      14:03     8:51PM ↓
         ○ waning gibbous @ 90%
    ────────────────────────────────
        tomorrow: 58-77°F, 20%p
             partly cloudy
    ════════════════════════════════
    82║×××  │  ···      │        ║58
    78║   × │           │  ××    ║46
    75║    ¤·      ··   │××··××× ║34
    72║  ·· ×··   ·  ··¤×··  ···×║23
    69║     │××××××× ×× ·       ·║11
    66║··   │       ×   │        ║ 0
    °F×  9  12 3  6  9  12 3  6  ·%p
    ════════════════════════════════
     6:30AM ║ jay @general
    ────────────────────────────────
    all day ║ visit jay (day 6 of 8)
    all day ║ summer break (day 43
            ║ of 60)
    ────────────────────────────────
    [] get toothpaste
    ────────────────────────────────
     17 ║ move in day (2017-08-27)
    137 ║ christmas (2017-12-25)
    263 ║ birthday (2018-04-30)
    ════════════════════════════════
    → Aiming Missiles to Fall Near
      Guam, North Korea’s Kim Takes
      New Risk ⟨goo.gl/TSStQP⟩
    → Trump’s ‘Fire and Fury’ Threat
      Raises Alarm in Asia
      ⟨goo.gl/JQDLfS⟩
    → Memo from Europe: Europe’s
      Leaders Curtail Summer
      Holidays in Light of Crises
      ⟨goo.gl/uJbJn4⟩
    → Exclusive: Amazon in talks to
      offer event ticketing in U.S.-
      sources ⟨goo.gl/5YCNw8⟩
    ════════════════════════════════
    @dril: im sorry every one.  the
    mayor ran out of key to the
    cities so they had to give me
    the key to all the girls
    bathrooms instead
    ────────────────────────────────
    9881 likes, 1573 rts
    2017-08-10 06:40:26AM
    ════════════════════════════════
    Tatiana Tolmacheva
    ────────────────────────────────
    Tatiana Aleksandrovna Tolmacheva
    (Russian: Татьяна Александровна
    Толмачева; January 21, 1907 –
    October 21, 1998 in Moscow), née
    Granatkina (Russian: Гранаткина)
    was a former Soviet figure
    skater, figure skating coach and
    one of the founders of Soviet
    figure skating school, Honoured
    Master of Sports of the USSR.
    She started skating as single
    skater and represented "Dynamo"
    club in the 1930s. Then she
    moved to pair skating with
    partner Alexander Tolmachev.
    ════════════════════════════════
    S&P 500     -1.06%       2447.90
    Dow Jones   -0.93      21,844.01
    VIX         +27.45%        14.16
    GOLD        +1.208%       96.745
    ────────────────────────────────
    AMZN        -2.06%        961.75
    GDX         +1.881%       23.025
    MSFT        -0.63%         72.01
    RDS-A       -1.13%         56.13
    FB          -1.64%        168.37
    GOOGL       -1.16%        929.14
    TWTR        -1.61%         15.88
    AAPL        -2.1719%    156.9456
    TSLA        -0.73%        360.86

In order, we see

* The date and time
* Today's weather and conditions
* Today's sunrise, sunset, and total hours of daylight
* Today's phase of the moon
* Tomorrow's weather and conditions
* A graph of temperature and precipitation chances over the next 24 hours
* Information pulled from Google Calendars, including work shifts, all day
  events, to-dos, and countdowns.
* News headlines from Reuters and the New York Times
* @dril's latest tweet (or nothing if the latest Tweet wasn't made in the past
  day)
* A random Wikipedia article
* Stock prices

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

* Output like Unix `cal(1)`
* Gmail integration
* ???
* On this day in history
* Birthdays
* Oh god I need to test this whole thing
* Updated documentation (news & stocks)

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
[oauth2client]: https://google-auth.readthedocs.io/en/latest/oauth2client-deprecation.html
