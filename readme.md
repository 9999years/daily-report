> I said hey, what's going on?
>
> — “What’s Up?” by 4 Non Blondes (1992, Interscope Records)

The Daily Report is a script to output a daily briefing — I’m hooking it up
to a cron job and a receipt printer to print out an agenda for me daily.

Run `gen_credentials.py` to generate a credential file.

Usage:

    $ ./dailyreport.py

    good morning!
    today is monday, july 17
                          2017-07-17
    --------------------------------
    70-88F, 40% chance of precip.
    chance of a thunderstorm
    --------------------------------
    all day | business cards
    --------------------------------
     3:30PM | schedule doctor's appt
     3:30PM | heather
     8:00PM | egg drop soup w/
            | camille (& possibly
            | aya)


Make sure to edit `prefs.json` for accurate weather forecasts.

Potential usage with `cron`, to print daily at 6am:

    0 6 * * * cd /home/pi/daily-report && git pull && ./dailyreport.py | lpr -l

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
