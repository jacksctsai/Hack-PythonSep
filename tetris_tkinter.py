﻿# -*- coding: utf-8 -*-
import boards
import pieces
import signals
import ui_tkinter


#===============================================================================
# signal
#===============================================================================
piece_changed = signals.Signal()
board_changed = signals.Signal()


#===============================================================================
# piece status
#===============================================================================
piece_status = (pieces.EMPTY, pieces.PIECE_INIT_X, pieces.PIECE_INIT_Y, pieces.PIECE_INIT_DIRECTION)

def update_piece_status(pc, px, py, pdir):
    global piece_status
    piece_status = (pc, px, py, pdir)
    piece_changed.emit(*piece_status)


def get_piece_status():
    return piece_status


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
    pc, px, py, pdir = get_piece_status()
    npx = px - 1
    if collide(pc, npx, py, pdir):
        return
    update_piece_status(pc, npx, py, pdir)


def move_piece_right():
    pc, px, py, pdir = get_piece_status()
    npx = px + 1
    if collide(pc, npx, py, pdir):
        return
    update_piece_status(pc, npx, py, pdir)


def rotate_piece():
    pc, px, py, pdir = get_piece_status()
    npdir = (pdir + 1) % 4
    if collide(pc, px, py, npdir):
        return
    update_piece_status(pc, px, py, npdir)


def drop_piece():
    pc, px, py, pdir = get_piece_status()
    for j in range(py, boards.BOARD_HEIGHT):
        if collide(pc, px, j + 1, pdir):
            update_piece_status(pc, px, j, pdir)
            break


#===============================================================================
# score
#===============================================================================
def get_score():
    return score


def incr_score(value):
    global score
    assert isinstance(value, int), value
    score += value


#===============================================================================
# core function
#===============================================================================
def collide(pc, px, py, pdir):
    """
    collide = lambda piece, px, py: [1 for (i, j) in piece if board[j + py][i + px]] #是否碰撞
    """
    assert isinstance(px, int), px
    assert isinstance(py, int), py
    p_shape = pieces.get_piece_shape(pc, pdir)
    for (i, j) in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < boards.BOARD_WIDTH):
            return True
        if y >= boards.BOARD_HEIGHT:
            return True
        if y < 0:
            continue
        if board[y][x] != pieces.EMPTY:
            return True
    return False


def place_piece():
    """
    for i, j in piece:
        board[j + py][i + px] = pc
    """
    pc, px, py, pdir = get_piece_status()
    p_shape = pieces.get_piece_shape(pc, pdir)
    for i, j in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < boards.BOARD_WIDTH):
            continue
        if not (0 <= y < boards.BOARD_HEIGHT):
            continue
        board[y][x] = pc

    npc, npx, npy, npdir = pieces.new_piece()
    update_piece_status(npc, npx, npy, npdir)

    board_changed.emit(board)


def clear_complete_lines():
    global board
    nb = [l for l in board if pieces.EMPTY in l] # 沒有被填滿的
    s = len(board) - len(nb)
    if s:
        board = boards.create_board_lines(s, pieces.EMPTY) + nb
        board_changed.emit(board)
    return s


#===============================================================================
# 
#===============================================================================
def switch_pause():
    global pause, valid_keys
    assert isinstance(pause, bool), pause
    pause = (not pause)
    if pause:
        valid_keys = PAUSE_KEYS
    else:
        valid_keys = NORMAL_KEYS


def game_over():
    print "GAME OVER: score %i" % get_score() # game over 的狀況
    quit_game()


def quit_game():
    exit()


#===============================================================================
# 鍵盤控制
#===============================================================================
KEY_ACTION_MAP = {
    # switch_pause
    'p': switch_pause,
    # quit_game
    'q': quit_game,
    # drop_piece
    'down': drop_piece,
    'j': drop_piece,
    # rotate_piece
    'up': rotate_piece,
    'k': rotate_piece,
    # move_piece_left
    'left': move_piece_left,
    'h': move_piece_left,
    # move_piece_right
    'right': move_piece_right,
    'l': move_piece_right,
}


NORMAL_KEYS = set(['up', 'down', 'left', 'right', 'h', 'j', 'k', 'l', 'p', 'q'])
PAUSE_KEYS = set(['p', 'q'])


def perform_key_action(key):
    lkey = key.lower()
    if lkey not in valid_keys:
        return
    act_func = KEY_ACTION_MAP[lkey]
    act_func()


#===============================================================================
# event handler
#===============================================================================
def handle_event(e=None):
    global py

    if e:
        key = e.keysym # get key event
        perform_key_action(key)
        return

    if pause:
        return

    pc, px, py, pdir = get_piece_status()
    if not collide(pc, px, py + 1, pdir):
        update_piece_status(pc, px, py + 1, pdir)
        return

    if py < 0:
        game_over()
        return

    place_piece()
    s = clear_complete_lines()
    if s:
        incr_score(2 ** s)


#===============================================================================
# initial
#===============================================================================
if __name__ == '__main__':
    board = boards.create_board_lines(boards.BOARD_HEIGHT, pieces.EMPTY)

    _pc, _px, _py, _pdir = pieces.new_piece() # 第一個piece
    update_piece_status(_pc, _px, _py, _pdir)

    score = 0
    valid_keys = NORMAL_KEYS
    pause = False

    # ui
    ui_tkinter.init_ui(boards.BOARD_WIDTH, boards.BOARD_HEIGHT, board, _pc, _px, _py, _pdir, handle_event)
    piece_changed.connect(ui_tkinter.redraw_piece)
    board_changed.connect(ui_tkinter.redraw_board)
    ui_tkinter.main_loop()
