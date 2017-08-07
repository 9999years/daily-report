from extendedformatter import formatter, extformat

from prefs import prefs, keys

import misc
import dates
import twtr
import maze
import weather
import wikipedia

# Tab /=\|\./l1r1r0l0

formatter.extend_env(

    hrule           =      misc.hrule,
    thinhrule       =      misc.thinhrule,
    center          =      misc.center,
    right           =      misc.right,
    left_pad        =      misc.right,
    align           =      misc.align,
    fill            =      misc.fill,
    hm              =      misc.hoursminutes,
    shell           =      misc.shell,
    today           =     dates.today_date,
    now_hm          =     dates.now_hm,
    iso_date        =     dates.iso_date,
    events          =     dates.events,
    countdown       =     dates.today_countdowns,
    todo            =     dates.today_todos,
    work            =     dates.today_work,
    twitter         =      twtr.last,
    twitter_bot     =      twtr.bot,
    maze            =      maze.from_prefs,
    forecast        =   weather.today_forecast,
    tmrw_forecast   =   weather.tomorrow_forecast,
    conditions      =   weather.conditions,
    tmrw_conditions =   weather.tomorrow_conditions,
    weather_graph   =   weather.graph,
    sun             =   weather.suntimes,
    moon            =   weather.moon,
    wikipedia       = wikipedia.random,

)

formatter.width = prefs['width']
