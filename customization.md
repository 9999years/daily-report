# Customization

`prefs.json` is designed to make customization of The Daily Report flexible and
rich.

In the abstract, The Daily Report defines functions that return strings of
potentially interesting content. The Daily Report then interpolates these
functions into various [format strings][fmt-strings], which are very similar in
syntax to Python’s built-in `f`-string literals but slightly more powerful,
supporting the execution of arbitrary code and escapes, rather than just single
expressions. The formatting is done with my `extendedformatter` module.

All format strings can either be a single string key or an array of strings,
which are then joined with newlines (this makes long format sequences much more
readable).

The primary format string is `prefs.format` (`prefs` referring to `prefs.json`,
with `.format` referring to the `format` key; Javascript-syntax is used here for
in favor of Python’s, because `prefs['format']` is unnecessarily verbose).

All format strings have access to the global format variables, but many have
access to their own, sometimes nested format variables.

For example, the format of `{sun}`’s output is defined in
`prefs.weather.sun_format`, which has access to `{sunrise}` (the sunrise time),
`{daylight}` (the length of the day), and `{sunset}` (the sunset time). From
there, `{sunrise}` is defined by `prefs.weather.sunrise_format`. It’s a little
bit silly and certainly rather verbose but it allows you to truly make The Daily
Report your own.

All format variables are functions and must be called with parenthesis, though
they may be written without them in the documentation for brevity; this means
that format functions you don’t call aren’t evaluated, saving you time /
bandwidth / processing power.  Additionally, API calls are cached when possible,
saving requests.

All function parameters are optional, and may be omitted. However, sometimes it
is not sensible to do so; I assume you’ll want `twitter` to print the tweets of
someone who’s *not* @dril, for example. Options are written unbracketed, as
normal arguments, but are, again, optional.

Okay, that’s a bit of a lie; a few functions, like `center()`, require an
argument; usually, this will be clear. If this is the case, optional arguments
*are* written in brackets.

## Global Format Variables

These format variables are available in *all* format strings, whereas local
format variables are only available in some; `sun` can be used in any format
string, but `sunrise` can only be used in `prefs.weather.sun.format`.

### `hrule`

Definition: `misc.hrule`.

Description: A horizontal rule formed by repeating `prefs.horiz` `prefs.width`
times. Multiple consecutive `{hrule}`s and `{thinhrule}`s are compressed into a
single `{hrule}` in final output.

Example output:

    ================================

### `thinhrule`

Definition: `misc.thinhrule`.

Description: A thinner horizontal rule, using `prefs.horiz_light` instead of
`prefs.horiz` for the fill character. Multiple `{thinhrule}`s are condensed
into a single `{thinhrule}` in final output.

Example output:

    --------------------------------

### `center(string, [width=prefs.width,] [fillchar=' '])`

Definition: `misc.center`

Description: Centers its input; like `str.center(width, fill_char)` but the
width parameter is optional, defaulting to `prefs.width`.

Example output: `repr(center(isodate()))`

    '           2017-08-04           '

(`repr` included to show the quote boundaries.)

### `right(string, [width=prefs.width,] [fillchar=' '])`

Definition: `misc.right`

Alias: `left_pad`

Description: Right-aligns its input; like `str.rjust(width, fill_char)` but the
width parameter is optional, defaulting to `prefs.width`.

### `align(left='', center='', right='', width=prefs.width, fillchar=' ')`

Definition: `misc.align`

Description: A combination of `right` and `center`; takes three
positional arguments `left`, `center`, and `right` or any number of keyword
arguments and justifies the output, left-aligning `left`, centering `center`,
and right-aligning `right` (to width `prefs.width` by default or any arbitrary
width with the `width` keyword-argument).

All arguments are optional but using one without the others is a bit
self-defeating.

Example output: `align('left', 'center', 'right')`

    left         center        right

### `today`

Definition: `dates.today_date(day=0)`

Description: Today’s date, human-style. From `prefs.dates.today_format`, as a
[`strftime` escape][strftime]. `day` argument specifies an offset, to get the
date for tomorrow or yesterday or a week from now.

Example output: `today is sunday, july 30`

### `iso_date`

Definition: `dates.iso_date`

Description: [ISO 8601][iso8601]-compliant date.

Example output: `2017-07-30`

### `now_hm(fillchar='')`

Definition: `dates.now_hm`

Description: Outputs the current time in hours/minutes. If `prefs.dates.hours`
is 24, `now_hm` will output 24-hour times. Note that output can always be a
constant width with the `fillchar` kwarg set to `' '`, for easy alignment.

Example output: ` 4:43PM`

### `calendar`

Definition: `dates.events(day=0)`

Description: Outputs two sections, separated by a `thinhrule`. The first is all
day events, formatted with `prefs.dates.all_day` in a left-column and post-fixed
with `(day x of y)` with `x` being the current day in the event and `y` being
the event’s duration in days.

The second section is the current day’s events, formatted with their time (hours
and minutes) in the left column.

An optional `day` parameter offsets the output by a given number of days; pass
`day=1` to get tomorrow’s schedule, and `day=2` for the day after tomorrow’s
schedule, etc.

Example output:

    all day ║ summer break (day 43
            ║ of 60)
    ────────────────────────────────
    12:00PM ║ work at citysburg
     6:00PM ║ cook egg drop soup
            ║ with friends

### `countdown`

