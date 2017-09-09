import requests
import urllib
import json

import misc
from time import sleep
from prefs import prefs, keys
from formatter import extformat

cache = {}

# we merge stocks with this so keyerrors dont happen
emptyquote = {
    'AfterHoursChangeRealtime'                       ,
    'AnnualizedGain'                                 ,
    'Ask'                                            ,
    'AskRealtime'                                    ,
    'AverageDailyVolume'                             ,
    'Bid'                                            ,
    'BidRealtime'                                    ,
    'BookValue'                                      ,
    'Change'                                         ,
    'ChangeFromFiftydayMovingAverage'                ,
    'ChangeFromTwoHundreddayMovingAverage'           ,
    'ChangeFromYearHigh'                             ,
    'ChangeFromYearLow'                              ,
    'ChangePercentRealtime'                          ,
    'ChangeRealtime'                                 ,
    'Change_PercentChange'                           ,
    'ChangeinPercent'                                ,
    'Commission'                                     ,
    'Currency'                                       ,
    'DaysHigh'                                       ,
    'DaysLow'                                        ,
    'DaysRange'                                      ,
    'DaysRangeRealtime'                              ,
    'DaysValueChange'                                ,
    'DaysValueChangeRealtime'                        ,
    'DividendPayDate'                                ,
    'DividendShare'                                  ,
    'DividendYield'                                  ,
    'EBITDA'                                         ,
    'EPSEstimateCurrentYear'                         ,
    'EPSEstimateNextQuarter'                         ,
    'EPSEstimateNextYear'                            ,
    'EarningsShare'                                  ,
    'ErrorIndicationreturnedforsymbolchangedinvalid' ,
    'ExDividendDate'                                 ,
    'FiftydayMovingAverage'                          ,
    'HighLimit'                                      ,
    'HoldingsGain'                                   ,
    'HoldingsGainPercent'                            ,
    'HoldingsGainPercentRealtime'                    ,
    'HoldingsGainRealtime'                           ,
    'HoldingsValue'                                  ,
    'HoldingsValueRealtime'                          ,
    'LastTradeDate'                                  ,
    'LastTradePriceOnly'                             ,
    'LastTradeRealtimeWithTime'                      ,
    'LastTradeTime'                                  ,
    'LastTradeWithTime'                              ,
    'LowLimit'                                       ,
    'MarketCapRealtime'                              ,
    'MarketCapitalization'                           ,
    'MoreInfo'                                       ,
    'Name'                                           ,
    'Notes'                                          ,
    'OneyrTargetPrice'                               ,
    'Open'                                           ,
    'OrderBookRealtime'                              ,
    'PEGRatio'                                       ,
    'PERatio'                                        ,
    'PERatioRealtime'                                ,
    'PercebtChangeFromYearHigh'                      ,
    'PercentChange'                                  ,
    'PercentChangeFromFiftydayMovingAverage'         ,
    'PercentChangeFromTwoHundreddayMovingAverage'    ,
    'PercentChangeFromYearLow'                       ,
    'PreviousClose'                                  ,
    'PriceBook'                                      ,
    'PriceEPSEstimateCurrentYear'                    ,
    'PriceEPSEstimateNextYear'                       ,
    'PricePaid'                                      ,
    'PriceSales'                                     ,
    'SharesOwned'                                    ,
    'ShortRatio'                                     ,
    'StockExchange'                                  ,
    'Symbol'                                         ,
    'TickerTrend'                                    ,
    'TradeDate'                                      ,
    'TwoHundreddayMovingAverage'                     ,
    'Volume'                                         ,
    'YearHigh'                                       ,
    'YearLow'                                        ,
    'YearRange'                                      ,
    'symbol'                                         ,
}

