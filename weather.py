import datetime
import json
import requests
from urllib import parse as urlparse
from collections import namedtuple
import os
from time import sleep

import prefs
import misc

# dict of runtime caches, to avoid double requests
cache = {}

def api_url(endpoint):
    return ('https://api.wunderground.com/api/'
        + prefs.keys['wunderground']
        + '/'
        + endpoint
        + '/q/{location}.json'.format_map(prefs.prefs['weather']))

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

    width = prefs.prefs['width']
    height = prefs.prefs['weather']['height']
    margin = 3
    step = int((width - 2 * margin) / len(moments))
    time_rows = 3 * step

    graph = [' ' * width for x in range(height + time_rows)]

    for y in range(height):
        place(str(int(misc.lerp(temp_min, temp_max, y / (height - 1)))),
            0, y)

        place(prefs.prefs['vert'], margin - 1, y)

        place(str(int(misc.lerp(precip_min, precip_max, y / (height - 1)))),
            width, y, align='right')

        place(prefs.prefs['vert'], width - margin, y)

    chars = prefs.prefs['weather']['chars']

    for i, moment in enumerate(moments):
        odd = i % time_rows
        i_orig = i
        i = int(i * step + margin)
        time_num = moment.time[:-2]
        if int(time_num) % 12 == 0:
            for j in range(height):
                place(prefs.prefs['vert_light'], i, j)
        temp_y = int(misc.scale(
            moment.temp, temp_min, temp_max, 0, height - 1))
        place(chars['temp'], i, temp_y)
        precip_y = int(misc.scale(
            moment.precip, precip_min, precip_max, 0, height - 1))
        if graph[precip_y][i] is chars['temp']:
            place(chars['both'], i, precip_y)
        else:
            place(chars['precip'], i, precip_y)

        place(time_num, i, height + odd)

    return '\n'.join(graph)

def day_forecast(day=0, prefix=''):
    forecast = weather('forecast')['forecast']
    day_data = forecast['simpleforecast']['forecastday'][day]
    txt_data = forecast['txt_forecast']['forecastday'][day]
    high     = int(day_data['high'][prefs.prefs['weather']['temp']])
    low      = int(day_data['low'][prefs.prefs['weather']['temp']])
    precip   = int(day_data['pop'])
    conds    = day_data['conditions'].lower()
    summary  = txt_data['fcttext']
    return prefs.prefs['weather']['forecast_format'].format(**locals())

def conditions(day=0):
    return (weather('forecast')
        ['forecast']
        ['simpleforecast']
        ['forecastday']
        [day]
        ['conditions'].lower())

def tomorrow_conditions():
    return conditions(day=1)

def today_forecast():
    return day_forecast(day=0, prefix=prefs.prefs['weather']['today_prefix'])

def tomorrow_forecast():
    return day_forecast(day=1, prefix=prefs.prefs['weather']['tomorrow_prefix'])

def sunrise():
    times = weather('astronomy')['sun_phase']['sunrise']
    return datetime.datetime.strptime(
        times['hour'] + times['minute'],
        '%H%M')
    return time

def sunset():
    times = weather('astronomy')['sun_phase']['sunset']
    return datetime.datetime.strptime(
        times['hour'] + times['minute'],
        '%H%M')

def suntimes():
    risetime, settime = sunrise(), sunset()
    daylight = settime - risetime
    return misc.align(
        misc.hourminute(risetime) + ' rise',
        misc.formatdelta(daylight, clock=24),
        misc.hourminute(settime) + ' set',
        prefs.prefs['width'])

def moon():
    times = weather('astronomy')['moon_phase']
    phase = times['phaseofMoon']
    percent = times['percentIlluminated']
    graphic = (prefs.prefs['weather']['moon_bright']
        if int(times['percentIlluminated']) > 50
        else prefs.prefs['weather']['moon_dark'])

    return misc.center(f'{graphic} {phase.lower()} @ {percent}%')

def main():
    forecast()

if __name__ == '__main__':
    main()
