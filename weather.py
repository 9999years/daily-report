#! /usr/local/bin/python3
import datetime
import json
import requests
from urllib import parse as urlparse
from collections import namedtuple
import os

from prefs import prefs, keys
import misc
from formatter import extformat

# dict of runtime caches, to avoid double requests
cache = {}

def api_url(endpoint, location=prefs['weather']['location']):
    return ('https://api.wunderground.com/api/'
        + keys['wunderground']
        + f'/{endpoint}/q/{location}.json')

def weather(endpoint, location=prefs['weather']['location']):
    global cache
    ret, cache = misc.request_json(api_url(endpoint, location), cache)
    return ret

def hours(length=24, location=prefs['weather']['location']):
    moments = []
    forecast = weather('hourly', location)
    Weather = namedtuple('Weather', ['temp', 'precip', 'time'])
    for i, hour in enumerate(forecast['hourly_forecast']):
        if i >= length:
            break
        moments.append(Weather(
            temp=int(hour['temp']['english']),
            precip=int(hour['pop']),
            time=str(int(hour['FCTTIME']['hour']) % 12 + 1)
            + hour['FCTTIME']['ampm']
        ))
    return moments

def graph(location=prefs['weather']['location']):
    width = prefs['width']
    height = prefs['weather']['height']
    margin = 3
    inner_width = width - 2 * margin
    moments = hours(length=inner_width, location=location)

    if len(moments) == 0:
        return ''

    def limit(seq, fn, key):
        return getattr(fn(seq, key=lambda x: getattr(x, key)), key)

    def limits(seq, key):
        return (limit(seq, min, key),
                limit(seq, max, key))

    (temp_max, temp_min)     = limits(moments, 'temp')
    (precip_max, precip_min) = limits(moments, 'precip')

    def place(val, x, y, align='left'):
        nonlocal graph
        field = graph
        if y > len(field) or x > len(field[y]):
            return

        if align is 'left':
            field[y] = field[y][0:x] + val + field[y][x + len(val):]
        elif align is 'right':
            field[y] = field[y][0:x - len(val)] + val + field[y][x:]

    step = int((inner_width) / len(moments))
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

def day_forecast(day=0, location=prefs['weather']['location']):
    forecast = weather('forecast', location)['forecast']
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

def conditions(day=0, location=prefs['weather']['location']):
    return (weather('forecast', location)
        ['forecast']
        ['simpleforecast']
        ['forecastday']
        [day]
        ['conditions'])

def tomorrow_conditions(location=prefs['weather']['location']):
    return conditions(day=1, location=location)

def today_forecast(day=0, location=prefs['weather']['location']):
    return day_forecast(day=day, location=location)

def tomorrow_forecast(day=1, location=prefs['weather']['location']):
    return day_forecast(day=day, location=location)

def parsesuntime(t):
    return datetime.datetime.strptime(
        t['hour'].rjust(2, '0') + t['minute'], '%H%M')

def sunrise(location=prefs['weather']['location']):
    times = weather('astronomy', location)['sun_phase']['sunrise']
    return parsesuntime(times)

def sunset(location=prefs['weather']['location']):
    times = weather('astronomy', location)['sun_phase']['sunset']
    return parsesuntime(times)

def suntimes(location=prefs['weather']['location']):
    risetime, settime = sunrise(location), sunset(location)
    daylight = settime - risetime

    risefmt = extformat(
        prefs['weather']['sun']['rise_format'],
        sunrise=misc.hoursminutes(risetime, fillchar=''))

    setfmt = extformat(
        prefs['weather']['sun']['set_format'],
        sunset=misc.hoursminutes(settime, fillchar=''))

    dayfmt = extformat(
        prefs['weather']['sun']['daylight_format'],
        daylight=misc.formatdelta(daylight))

    return extformat(
        prefs['weather']['sun']['format'],
        sunrise =risefmt,
        sunset  =setfmt,
        daylight=dayfmt,)

def moon(location=prefs['weather']['location']):
    times = weather('astronomy', location)['moon_phase']
    phase = times['phaseofMoon'].lower()
    percent = times['percentIlluminated']
    graphic = (prefs['weather']['moon']['bright_graphic']
        if int(times['percentIlluminated']) > 50
        else prefs['weather']['moon']['dark_graphic'])

    return extformat(prefs['weather']['moon']['format'],
        **locals())

def main():
    print(today_forecast())
    print(graph())

if __name__ == '__main__':
    main()
