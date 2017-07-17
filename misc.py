import prefs

def left_pad(txt, width, char=' '):
    while len(txt) < width:
        txt = char + txt
    return txt

def hrule():
    return '-' * prefs.prefs['width']
