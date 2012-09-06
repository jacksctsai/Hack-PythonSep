# -*- coding: utf-8 -*-
import copy
import sys
import Tkinter

import pieces

#===============================================================================
# global constant
#===============================================================================
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

UNIT_X = 30
UNIT_Y = 30

PIECE_INIT_X = 3
PIECE_INIT_Y = -2

BACKGROUND_COLOR = '#000'

#===============================================================================
# action
#===============================================================================
"""
    npx = px + (-1 if keys == "Left" else (1 if keys == "Right" else 0)) # 左-1右1否則0
    npiece = [(j, 3 - i) for (i, j) in piece] if keys == "Up" else piece   #rotate

    if not collide(npiece, npx, py):
        piece, px = npiece, npx

    if keys == "Down":
        py = (j for j in range(py, BOARD_HEIGHT) if collide(piece, px, j + 1)).next()
"""
def move_piece_left():
    global px
    npx = px - 1
    if collide(pc, npx, py, pdir):
        return
    px = npx


def move_piece_right():
    global px
    npx = px + 1
    if collide(pc, npx, py, pdir):
        return
    px = npx


def rotate_piece():
    global pdir
    npdir = (pdir + 1) % 4
    if collide(pc, px, py, npdir):
        return
    pdir = npdir


def drop_piece():
    global py
    for j in range(py, BOARD_HEIGHT):
        if collide(pc, px, j + 1, pdir):
            py = j
            break


#===============================================================================
# ui
#===============================================================================
PIECE_COLOR = {
    pieces.I_PIECE: "red",
    pieces.J_PIECE: "#0f0",
    pieces.L_PIECE: "#ff0",
    pieces.O_PIECE: "#0ff",
    pieces.S_PIECE: "#38f",
    pieces.T_PIECE: "blue",
    pieces.Z_PIECE: "#f0f"
}


def map_to_ui_x(i):
    return i * UNIT_X


def map_to_ui_y(j):
    return j * UNIT_Y


def ui_create_rect(i, j, color):
    assert isinstance(i, int), i
    assert isinstance(j, int), j
    x0 = map_to_ui_x(i)
    y0 = map_to_ui_y(j)
    x1 = map_to_ui_x(i + 1)
    y1 = map_to_ui_y(j + 1)
    return scr.create_rectangle(x0, y0, x1, y1, fill=color)


UI_BOARD = []
UI_PIECE = []
UI_RECT_ID = []
def init_ui(scr, board, pc, px, py, pdir):
    global UI_BOARD, UI_RECT_ID, UI_PIECE
    UI_BOARD = copy.deepcopy(board)
    UI_PIECE = [pc, px, py, pdir]

    UI_RECT_ID = []
    for j in range(BOARD_HEIGHT):
        id_list = []
        for i in range(BOARD_WIDTH):
            rect_id = ui_create_rect(i, j, BACKGROUND_COLOR)
            id_list.append(rect_id)
        UI_RECT_ID.append(id_list)


def redraw_ui(board, pc, px, py, pdir):
    piece_changed = False
    if pc != UI_PIECE[0]:
        UI_PIECE[0] = pc
        piece_changed = True
    if px != UI_PIECE[1]:
        UI_PIECE[1] = px
        piece_changed = True
    if py != UI_PIECE[2]:
        UI_PIECE[2] = py
        piece_changed = True
    if pdir != UI_PIECE[3]:
        UI_PIECE[3] = pdir
        piece_changed = True

    p_shape = pieces.get_piece_shape(pc, pdir)
    piece_region = [(i + px, j + py) for i, j in p_shape]

    for i, j in [(i, j) for i in range(BOARD_WIDTH) for j in range(BOARD_HEIGHT)]:
        if (i, j) in piece_region: # display piece color
            if not piece_changed:
                continue
            UI_BOARD[j][i] = pc
            color = PIECE_COLOR[pc]
        else: # display board color
            if board[j][i] == UI_BOARD[j][i]: # board (i, j) not change
                continue
            UI_BOARD[j][i] = board[j][i]
            color = PIECE_COLOR.get(board[j][i], BACKGROUND_COLOR)
        rect_id = UI_RECT_ID[j][i]
        scr.itemconfig(rect_id, fill=color)


