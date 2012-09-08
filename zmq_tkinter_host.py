# -*- coding: utf-8 -*-
"""
# ZeroMQ
#   Website -- http://www.zeromq.org/
#   Python binding -- http://www.zeromq.org/bindings:python
#   Guide -- http://zguide.zeromq.org/chapter:all
"""

import logging
import zmq

import boards
import codec
import pieces
import ui_tkinter

#===============================================================================
# global constant
#===============================================================================
ZMQ_PUBLISH_ID = 'TETRIS'


#===============================================================================
# ZMQ publish
#===============================================================================
def publish(msg):
    publisher.send('%s %s' % (ZMQ_PUBLISH_ID, msg))


#===============================================================================
# event
#===============================================================================
def piece_changed_event():
    ui_tkinter.redraw_piece(pc, px, py, pdir)

    code_str = codec.encode_piece(pc, px, py, pdir)
    publish(code_str)


def board_changed_event():
    ui_tkinter.redraw_board(boards.BOARD_WIDTH, boards.BOARD_HEIGHT, board)

    code_str = codec.encode_board(boards.BOARD_WIDTH, boards.BOARD_HEIGHT, board)
    publish(code_str)


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
    piece_changed_event()


def move_piece_right():
    global px
    npx = px + 1
    if collide(pc, npx, py, pdir):
        return
    px = npx
    piece_changed_event()


def rotate_piece():
    global pdir
    npdir = (pdir + 1) % 4
    if collide(pc, px, py, npdir):
        return
    pdir = npdir
    piece_changed_event()


def drop_piece():
    global py
    for j in range(py, boards.BOARD_HEIGHT):
        if collide(pc, px, j + 1, pdir):
            py = j
            break
    piece_changed_event()


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
    global pc, px, py, pdir
    p_shape = pieces.get_piece_shape(pc, pdir)
    for i, j in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < boards.BOARD_WIDTH):
            continue
        if not (0 <= y < boards.BOARD_HEIGHT):
            continue
        board[y][x] = pc

    pc, px, py, pdir = pieces.new_piece()

    piece_changed_event()
    board_changed_event()


def clear_complete_lines():
    global board
    nb = [l for l in board if pieces.EMPTY in l] # 沒有被填滿的
    s = len(board) - len(nb)
    if s:
        board = boards.create_board_lines(s, pieces.EMPTY) + nb
        board_changed_event()
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
# tick
#===============================================================================
def handle_event(e=None):
    global py

    if e:
        key = e.keysym # get key event
        perform_key_action(key)
        return

    if pause:
        return

    if not collide(pc, px, py + 1, pdir):
        py += 1
        piece_changed_event()
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
    logging.basicConfig()

    board = boards.create_board_lines(boards.BOARD_HEIGHT, pieces.EMPTY)
    pc, px, py, pdir = pieces.new_piece() # 第一個piece
    score = 0
    valid_keys = NORMAL_KEYS
    pause = False

    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:5556")

    # ui
    ui_tkinter.init_ui(boards.BOARD_WIDTH, boards.BOARD_HEIGHT, board, pc, px, py, pdir, handle_event)
    ui_tkinter.main_loop()
