import datetime
import json
import requests
from urllib import parse as urlparse
from collections import namedtuple
import os
from time import sleep

import prefs
import misc

def api_url(endpoint):
    return ('https://api.wunderground.com/api/'
        + prefs.keys['wunderground']
        + '/'
        + endpoint
        + '/q/{state}/{city}.json'.format_map(prefs.prefs['location']))

def weather(endpoint, retries=2):
    url = api_url(endpoint)

    # request and retry up to `retries` times
    for i in range(retries):
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            break
        else:
            # wait a second --- don't hammer the api
            sleep(1)

    return r.json()

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

def forecast():
    forecast = weather('forecast')['forecast']
    day_data = forecast['simpleforecast']['forecastday'][0]
    txt_data = forecast['txt_forecast']['forecastday'][0]
    high     = int(day_data['high']['fahrenheit'])
    low      = int(day_data['low']['fahrenheit'])
    precip   = int(day_data['pop'])
    conds    = day_data['conditions'].lower()
    summary  = txt_data['fcttext']
    return f'{low}-{high}°F, {precip}% chance of precip.\n{conds}'

def main():
    forecast()

if __name__ == '__main__':
    main()
