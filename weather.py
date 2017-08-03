import datetime
import json
import requests
from urllib import parse as urlparse
from collections import namedtuple
import os
from time import sleep

from prefdicts import prefs, keys
import misc
from extendedformatter import formatter, extformat

# dict of runtime caches, to avoid double requests
cache = {}

def api_url(endpoint):
    return ('https://api.wunderground.com/api/'
        + keys['wunderground']
        + '/'
        + endpoint
        + '/q/{location}.json'.format_map(prefs['weather']))

def weather(endpoint, retries=2):
    # already made this request? don't make it again!
    # TODO maybe add a time limit for cache validity
    if endpoint in cache:
        return cache[endpoint]

    url = api_url(endpoint)

    # request and retry up to `retries` times
    for i in range(retries):
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            break
        else:
            # wait a second --- don't hammer the api
            sleep(1)

    ret = r.json()
    cache[endpoint] = ret
    return ret

def graph():
    forecast = weather('hourly')
    Weather = namedtuple('Weather', ['temp', 'precip', 'time'])
    moments = []
    i = 0
    for hour in forecast['hourly_forecast']:
        moments.append(Weather(
            temp=int(hour['temp']['english']),
            precip=int(hour['pop']),
            time=str(int(hour['FCTTIME']['hour']) % 12 + 1)
            + hour['FCTTIME']['ampm']
        ))
        if i > 24:
            break
        else:
            i += 1

    def limit(list, fn, key):
        return getattr(fn(list, key=lambda x: getattr(x, key)), key)

    def limits(list, key):
        return (limit(list, min, key),
                limit(list, max, key))

    (temp_max, temp_min)     = limits(moments, 'temp')
    (precip_max, precip_min) = limits(moments, 'precip')

    def place(val, x, y, align='left'):
        nonlocal graph
        field = graph
        if align is 'left':
            field[y] = field[y][0:x] + val + field[y][x + len(val):]
        elif align is 'right':
            field[y] = field[y][0:x - len(val)] + val + field[y][x:]

    width = prefs['width']
    height = prefs['weather']['height']
    margin = 3
    step = int((width - 2 * margin) / len(moments))
    time_rows = 1
    # time_rows = 3 * step

    graph = [' ' * width for x in range(height + time_rows)]

    chars = prefs['weather']['chars']

    place('°F' + chars['temp'], 0, height)
    place(chars['precip'] + '%p', width - margin, height)

    for y in range(height):
        # temp axis marker
        place(str(int(misc.lerp(temp_min, temp_max, y / (height - 1)))),
            0, y)

        # left rule
        place(prefs['vert'], margin - 1, y)

        # precip marker
        place(str(int(misc.lerp(precip_min, precip_max, y / (height - 1)))),
            width, y, align='right')

        # right rule
        place(prefs['vert'], width - margin, y)

    for i, moment in enumerate(moments):
        # odd = i % time_rows
        i_orig = i
        i = int(i * step + margin)
        time_num = int(moment.time[:-2])

        if time_num % 3 == 0:
            # write time at 3 6 9 12
            place(str(time_num), i, height)

            # vrule at 12am/pm
            if time_num % 12 == 0:
                for j in range(height):
                    place(prefs['vert_light'], i, j)

        temp_y = int(misc.scale(
            moment.temp, temp_min, temp_max, 0, height - 1))
        place(chars['temp'], i, temp_y)
        precip_y = int(misc.scale(
            moment.precip, precip_min, precip_max, 0, height - 1))
        if graph[precip_y][i] is chars['temp']:
            place(chars['both'], i, precip_y)
        else:
            place(chars['precip'], i, precip_y)


    return '\n'.join(graph)

def day_forecast(day=0):
    forecast = weather('forecast')['forecast']
    day_data = forecast['simpleforecast']['forecastday'][day]
    txt_data = forecast['txt_forecast']['forecastday'][day]

    return extformat(prefs['weather']['forecast_format'],
        forecast=forecast,
        day_data=day_data,
        txt_data=txt_data,
        high    =int(day_data['high'][prefs['weather']['temp']]),
        low     =int(day_data['low'][prefs['weather']['temp']]),
        precip  =int(day_data['pop']),
        conds   =day_data['conditions'],
        summary =txt_data['fcttext'],
    )

def conditions(day=0):
    return (weather('forecast')
        ['forecast']
        ['simpleforecast']
        ['forecastday']
        [day]
        ['conditions'])

def tomorrow_conditions():
    return conditions(day=1)

def today_forecast():
    return day_forecast(day=0)

def tomorrow_forecast():
    return day_forecast(day=1)

def parsesuntime(t):
    return datetime.datetime.strptime(
        t['hour'].rjust(2, '0') + t['minute'], '%H%M')

def sunrise():
    times = weather('astronomy')['sun_phase']['sunrise']
    return parsesuntime(times)

def sunset():
    times = weather('astronomy')['sun_phase']['sunset']
    return parsesuntime(times)

def suntimes():
    risetime, settime = sunrise(), sunset()
    daylight = settime - risetime

    risefmt = extformat(
        prefs['weather']['sun']['rise_format'],
        sunrise=misc.hoursminutes(risetime, pad=''))

    setfmt = extformat(
        prefs['weather']['sun']['set_format'],
        sunset=misc.hoursminutes(settime, pad=''))

    dayfmt = extformat(
        prefs['weather']['sun']['daylight_format'],
        daylight=misc.formatdelta(daylight, clock=24))

    return extformat(
        prefs['weather']['sun']['format'],
        sunrise =risefmt,
        sunset  =setfmt,
        daylight=dayfmt,)

def moon():
    times = weather('astronomy')['moon_phase']
    phase = times['phaseofMoon'].lower()
    percent = times['percentIlluminated']
    graphic = (prefs['weather']['moon']['bright_graphic']
        if int(times['percentIlluminated']) > 50
        else prefs['weather']['moon']['dark_graphic'])

    return extformat(prefs['weather']['moon']['format'],
        **locals())

def main():
    forecast()

if __name__ == '__main__':
    main()
