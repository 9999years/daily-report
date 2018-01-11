from bs4 import BeautifulSoup
import urllib
import requests
import datetime

import misc
from prefs import prefs, keys

cache = {}

session = requests.Session()

def url(path=''):
    return urllib.parse.urljoin(prefs['myhomework']['base_url'], path)

def login_cookies():
    global cache
    global session
    if 'cookies' in cache:
        return
    login_page = session.get(url('/login'))
    form = BeautifulSoup(login_page.text, 'html').find(
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

def hw_dict(bs):
    """BeautifulSoup el -> hw dict"""
    global session
    bs = BeautifulSoup(session.get(url(bs.find('a')['href'])).text, 'html')
    fields = bs.find('dl').children
    hw = {}
    for field in fields:
        if isinstance(field, str):
            continue
        dat = next(fields)
        if not isinstance(dat, str):
            dat = dat.text
        if dat == '--':
            continue
        hw[field.text] = dat
    return hw

def homework():
    global session
    login_cookies()
    home = session.get(url('/home'))
    hws = BeautifulSoup(home.text, 'html').find('ul',
        { 'class': 'homework-list' }).find_all('li', { 'class': 'hw-row' })
    assignments = []
    for hw in hws:
        assignments.append(hw_dict(hw))
    return assignments
