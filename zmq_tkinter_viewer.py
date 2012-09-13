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
import tetris_core
import ui_tkinter


#===============================================================================
# global constant
#===============================================================================
ZMQ_PUBLISH_ID = 'TETRIS'


#===============================================================================
# status
#===============================================================================
piece = tetris_core.Piece()
board = tetris_core.Board()
score = tetris_core.Score()


#===============================================================================
# key event
#===============================================================================
def key_event(e=None):
    if not e:
        return

    key = e.keysym # get key event
    if key.lower() == 'q':
        exit()


#===============================================================================
# 
#===============================================================================
def show_score(value):
    print 'score: %s' % value


MESSAGE_HANDLE_TABLE = {}

no_op = lambda *args, **kwargs: None


def register_handler(message_tag, handle_func):
    assert isinstance(message_tag, str)
    assert callable(handle_func)
    MESSAGE_HANDLE_TABLE[message_tag] = handle_func


def handle_message(msg):
    _log = logging.getLogger('handle_message')
    _log.debug('[MESSAGE] %s' % `msg`)

    if len(msg) != 2:
        return

    (header, obj) = msg
    handle_func = MESSAGE_HANDLE_TABLE.get(header, no_op)
    return handle_func(obj)


def polling():
    socks = dict(poller.poll(0))
    if subscriber not in socks:
        return False
    if socks[subscriber] != zmq.POLLIN:
        return False

    recv_str = subscriber.recv()
    (_, code_str) = recv_str.split(None, 1) # strip ZMQ_PUBLISH_ID
    msg = codec.decode(code_str)
    if not msg:
        return False

    handle_message(msg)
    return True


def handle_event(e=None):
    if e:
        return key_event(e)
    else:
        return polling()


if __name__ == '__main__':
    logging.basicConfig()

    context = zmq.Context()

    # connect to tetris server
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5556")
    subscriber.setsockopt(zmq.SUBSCRIBE, ZMQ_PUBLISH_ID)

    # initialize poll set
    poller = zmq.Poller()
    poller.register(subscriber, zmq.POLLIN)

    # ui
    ui_tkinter.init_ui(handle_event)

    # message handler
    register_handler(codec.PIECE_HEADER, piece.update_status)
    register_handler(codec.BOARD_HEADER, board.update_status)
    register_handler(codec.SCORE_HEADER, score.update_value)

    # signal
    piece.status_changed.connect(ui_tkinter.redraw_piece)
    board.status_changed.connect(ui_tkinter.redraw_board)
    score.value_changed.connect(show_score)

    # main loop
    ui_tkinter.main_loop()
