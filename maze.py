#! /usr/local/bin/python3

# heavily modified, but original algs by Vidar 'koala_man' Holen
# vidarholen.net
# http://www.vidarholen.net/~vidar/generatemaze.py

import random
from prefdicts import prefs, keys

# so we can deal with directions with binary addition / subtraction
# north and south = north + south or north | south yknow that kinda deal
north = 0b1000
east  = 0b0001
south = 0b0010
west  = 0b0100


def maze_char(directions):
    chars = [
        [' ', ' '], # 0
        ['╶', '╶'], # r
        ['╷', '╷'], # d
        ['╭', '┌'], # r | d
        ['╴', '╴'], # l
        ['─', '─'], # l | r
        ['╮', '┐'], # l | d
        ['┬', '┬'], # l | r | d
        ['╵', '╵'], # u
        ['╰', '└'], # u | r
        ['│', '│'], # u | d
        ['├', '├'], # u | d | r
        ['╯', '┘'], # u | l
        ['┴', '┴'], # u | l | r
        ['┤', '┤'], # u | l | d
        ['┼', '┼'], # u | l | d | r
    ]
    if prefs['maze']['style'] == 'round':
        chars = [k[0] for k in chars]
    elif prefs['maze']['style'] == 'square':
        chars = [k[1] for k in chars]
    elif prefs['maze']['style'] == 'random':
        chars = [k[random.randint(0, 1)] for k in chars]
    else:
        chars = [chr(random.randint(0x2500, 0x27ff)) for k in chars]

    if prefs['maze']['halves'] == False:
        chars[north] = chars[south] = '│'
        chars[east] = chars[west] = '─'

    return chars[directions]


class Cell():
    def __init__(self,
            right=True,
            bottom=True,
            captured=False,
            backtrack=0,
            solution=False):
        self.right     = right
        self.bottom    = bottom
        self.captured  = captured
        self.backtrack = backtrack
        self.solution  = solution

    def directions(self, right, bottom):
        return (int(self.right) * north
            + int(self.bottom)  * west
            + int(bottom.right) * south
            + int(right.bottom) * east)

def gen(w, h):
    if h < 3 or w < 3:
        return 'maze width and height MUST be ≥3'

    width  = int(w / 2 + 1)
    height = int(h)

    # maze[x][y]
    maze = [[Cell() for y in range(height)] for x in range(w)]

    for y in range(height):
        maze[width - 1][y].bottom   = maze[0][y].bottom   = False
        maze[width - 1][y].captured = maze[0][y].captured = True

    for x in range(width):
        maze[x][height - 1].right    = maze[x][0].right = False
        maze[x][height - 1].captured = maze[x][0].captured = True

    maze[width - 1][0].right = maze[0][0].right = maze[0][0].bottom = False
    maze[width - 1][0].captured = maze[0][0].captured = True

    start = (1, 1)
    exit = (width - 1, height - 1)

    x, y = start
    backtrack = 1
    captures = 0
    solutiontrack = 0

    while True:
        if (x, y) == exit:
            solutiontrack = backtrack

        if solutiontrack > 0 and solutiontrack == maze[x][y][3]:
            solutiontrack -= 1
            maze[x][y].solution = True

        if maze[x][y].captured == False:
            maze[x][y].captured = True
            captures += 1

        maze[x][y].backtrack = backtrack
        possibilities = []
        for a, b in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            if a >= 0 and a < width and b >= 0 and b < height:
                if maze[a][b].captured == False:
                    possibilities.append((a, b))

        if len(possibilities) == 0:
            maze[x][y].backtrack = 0
            backtrack -= 1
            if backtrack == 0:
                break
            for a, b in [
                    (x + 1, y    ),
                    (x - 1, y    ),
                    (x,     y + 1),
                    (x,     y - 1),
                    (-1,    -1   ),
                ]:
                if a >= 0 and a < width and b >= 0 and b < height:
                    if maze[a][b].backtrack == backtrack:
                        break

            x = a
            y = b
            continue

        pos = random.randint(0, len(possibilities) - 1)
        a, b = possibilities[pos]
        if a < x: maze[a][b].right  = False
        if a > x: maze[x][y].right  = False
        if b < y: maze[a][b].bottom = False
        if b > y: maze[x][y].bottom = False
        x = a
        y = b
        backtrack = backtrack + 1

    ret = ''
    for y in range(0, height - 1):
        for x in range(0, width - 1):
            dir = maze[x][y].directions(right=maze[x + 1][y], bottom=maze[x][y + 1])
            ret += maze_char(dir)
            if dir & east == 0:
                ret += maze_char(0)
            else:
                ret += maze_char(east | west)
        ret += '\n'

    if 'start' in prefs['maze']:
        ret = prefs['maze']['start'] + ret[1:]
    if 'end' in prefs['maze']:
        ret = ret[:-3] + prefs['maze']['end'] + '\n'

    return ret

def from_prefs():
    return gen(prefs['width'], prefs['maze']['height'])

def main():
    import argparse
    parser = argparse.ArgumentParser(description='generates mazes')
    parser.add_argument('width', default=32, type=int)
    parser.add_argument('height', default=64, type=int)
    parser.add_argument('-p', '--print', action='store_true')
    args = parser.parse_args()

    w = args.width
    h = args.height

    if w < 4:
        w = 4
    if h < 4:
        h = 4

    if args.print:
        from sys import stdout
        import uni2esky
        stdout.buffer.write(b'\x1b\x33\x18'
            + uni2esky.encode(gen(w, h)))
    else:
        print(gen(w, h))

if __name__ == '__main__':
    main()
