# -*- coding: utf-8 -*-
"""
# ZeroMQ
#   Website -- http://www.zeromq.org/
#   Python binding -- http://www.zeromq.org/bindings:python
#   Guide -- http://zguide.zeromq.org/chapter:all
"""

import logging
import zmq

import codec
import pieces
import tetris_core
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


def publish_piece_info(pc, px, py, pdir):
    code_str = codec.encode_piece(pc, px, py, pdir)
    publish(code_str)


def publish_board_info(board):
    code_str = codec.encode_board(board)
    publish(code_str)


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
    'down': tetris_core.drop_piece,
    'j': tetris_core.drop_piece,
    # rotate_piece
    'up': tetris_core.rotate_piece,
    'k': tetris_core.rotate_piece,
    # move_piece_left
    'left': tetris_core.move_piece_left,
    'h': tetris_core.move_piece_left,
    # move_piece_right
    'right': tetris_core.move_piece_right,
    'l': tetris_core.move_piece_right,
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
    if e:
        key = e.keysym # get key event
        perform_key_action(key)
        return

    if pause:
        return

    pc, px, py, pdir = tetris_core.piece.get_status()
    if not tetris_core.collide(pc, px, py + 1, pdir):
        tetris_core.piece.update_status(pc, px, py + 1, pdir)
        return

    if py < 0:
        game_over()
        return

    tetris_core.place_piece()

    npc, npx, npy, npdir = pieces.new_piece()
    tetris_core.piece.update_status(npc, npx, npy, npdir)

    complete_lines = tetris_core.get_complete_lines()
    if not complete_lines:
        return

    tetris_core.strip_board_lines(complete_lines)
    incr_score(2 ** len(complete_lines))


#===============================================================================
# initial
#===============================================================================
if __name__ == '__main__':
    logging.basicConfig()

    _board = tetris_core.get_board_status()

    _pc, _px, _py, _pdir = pieces.new_piece() # 第一個piece
    tetris_core.piece.update_status(_pc, _px, _py, _pdir)

    score = 0
    valid_keys = NORMAL_KEYS
    pause = False

    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:5556")

    tetris_core.piece_changed.connect(publish_piece_info)
    tetris_core.board_changed.connect(publish_board_info)

    # ui
    ui_tkinter.init_ui(_board, _pc, _px, _py, _pdir, handle_event)
    tetris_core.piece_changed.connect(ui_tkinter.redraw_piece)
    tetris_core.board_changed.connect(ui_tkinter.redraw_board)
    ui_tkinter.main_loop()
