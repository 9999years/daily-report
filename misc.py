import prefs
import textwrap

def left_pad(txt, width, char=' '):
    while len(txt) < width:
        txt = char + txt
    return txt

def hrule():
    return prefs.prefs['horiz'] * prefs.prefs['width']

def lerp(min, max, amt):
    """Interpolate from min to max by amt"""
    return amt * (max - min) + min

def between(min, max, val):
    """fraction val is between min and max"""
    return (val - min) / (max - min)

def scale(val, min, max, omin, omax):
    """linear map from a∈[min, max] → b∈[omin, omax]"""
    return (val - min) / (max - min) * (omax - omin) + omin

def format_left(txt, leader='',
        firstline=None, align_leader='right', margin='firstline'):
    firstline = firstline or leader
    margin = len(firstline)
    leader = left_pad(leader, margin) if align_leader == 'right' else leader
    width = prefs.prefs['width'] - margin
    lines = textwrap.wrap(txt, width=width)
    out = f'{firstline}{lines.pop(0)}\n'
    for line in lines:
        out += (f'{leader}{line}\n')
    return out
