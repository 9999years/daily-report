import requests
import urllib
import json

import misc
from prefs import prefs, keys
from formatter import extformat

cache = {}

def query(url):
    """
    local wrapper around misc.request_json
    performs caching
    """
    global cache
    ret, cache = misc.request_json(url, cache)
    return ret

def yahoo_query(url):
    """
    local wrapper around misc.request_json
    performs caching
    """
    global cache
    ret, cache = misc.request_json(url, cache)
    if 'query' in ret:
        ret = cache[url] = ret['query']['results']['quote']
    return ret

def google_query(url):
    """
    local wrapper around misc.request
    performs caching
    """
    global cache
    ret, cache = misc.request(url, cache)
    if isinstance(ret, str):
        # google returns a `// [` before and a `]` after the data we can get rid
        # of with a slice
        ret = cache[url] = json.loads(ret[4:])
    return ret

def yahoo_query_url(query):
    """
    takes a YQL query like
        select * from yahoo.finance.quotes where symbol in ("TLSA", "^GSPC")
    and returns a correctly encoded URL that can be requested and parsed as json
    with query or misc.request_json
    """
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

def google_query_url(symbols):
    # https://github.com/hongtaocai/googlefinance
    symblist = ','.join(symbols)
    # a deprecated but still active & correct api
    # {
    #   'client': 'ig',
    #   'q': symblist,
    # }
    return ('http://finance.google.com/finance/info?client=ig&q='
        + urllib.parse.quote(symblist))

def yahoo_stock_query(symbols):
    """
    generates the yahoo finance query url for a list of symbols using
    yahoo_query_url

    takes ONE argument, a list/tuple of symbols; not multiple arguments

    generally don't call this alone; call symbol_list to deal with possible
    dict symbols (if applicable)
    """
    symblist = '"' + '", "'.join(symbols) + '"'
    return yahoo_query_url(
        f'select * from yahoo.finance.quotes where symbol in ({symblist})')

def google_dat(symbols):
    symbols = misc.listifier(symbols)
    dat = google_query(google_query_url(symbols))

    fullnames = {
        'id'       : 'ID',
        't'        : 'StockSymbol',
        'e'        : 'Index',
        'l'        : 'LastTradePrice',
        'l_cur'    : 'LastTradeWithCurrency',
        'ltt'      : 'LastTradeTime',
        'lt_dts'   : 'LastTradeDateTime',
        'lt'       : 'LastTradeDateTimeLong',
        'div'      : 'Dividend',
        'yld'      : 'Yield',
        's'        : 'LastTradeSize',
        'c'        : 'Change',
        'cp'       : 'ChangePercent',
        'el'       : 'ExtHrsLastTradePrice',
        'el_cur'   : 'ExtHrsLastTradeWithCurrency',
        'elt'      : 'ExtHrsLastTradeDateTimeLong',
        'ec'       : 'ExtHrsChange',
        'ecp'      : 'ExtHrsChangePercent',
        'pcls_fix' : 'PreviousClosePrice'
    }

    ret = []

    for symbol in dat:
        # convert short keys to long keys
        for key in symbol:
            if key in fullnames:
                symbol[fullnames[key]] = symbol.pop(key)
        ret.append(symbol)

    return ret

def stock_dat(symbols):
    """
    gets data for a list of symbols
    """
    symbols = misc.listifier(symbols)

    dat = yahoo_query(yahoo_stock_query(symbols))

    dat = misc.listifier(dat)

    ret = []
    for s in dat:
        if (s['PreviousClose'] is None and
            s['PercentChange'] is None and
            s['Volume'] is None):
            # yahoo finance isn't able to return data
            # e.g. in case of dow jones (^DJI)
            # default to google finance
            # see https://stackoverflow.com/a/3681992/5719760
            ret.append(google_dat(s['symbol']))
        else:
            ret.append(dat)
    return ret

def symbol_list(symbols):
    """
    prefs.json allows overriding the format on a symbol-by-symbol basis
    so, prefs.stocks.symbols isnt always 100% a string list
    """
    if isinstance(symbols, str):
        return [symbols]
    ret = []
    for s in symbols:
        if isinstance(s, str):
            ret.append(s)
        elif isinstance(s, dict):
            ret.append(s['symbol'])
        else:
            ret.append(str(s))
    return ret

def stocks(symbols=prefs['stocks']['symbols']):
    """
    assembles and formats output from a list/tuple of symbols

    only takes one argument! might support *args in the future, but not now
    """
    symbols = misc.listifier(symbols)

    dat = stock_dat(symbol_list(symbols))
    dat = misc.listifier(dat)
    ret = []
    for symbol, key in zip(dat, symbols):
        if isinstance(key, dict):
            fstr = key['format']
        else:
            fstr = prefs['stocks']['format']
        # sepearte formatting for each symbol (optional dict)
        if symbol['Currency'] in prefs['stocks']['excluded_currencies']:
            symbol['Currency'] = ''
        ret.append(extformat(fstr, symbol,
            default=extformat(prefs['stocks']['format'], symbol)))
    return '\n'.join(ret)

def main():
    print(stocks())

if __name__ == '__main__':
    main()
