from bs4 import BeautifulSoup
import requests
import re

from prefs import prefs
import misc
from formatter import extformat

def random_parser():
    article = requests.get('https://en.m.wikipedia.org/wiki/Special:Random#/random')
    soup = BeautifulSoup(article.text, 'html.parser')
    return soup

def random():
    soup = random_parser()
    title = soup.find('h1', id='section_0').text
    body = soup.find('div', 'mw-parser-output')
    first = body.find('p').text
    first = re.sub('\[\d+\]', '', first)
    return extformat(prefs['wikipedia']['format'], locals())

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='a random wikipedia snippet'
    )

    parser.add_argument('-w', '--width', type=int, default=80)

    args = parser.parse_args()

    print(random())
