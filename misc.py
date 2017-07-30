import textwrap
import datetime
import re
from string import Formatter

# local
from prefdicts import prefs, keys
import weather
import dates
import misc
import twtr
# incredibly silly, please ignore
import maze as _maze

def format(msg, extra_vars={}):
    # :Tab /=\|\./l1r1r0l0

    hrule           =    misc.hrule
    thinhrule       =    misc.thinhrule
    center          =    misc.center
    right           =    misc.right
    left_pad        =    misc.right
    align           =    misc.align
    fill            =    misc.fill
    today           =   dates.today_date
    now_hm          =   dates.now_hm
    iso_date        =   dates.iso_date
    calendar        =   dates.events
    countdown       =   dates.today_countdowns
    todo            =   dates.today_todos
    work            =   dates.today_work
    twitter         =    twtr.last
    maze            =   _maze.from_prefs
    moon            = weather.moon
    forecast        = weather.today_forecast
    tmrw_forecast   = weather.tomorrow_forecast
    conditions      = weather.conditions
    tmrw_conditions = weather.tomorrow_conditions
    weather_graph   = weather.graph
    sun             = weather.suntimes

    # use locals, but override with extra_vars
    formatting_variables = locals()
    formatting_variables.update(extra_vars)

    formatter = Formatter()

    literal_txt     = 0
    replacement_txt = 1
    format_spec     = 2
    conversion_spec = 3

    orig_msg = '\n'.join(msg) if isinstance(msg, list) else msg
    msg = ''
    for field in formatter.parse(orig_msg):
        # field is a tuple of
        # (literal text, replacement text, conversion, format spec)
        # 'locals are {locals()!r:s}'
        # corresponds to ('locals are', 'locals()', 'r', 's')
        msg += field[literal_txt]

        if field[replacement_txt] is not None:
            field_txt = eval(field[replacement_txt],
                    globals(), formatting_variables)
            if field[conversion_spec] is not None:
                conversion_mapping = {
                    'center': misc.center,
                    'right': misc.right,
                    'fill': misc.fill,
                }

                def abbreviate(a, b):
                    nonlocal conversion_mapping
                    conversion_mapping[b] = conversion_mapping[a]

                abbreviate('center', 'c')
                abbreviate('right', 'r')
                abbreviate('fill', 'f')

                if field[conversion_spec] in conversion_mapping:
                    field_txt = conversion_mapping[field[conversion_spec]](field_txt)
                else:
                    field_txt = formatter.convert_field(
                        field_txt, field[conversion_spec])

            if len(field[format_spec]) > 0:
                field_txt = formatter.format_field(
                    field_txt, field[format_spec])
            else:
                field_txt = str(field_txt)

            msg += field_txt

    msg = misc.deduplicate_rules(msg)

    return msg

def fill(txt, width=prefs['width'], **kwargs):
    return textwrap.fill(txt, **kwargs)

def left(txt, width=prefs['width'], fillchar=' '):
    return txt.ljust(width, fillchar)

# keep procedural public api
def right(txt, width=prefs['width'], fillchar=' '):
    return txt.rjust(width, fillchar)

left_pad = right

def hrule():
    return prefs['horiz'] * prefs['width']

def thinhrule():
    return prefs['horiz_light'] * prefs['width']

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
    leader = leader.rjust(margin) if align_leader == 'right' else leader
    width = prefs['width'] - margin
    lines = textwrap.wrap(txt, width=width)
    out = f'{firstline}{lines.pop(0)}\n'
    for line in lines:
        out += (f'{leader}{line}\n')
    return out

def center(txt, width=prefs['width'], fillchar=' '):
    return txt.center(width, fillchar)

def align(left='', center='', right='', width=prefs['width']):
    """
    returns a string aligned to `width`, with `left`, `right`, and `center` at
    their respective locations in the string. `center` will destructively
    overwrite `left` and `right`, and `left` will overwrite `right`.

    like a stronger left_pad
    """
    lr = left + right.rjust(width)[len(left):]

    c = width // 2
    halfc = int(c - len(center) / 2)

    return lr[:halfc] + center + lr[halfc + len(center):]

def hoursminutes(time, pad=' '):
    hrs = datetime.datetime.strftime(time, '%I')
    # pad with spaces instead of 0s
    if hrs[0] == '0':
        hrs = pad + hrs[1:]
    return hrs + ':' + datetime.datetime.strftime(time, '%M%p')

def formatdelta(time, clock=12):
    days = time.days
    hrs  = time.seconds // 3600 # 60 × 60
    if clock == 12:
        if hrs > 12:
            hrs -= 12
            ampm = 'PM'
        else:
            ampm = 'AM'
    else:
        ampm = ''

    secs = time.seconds  % 3600
    mins = secs // 60
    secs = secs  % 60
    ret = ''
    if days != 0:
        ret += f'{days} days, '
    ret += f'{hrs: 2}:{mins:02}'
    if secs != 0:
        ret += f'::{secs:02}'
    ret += ampm
    return ret

def deduplicate_rules(msg):
    # empty sections surrounded by hrules can look silly
    # make them one hrule instead
    # replace multiple thin hrules with one thinhrule
    msg = re.sub('((' + thinhrule() + r')\n*){2,}',
        thinhrule() + '\n', msg)
    # but all regular hrules or mixed thin/regular hrules turn into regular
    # hrules
    return re.sub('((' + hrule() + '|' + thinhrule() + r')\n*){2,}',
        hrule() + '\n', msg)
