import requests
import urllib

import misc
from prefs import prefs, keys
from formatter import extformat

cache = {}

def query_url(query):
    # {
    #   'format': 'json',
    #   'diagnostics': 'true',
    #   'env': 'store://datatables.org/alltableswithkeys',
    #   'q': query,
    # }
    return ('https://query.yahooapis.com/v1/public/yql?format=json'
        '&diagnostics=true'
        '&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&q='
        + urllib.parse.quote(query))

def query(url):
    global cache
    ret, cache = misc.request_json(url, cache)
    return ret

def stock_query(symbols):
    symblist = '"' + '", "'.join(symbols) + '"'
    return query_url(
        f'select * from yahoo.finance.quotes where symbol in ({symblist})')

def stock_dat(symbols):
    return query(stock_query(symbols))

def stocks(symbols=prefs['stocks']['symbols']):
    dat = stock_dat(symbols)['query']['results']['quote']
    if isinstance(dat, dict):
        # dont iterate over keys
        dat = [dat]
    ret = []
    for symbol in dat:
        if symbol['Currency'] in prefs['stocks']['exclude_currencies']:
            symbol['Currency'] = ''
        ret.append(extformat(prefs['stocks']['format'], symbol))
    return '\n'.join(ret)