Definition: `dates.today_countdowns`

Description: A list of countdowns, calculated as the days until the next
`prefs.calendar.max_countdowns` in the calendars that match
`prefs.calendar.countdown_pat`.

Example output:

      5 ║ visit jay (2017-08-04)
     28 ║ move in day (2017-08-27)
    148 ║ christmas (2017-12-25)
    274 ║ birthday (2018-04-30)

### `todo`

Definition: `dates.today_todos`

Description: A list of todos, generated from today’s events in the calendars
that match `prefs.calendar.todo_pat`.

Example output:

    [] get toothpaste

### `work`

Definition: `dates.today_work`

Description: Like `calendar` but for work shifts, from a work calendar, to let
you separate the output.

Example output:


### `twitter(handle='dril')`

Definition: `twtr.last`

Description: The last status from the given Twitter user

Example output: `twitter('tiny_star_field')`

    @tiny_star_field: * 　 　　 ˚
    ✵        ·   .         · .  ·
         ˚  ˚  · ✦       ✵        ·
    ⋆  .  ·
    67 likes, 46 rts
    2017-08-04 10:29:02 PM

(Perhaps not the best example, because the output is formatted [i.e. the
original tweet’s linebreaks are ignored] so the neat grid that
`@tiny_star_field` generates is lost... TODO: Keep original line-breaks by
doubling them)

### `maze`

Definition: `maze.gen(w=prefs.width, h=prefs.maze.height)`

Description: Generates a tiny maze of width `w` and height `h`!

Example output:

    S─┬───┬─────┬───┬─────┬───────┐
    │ ╰─┐ │ │ │ │ │ │ ╭─┐ └─╮ ──╮ │
    ├─┐ │ ┌─┤ ╰───┤ │ │ ╰── ├───┘ │
    │ │ │ │ └─┬── ├───┤ ┌───╯ ──╮ │
    │ ──┴───╮ │ ╭─┘ │ │ │ ──┬── │ │
    ├───┬── │ │ │ ┌─╯ │ ├── │ ──┴─┤
    ├── │ ╭─┴─┴─┐ │ ╭─┤ └─╮ ╰───╮ │
    │ ──╯ │ ┌── └─┘ │ ╰── └─────┘ │
    └───────┴───────┴─────────────E

### `forecast`

Definition: `weather.today_forecast(day=0)`

Description: Today’s forecast, as defined by `prefs.weather.forecast_format`.
Accepts an arbitrary day-offset; a builtin `tmrw_forecast` exists but not for
further days; day-after-tomorrow forecasts can be shown with `forecast(2)`

Example output: `60-82°F, 10%p`

### `tmrw_forecast`

Definition: `weather.tomorrow_forecast`

Description: Identical to `forecast` but for tomorrow instead of the current day.

### `conditions`

Definition: `weather.conditions(day=0)`

Description: Today’s conditions.

Example output: `Chance of thunderstorms`

### `tmrw_conditions`

Definition: `weather.tomorrow_conditions`

Description: See above. Wrapper around `weather.conditions(day=1)`

Example output: `Clear`


### `weather_graph`

Definition: `weather.graph`

Description: Prints a graph of the 24-hour forecast. `×` marks (or whatever’s in
`prefs.weather.chars.temp`) denote temperatures, with the axis marks printed on
the left. `·` marks denote precipitation chances, with axis marks printed on the
right. `¤` marks indicate that the precipitation chance and temperature occupies
the same space for that time. Hours are printed at the bottom, at multiples of
3, and vertical bars are printed at noon / midnight.

Example output:

    81║¤·······       │          ║15
    78║ ×××           │  ×××××   ║12
    75║   │××         │ ×     ×  ║ 9
    73║   │  ××¤···   ××       × ║ 6
    70║   │     ×× ¤¤×│         ¤║ 3
    68║   │       ×  ··········· ║ 0
    °F×9  12 3  6  9  12 3  6  9 ·%p


### `sun`

Definition: `weather.suntimes`

Description: Outputs sun information, formatted according to
`prefs.weather.sun.format`.

Example output:

    6:08AM ↑      14:14     8:22PM ↓

### `moon`

Definition: `weather.moon`

Description: Shows moon phase and illumination percent, formatted according to
`prefs.weather.moon.format`.

Example output:

         ○ first quarter @ 53%

## Local Format Variables

### `forecast`

variable | description | example
---------|-------------|---------
`low` | the lower predicted temperature for the day. | 24
`high` | the upper predicted temperature for the day. | 68
`conds` | the predicted conditions for the day. | clear
`summary` | (I forget exactly what this looks like, stuff it in and find out!) |
`day_data` | raw data |
`txt_data` | raw data |

### `moon`

variable | description | example
---------|-------------|---------
`phase` | the moon’s phase | Waxing gibbous
`percent` | the moon’s illumination percentage | 55
`graphic` | `prefs.moon.dark_graphic` if `percentage` < 50, `prefs.moon.bright_graphic` otherwise | ○

### `sun`

variable | description | example
---------|-------------|---------
`sunrise` | sunrise time | 5:28AM
`sunset` | sunset time | 8:50PM
`daylight` | daylight time, in hours and minutes | 14:28

### `twitter`

variable | description | example
---------|-------------|---------
`date` | datetime of tweet |
`pretty_format` | format in `prefs.twitter.pretty_format` |
everything else in a `tweet.AsDict()` ||
