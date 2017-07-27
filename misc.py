import prefs
import textwrap

def left_pad(txt, width=prefs.prefs['width'], char=' '):
    while len(txt) < width:
        txt = char + txt
    return txt

def hrule():
    return prefs.prefs['horiz'] * prefs.prefs['width']

def thinhrule():
    return prefs.prefs['horiz_light'] * prefs.prefs['width']

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

def center(txt, width=prefs.prefs['width'], char=' '):
    spc = (width - len(txt)) / 2
    if isinstance(spc, int):
        return char * spc + txt + char * spc
    else:
        # (not an even amt of space)
        spc = int(spc)
        return char * spc + txt + char * (spc + 1)

def align(left='', center='', right='', width=prefs.prefs['width']):
    """
    returns a string aligned to `width`, with `left`, `right`, and `center` at
    their respective locations in the string. `center` will destructively
    overwrite `left` and `right`, and `left` will overwrite `right`.

    like a stronger left_pad
    """
    r = left_pad(right, width)
    lr = left + r[len(left):]
    c = width // 2
    halfc = len(center) // 2
    return lr[:c - halfc] + center + lr[c + halfc:]

def hourminute(time):
    return time.strftime('%I:%M%p')

def formatdelta(time, clock=12):
    days = time.days
    hrs  = time.seconds // 3600 # 60 × 60
    ampm = ''
    if clock == 12:
        if hrs > 12:
            hrs -= 12
            ampm = 'PM'
        else:
            ampm = 'AM'

    secs = time.seconds  % 3600
    mins = secs // 60
    secs = secs  % 60
    ret = ''
    if days != 0:
        ret += f'{days} days, '
    ret += f'{hrs: 2}:{mins:02}'
    if secs != 0:
        ret += f':{secs:02}'
    ret += ampm
    return ret