#===============================================================================
# score
#===============================================================================
def reset_score():
    global score
    score = 0


def get_score():
    return score


def incr_score(value):
    global score
    assert isinstance(value, int), value
    score += value


#===============================================================================
# collide
#===============================================================================
"""
collide = lambda piece, px, py: [1 for (i, j) in piece if board[j + py][i + px]] #是否碰撞
"""
def collide(pc, px, py, pdir):
    assert isinstance(px, int), px
    assert isinstance(py, int), py
    p_shape = pieces.get_piece_shape(pc, pdir)
    for (i, j) in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < BOARD_WIDTH):
            return True
        if y >= BOARD_HEIGHT:
            return True
        if y < 0:
            continue
        if board[y][x]:
            return True
    return False


#===============================================================================
# board
#===============================================================================
def new_board_lines(num):
    assert isinstance(num, int), num
    return [[0] * BOARD_WIDTH for _ in range(num)]


board = new_board_lines(BOARD_HEIGHT)


def place_piece(pc, px, py, pdir):
    """
    for i, j in piece:
        board[j + py][i + px] = pc
    """
    p_shape = pieces.get_piece_shape(pc, pdir)
    for i, j in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < BOARD_WIDTH):
            continue
        if not (0 <= y < BOARD_HEIGHT):
            continue
        board[y][x] = pc


def clear_complete_lines():
    global board
    nb = [l for l in board if 0 in l] # 沒有被填滿的
    s = len(board) - len(nb)
    if s:
        board = new_board_lines(s) + nb
    return s


#===============================================================================
# 
#===============================================================================
def switch_pause():
    global pause
    assert isinstance(pause, bool), pause
    pause = (not pause)


def game_over():
    sys.exit("GAME OVER: score %i" % get_score()) # game over 的狀況


#===============================================================================
# tick
#===============================================================================
def tick(e=None):
    global px, py, pc, pdir

    keys = e.keysym if e else  "" # get key event

    if keys in ['p', 'P']:
        switch_pause()
    elif keys in ['Left', 'h', 'H']:
        move_piece_left()
    elif keys in ['Right', 'l', 'L']:
        move_piece_right()
    elif keys in ['Up', 'k', 'K']:
        rotate_piece()
    elif keys in ['Down', 'j', 'J']:
        drop_piece()

    if pause:
        return

    if e == None:
        if collide(pc, px, py + 1, pdir):
            if py < 0:
                game_over()
                return

            place_piece(pc, px, py, pdir)

            pc, px, py, pdir = pieces.new_piece()
            px, py = PIECE_INIT_X, PIECE_INIT_Y

        else:
            py += 1

        s = clear_complete_lines()
        if s:
            incr_score(2 ** s)

        scr.after(300, tick)

    redraw_ui(board, pc, px, py, pdir)


#===============================================================================
# initial
#===============================================================================
board = None
piece = None
pc = None
px = PIECE_INIT_X
py = PIECE_INIT_Y
pdir = 0
score = 0
pause = False
scr = None

def init_tetris():
    global board, pc, px, py, pdir, scr
    board = new_board_lines(BOARD_HEIGHT)
    pc, px, py, pdir = pieces.new_piece() # 第一個piece
    reset_score()

    scr = Tkinter.Canvas(width=map_to_ui_x(BOARD_WIDTH), height=map_to_ui_y(BOARD_HEIGHT), bg=BACKGROUND_COLOR)
    init_ui(scr, board, pc, px, py, pdir)
    scr.after(300, tick)
    scr.bind_all("<Key>", tick)
    scr.pack()
    scr.mainloop()

#  for line in board: print '\t'.join(str(v) for v in line)
#  print len(board)
#  print px,py

if __name__ == '__main__':
    init_tetris()
