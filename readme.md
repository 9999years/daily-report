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

Which you can install with

    pip install google-api-python-client python-twitter requests

Please let me know if there are any other dependencies I haven’t listed here!

# `keys.json`

`keys.json` should have the following keys:

* [`wunderground`][wundeground]
* [`twitter`][twitter], which should contain:
    * `consumer_key`
    * `consumer_secret`
    * `access_token`
    * `access_token_secret`

[wundeground]: https://www.wunderground.com/weather/api
[twitter]: https://apps.twitter.com/app/new
