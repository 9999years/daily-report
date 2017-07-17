> I said hey, what's going on?
>
> — “What’s Up?” by 4 Non Blondes (1992, Interscope Records)

The Daily Report is a script to output a daily briefing — I’m hooking it up
to a cron job and a receipt printer to print out an agenda for me daily.

Run `gen_credentials.py` to generate a credential file.

Usage:

    $ ./dailyreport.py

    good morning!
    today is Monday, July 17 (17-07-17)
    --------------------------------
    70-89F, 50% chance of precip.
    Chance of a Thunderstorm
    --------------------------------
    all day:  parents gone
    all day:  business cards
    --------------------------------
    12:30PM  -  schedule clinic visit
     8:00PM  -  egg drop soup (possibly w/ aya)

Make sure to edit `prefs.json` for accurate weather forecasts.

# `keys.json`

`keys.json` should have the following keys:

* [`wunderground`][wundeground]

[wundeground]: https://www.wunderground.com/weather/api
