import datetime
import json
import requests
from urllib import parse as urlparse
import os

import prefs

def api_url(endpoint):
    return ('http://api.wunderground.com/api/' + prefs.keys['wunderground']
        + f'/{endpoint}'
        + '/q/{state}/{city}.json'.format_map(prefs.prefs['location']))

def weather(endpoint):
    url = api_url(endpoint)
    r = requests.get(url)
    return r.json()

def graph_weather():
    forecast = weather('hourly')
    Weather = namedtuple('Weather', ['temp', 'precip', 'time'])
    moments = []
    for hour in forecast['hourly_forecast']:
        moments.append(Weather(
            temp=int(hour['temp']['english']),
            precip=int(hour['pop']),
            time=str(int(hour['FCTTIME']['hour']) % 12 + 1)
            + hour['FCTTIME']['ampm']
        ))

    def limit(list, fn, key):
        return getattr(fn(list, key=lambda x: getattr(x, key)), key)

    def limits(list, key):
        return (limit(list, min, key),
                limit(list, max, key))

    (temp_max, temp_min)     = limits(moments, 'temp')
    (precip_max, precip_min) = limits(moments, 'precip')

    def place(val, x, y, field, align='left'):
        if align is 'left':
            field[y] = field[y][0:x] + val + field[y][x + len(val):]
        elif align is 'right':
            field[y] = field[y][0:x - len(val)] + val + field[y][x:]

    width = prefs.prefs['width']
    height = prefs.prefs['weather']['height']
    graph = [' ' * width for x in range(height + 2)]

    def lerp(min, max, amt):
        """Interpolate from min to max by amt"""
        return amt * (max - min) + min

    def between(min, max, val):
        """fraction val is between min and max"""
        return (val - min) / (max - min)

    margin = 3

    for y in range(height):
        place(str(int(lerp(temp_min, temp_max, y / (height - 1)))),
            0, y, graph)

        place('|', margin, y, graph)

        place(str(int(lerp(precip_min, precip_max, y / (height - 1)))),
            width, y, graph, align='right')

        place('|', width - margin, y, graph)

    step = (width - 2 * margin) / len(moments)
    time_rows = step

    for i, moment in enumerate(moments):
        odd = i % time_rows
        i = i * step + margin + 1
        place('×', i, int(lerp(0, height - 1,
            between(temp_min, temp_max, moment.temp))), graph)
        precip_y = int(lerp(0, height - 1,
            between(precip_min, precip_max, moment.precip)))
        if graph[precip_y][i] is '×':
            place('#', i, precip_y, graph)
        else:
            place('·', i, precip_y, graph)

        time_num = moment.time[:-2]
        place(time_num, i, height + odd, graph)

    for line in graph:
        print(line)

def forecast():
    prefs.get_prefs()
    forecast = weather('forecast')['forecast']
    day_data = forecast['simpleforecast']['forecastday'][0]
    txt_data = forecast['txt_forecast']['forecastday'][0]
    high     = int(day_data['high']['fahrenheit'])
    low      = int(day_data['low']['fahrenheit'])
    precip   = int(day_data['pop'])
    conds    = day_data['conditions']
    summary  = txt_data['fcttext']
    return f'{low}-{high}F, {precip}% prec.\n{conds}'

def main():
    prefs.get_prefs()
    forecast()

if __name__ == '__main__':
    main()