# numeric key values we should convert to numbers instead of strings
numerkeys = [
    'Ask',
    'AverageDailyVolume',
    'Bid',
    'AskRealtime',
    'BidRealtime',
    'BookValue',
    'Change',
    'ChangeRealtime',
    'AfterHoursChangeRealtime',
    'DividendShare',
    'EarningsShare',
    'EPSEstimateCurrentYear',
    'EPSEstimateNextYear',
    'EPSEstimateNextQuarter',
    'DaysLow',
    'DaysHigh',
    'YearLow',
    'YearHigh',
    'HoldingsGainPercent',
    'AnnualizedGain',
    'HoldingsGain',
    'HoldingsGainPercentRealtime',
    'HoldingsGainRealtime',
    'MarketCapitalization',
    'MarketCapRealtime',
    'EBITDA',
    'ChangeFromYearLow',
    'PercentChangeFromYearLow',
    'ChangePercentRealtime',
    'ChangeFromYearHigh',
    'PercebtChangeFromYearHigh',
    'LastTradePriceOnly',
    'FiftydayMovingAverage',
    'TwoHundreddayMovingAverage',
    'ChangeFromTwoHundreddayMovingAverage',
    'PercentChangeFromTwoHundreddayMovingAverage',
    'ChangeFromFiftydayMovingAverage',
    'PercentChangeFromFiftydayMovingAverage',
    'Open',
    'PreviousClose',
    'PricePaid',
    'ChangeinPercent',
    'PriceSales',
    'PriceBook',
    'PERatio',
    'PERatioRealtime',
    'PEGRatio',
    'PriceEPSEstimateCurrentYear',
    'PriceEPSEstimateNextYear',
    'SharesOwned',
    'ShortRatio',
    'OneyrTargetPrice',
    'Volume',
    'HoldingsValue',
    'HoldingsValueRealtime',
    'DaysValueChange',
    'DaysValueChangeRealtime',
    'DividendYield',
    'PercentChange',
]

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
    bad_request_str = 'httpserver.cc: Response Code 400\n'
    for i in range(prefs['max_retries']):
        ret, cache = misc.request(url, cache)
        if isinstance(ret, str):
            if ret != bad_request_str:
                # google returns a `// [` before and a `]` after the data we can get rid
                # of with a slice
                ret = cache[url] = json.loads(ret[4:])
                break
            else:
                ret = []
                sleep(1)
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
    #   'infotype': 'infoquoteall',
    #   'q': symblist,
    # }
    return ('http://finance.google.com/finance/info?client=ig'
        + '&infotype=infoquoteall&q='
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

def fill_quote(quote):
    """
    fill missing fields in a quote from google with empty strings
    to prevent keyerrors
    """
    for k in emptyquote:
        if k not in quote:
            quote[k] = ''
    return quote

def google_dat(symbols):
    symbols = misc.listifier(symbols)
    dat = google_query(google_query_url(symbols))

    fullnames = {
        'op'       : 'Open',
        'name'     : 'Name',
        'hi'       : 'DaysHigh',
        'hi52'     : 'YearHigh',
        'lo'       : 'DaysLow',
        'lo52'     : 'YearLow',
        'e'        : 'StockExchange',
        'l'        : 'LastTradePriceOnly',
        'lt'       : 'LastTradeDateTime',
        'ltt'      : 'LastTradeTime',
        'ltt_dts'  : 'LastTradeISOTime',
        'el'       : 'AfterHoursLastTradePriceOnly',
        'elt'      : 'AfterHoursLastTradeDateTime',
        'mc'       : 'MarketCapitalization',
        't'        : 'Symbol',
        'eps'      : 'EarningsShare',
        'c_fix'    : 'Change',
        'ec_fix'   : 'AfterHoursChange',
        'cp_fix'   : 'PercentChange',
        'ecp_fix'  : 'AfterHoursPercentChange',
        'pcls_fix' : 'PreviousClose',
        'pe'       : 'PERatio',
        'yld'      : 'DividendYield',
        'div'      : 'Dividend',
        'inst_own' : 'InstitutionShares',
        's'        : 'LastTradeSize',
    }

    ret = []

    for symbol in dat:
        # convert short keys to long keys
        out = {}
        for key in symbol:
            if key in fullnames:
                out[fullnames[key]] = symbol[key]
        ret.append(fill_quote(out))

    return ret

def yahoo_dat(symbols):
    """
    gets yahoo data for a list of symbols
    """
    symbols = misc.listifier(symbols)

    dat = yahoo_query(yahoo_stock_query(symbols))

    return misc.listifier(dat)

def extfloat(s):
    """
    more leniant float parsing
    """
    if isinstance(s, float) or isinstance(s, int):
        return s
    elif s is None or len(s) == 0:
        return None
    else:
        striplast = True
        if s[-1] == 'M':
            factor = 1e6
        elif s[-1] == 'B':
            factor = 1e9
        elif s[-1] == 'T':
            factor = 1e12
        else:
            striplast = False
            factor = 1
        if striplast:
            s = s[:-1]
        new_s = s.replace('%', '').replace(',', '')

        return float(new_s) * factor

def stock_dat(symbols, source=prefs['stocks']['source']):
    dat = yahoo_dat(symbols)
    # if source == 'yahoo':
        # dat = yahoo_dat(symbols)
    # else: # google
        # dat = google_dat(symbols)
    ret = []
    for s, orig in zip(dat, symbols):
        # if (('PreviousClose' not in s or s['PreviousClose'] is None) and
            # ('PercentChange' not in s or s['PercentChange'] is None) and
            # ('Volume'        not in s or s['Volume']        is None)):
            # # yahoo finance isn't able to return data
            # # e.g. in case of dow jones (^DJI)
            # # default to google finance
            # # see https://stackoverflow.com/a/3681992/5719760
            # # replace ^ with . for eg ^DJI (yahoo) to .DJI (google)
            # tmp = google_dat(orig.replace('^', '.'))
            # if len(tmp) > 0:
                # s = tmp[0]
            # else:
                # s = None

        if s is not None:
            for numkey in numerkeys:
                if numkey in s:
                    s[numkey] = extfloat(s[numkey])
            ret.append(fill_quote(s))
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

def format_stock(dat, symbol):
    fstr = prefs['stocks']['format']
    if isinstance(symbol, dict):
        if 'style' in symbol:
            fstr = prefs['stocks'][symbol['style'] + '_format']
        if ('source' in symbol
            and symbol['source'] != prefs['stocks']['source']):
            dat = stock_dat(symbol['Symbol'], symbol['source'])
        if 'display_symbol' in symbol:
            dat['Symbol'] = symbol['display_symbol']

    if dat['Currency'] in prefs['stocks']['excluded_currencies']:
        dat['Currency'] = ''

    return extformat(fstr, dat,
        default=lambda: extformat(prefs['stocks']['format'], dat))

def stocks(symbols=prefs['stocks']['symbols']):
    """
    assembles and formats output from a list/tuple of symbols

    only takes one argument! might support *args in the future, but not now
    """
    symbols = misc.listifier(symbols)

    dat = misc.listifier(stock_dat(symbol_list(symbols)))

    ret = []
    for symdat, symbol in zip(dat, symbols):
        ret.append(format_stock(symdat, symbol))

    return '\n'.join(ret)

def main():
    print(stocks())

if __name__ == '__main__':
    main()
