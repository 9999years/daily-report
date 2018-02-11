from bs4 import BeautifulSoup
import bs4
import urllib
import requests
import datetime

import misc
from prefs import prefs, keys
from formatter import extformat
import dates

cache = {}

session = requests.Session()

empty_hw = {
    'name': '',
    'class_name': '',
    'due': dates.zonify(datetime.datetime.today()),
    'reminder': '',
    'priority': '',
    'info': '',
    'type': '',
}

def url(path=''):
    return urllib.parse.urljoin(prefs['myhomework']['base_url'], path)

def login():
    global cache
    global session
    if 'cookies' in cache:
        return
    login_page = session.get(url('/login'))
    form = BeautifulSoup(login_page.text, 'html.parser').find(
        'form', { 'class': 'login-form' })
    payload = {
        'username': keys['myhomework']['username'],
        'password': keys['myhomework']['password'],
        'csrfmiddlewaretoken': form.find('input',
            { 'name': 'csrfmiddlewaretoken' })['value'],
    }
    login_url = url(form['action'])
    login_response = session.post(login_url, data=payload)
    cache['cookies'] = session.cookies.get_dict()

def hw_date(s):
    """Wed, Jan 9, 2019 OR Wed, Jan 9"""
    fmts = [
        '%a, %b %d, %I:%M %p, %Y', # Wed, Jan 9, 6:30 PM, 2019
        '%a, %b %d, %Y',           # Wed, Jan 9, 2019
        '%a, %b %d, %I:%M  %p',    # Wed, Jan 9, 6:30 PM
        '%a, %b %d',               # Wed, Jan 9
    ]
    for fmt in fmts:
        try:
            d = datetime.datetime.strptime(s, fmt)
            if '%Y' not in fmt:
                d = d.replace(year=datetime.date.today().year)
            break
        except ValueError:
            continue
    # i hope youre turning in hw in the same tz as your computer!
    return dates.zonify(d)

def hw_dict(bs):
    """BeautifulSoup el -> hw dict"""
    global session, empty_hw
    bs = BeautifulSoup(session.get(url(bs.find('a')['href'])).text, 'html.parser')
    fields = bs.find('dl')
    hw = {}
    hw.update(empty_hw)
    while fields is not None:
        fields = fields.find_next('dt')
        if fields is None:
            break
        dat = fields.find_next('dd')
        if dat is None:
            continue
        dat = dat.text
        if dat != '--' and dat.strip() != '':
            hw[fields.text] = dat
    if 'Date' in hw:
        hw['Due Date'] = hw['Date']
        del hw['Date']
    if 'Due Date' in hw:
        hw['Due Date'] = hw_date(hw['Due Date'])
    hw = misc.translate_keys(hw, {
        'Description': 'name',
        'Class': 'class_name',
        'Due Date': 'due',
        'Reminder': 'reminder',
        'Priority': 'priority',
        'Additional Info': 'info',
        'Type': 'type',
    })
    return hw

def homework():
    global session
    if 'homework' in cache:
        return cache['homework']
    login()
    home = session.get(url('/home'))
    hws = BeautifulSoup(home.text, 'html.parser').find('ul',
        { 'class': 'homework-list' }).find_all('li', { 'class': 'hw-row' })
    assignments = []
    for hw in hws:
        assignments.append(hw_dict(hw))
    cache['homework'] = assignments
    return assignments

def due(day=1):
    hws = homework()
    ret = []
    _, day = dates.today_times(day)
    for hw in hws:
        if 'due' in hw and hw['due'] <= day:
            ret.append(misc.format_left(extformat(
                    prefs['myhomework']['assignment_format'], hw
                ), firstline=prefs['myhomework']['check']))
    return ''.join(ret).rstrip()

def main():
    print(due())

if __name__ == '__main__':
    main()
