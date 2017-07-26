#! /usr/local/bin/python3

# heavily modified, but original algs by Vidar 'koala_man' Holen
# vidarholen.net
# http://www.vidarholen.net/~vidar/generatemaze.py

import random
import prefs

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
    if prefs.prefs['maze']['style'] == 'round':
        chars = [k[0] for k in chars]
    elif prefs.prefs['maze']['style'] == 'square':
        chars = [k[1] for k in chars]
    elif prefs.prefs['maze']['style'] == 'random':
        chars = [k[random.randint(0, 1)] for k in chars]
    else:
        chars = [chr(random.randint(0x2500, 0x27ff)) for k in chars]

    if prefs.prefs['maze']['halves'] == False:
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
    maze = ''

    width  = int(w / 2 + 2)
    height = int(h)

    # map[x][y]
    map = [[Cell() for y in range(height)] for x in range(w)]

    for y in range(height):
        map[width - 1][y].bottom   = map[0][y].bottom   = False
        map[width - 1][y].captured = map[0][y].captured = True

    for x in range(width):
        map[x][height - 1].right    = map[x][0].right = False
        map[x][height - 1].captured = map[x][0].captured = True

    map[width - 1][0].right = map[0][0].right = map[0][0].bottom = False
    map[width - 1][0].captured = map[0][0].captured = True

    start = (1, 1)
    exit = (width - 1, height - 1)

    x, y = start
    backtrack = 1
    captures = 0
    solutiontrack = 0

    while True:
        if (x, y) == exit:
            solutiontrack = backtrack

        if solutiontrack > 0 and solutiontrack == map[x][y][3]:
            solutiontrack -= 1
            map[x][y].solution = True

        if map[x][y].captured == False:
            map[x][y].captured = True
            captures += 1

        map[x][y].backtrack = backtrack
        possibilities = []
        for a, b in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            if a >= 0 and a < width and b >= 0 and b<height:
                if map[a][b].captured == False:
                    possibilities.append((a, b))

        if len(possibilities) == 0:
            map[x][y].backtrack = 0
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
                if a >= 0 and a < width and b >= 0 and b<height:
                    if map[a][b].backtrack == backtrack:
                        break

            x = a
            y = b
            continue

        pos = random.randint(0, len(possibilities) - 1)
        a, b = possibilities[pos]
        if a < x: map[a][b].right  = False
        if a > x: map[x][y].right  = False
        if b < y: map[a][b].bottom = False
        if b > y: map[x][y].bottom = False
        x = a
        y = b
        backtrack = backtrack + 1

    for y in range(0, height - 1):
        for x in range(0, width - 1):
            dir = map[x][y].directions(right=map[x + 1][y], bottom=map[x][y + 1])
            maze += maze_char(dir)
            if dir & east == 0:
                maze += maze_char(0)
            else:
                maze += maze_char(east | west)
        maze += '\n'

    return maze

def from_prefs():
    return gen(prefs.prefs['width'], prefs.prefs['maze']['height'])

def main():
    import argparse
    parser = argparse.ArgumentParser(description='generates mazes')
    parser.add_argument('width', default=32, type=int)
    parser.add_argument('height', default=64, type=int)
    args = parser.parse_args()
    print(gen(args.width, args.height))

if __name__ == '__main__':
    main()
