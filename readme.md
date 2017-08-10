> I said hey, what's going on?
>
> — “What’s Up?” by 4 Non Blondes (1992, Interscope Records)

The Daily Report is a script to output a daily briefing — I’m hooking it up
to a cron job and a receipt printer to print out an agenda for me daily.

Run `gen_credentials.py` to generate a credential file.

Usage:

    $ ./dailyreport.py

    good morning!
    today is wednesday, july 19
                          2017-07-19
    --------------------------------
    72-91°F, 20% chance of precip.
    partly cloudy
    --------------------------------
    94|øø····             ×××××××|15
    89|  ××             ××       |12
    85|    ×           ×         | 9
    81|     ×××·······×          | 6
    77|      ··××××  ×··         | 3
    73|            ××   ·········| 0
       6  9  12 3  6  9  12 3  6
        7  10 1  4  7  10 1  4  7
         8  11 2  5  8  11 2  5
    --------------------------------
    all day | parents gone (day 13
            | of 16)
    --------------------------------
     8:00PM | egg drop soup w
            | camille (& possibly
            | aya)
    --------------------------------
    [] send immunization records
    --------------------------------
     16 | visit jay (2017-08-04)
     39 | move in day (2017-08-27)
    159 | christmas (2017-12-25)
    285 | birthday (2018-04-30)



Make sure to edit `prefs.json` for accurate weather forecasts.

Potential usage with `cron`, to print daily at 6am:

    0 6 * * * cd /home/pi/daily-report && git pull && ./dailyreport.py | lpr -l

# Dependencies

The Daily Report has several dependencies, which you can find by attempting to
run `./dailyreport.py` and seeing what errors you get.

You will need *at least*:

* `google-api-python-client`
* `python-twitter`
* `requests`
<<<<<<< Updated upstream
||||||| merged common ancestors
* [`uni2esky`][uni2esky], my own library for converting Unicode strings to Esky
  POS-58 escape sequences. Only necessary if you’d like to print on a receipt
  printer.
* [`extendedformatter`][extformat], my library for formatting arbitrary strings
  as `f`-strings.
=======
* [`uni2esky`][uni2esky], my own library for converting Unicode strings to Esky
  POS-58 escape sequences. Only necessary if you’d like to print on a receipt
  printer.
* [`extendedformatter`][extformat], my library for formatting arbitrary strings
  as `f`-strings.
* `BeautifulSoup4`
>>>>>>> Stashed changes

Which you can install with

<<<<<<< Updated upstream
    pip install google-api-python-client python-twitter requests
||||||| merged common ancestors
    pip install google-api-python-client python-twitter requests uni2esky extendedformatter
=======
    pip install google-api-python-client python-twitter requests uni2esky extendedformatter beautifulsoup4
>>>>>>> Stashed changes

A larger barrier to entry will be the API keys:

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

Ah, Google. The blue beast. Anyways, to get some Google credentials you'll need
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
   `google_credentials.json` (`prefs.google_credential_path`).

[wunderground]: https://www.wunderground.com/weather/api
[twitter]: https://apps.twitter.com/app/new
[gcal]: https://console.cloud.google.com/apis/dashboard
[creds]: https://console.cloud.google.com/apis/credentials
[proj]: https://console.cloud.google.com/projectcreate
