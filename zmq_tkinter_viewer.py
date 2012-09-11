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
def process_message(msg):
    _log = logging.getLogger('process_msg')
    _log.debug('[MESSAGE] %s' % `msg`)

    if len(msg) != 2:
        return

    header = msg[0]
    obj = msg[1]
    if header == codec.PIECE_HEADER:
        piece.update_status(*obj)

    elif header == codec.BOARD_HEADER:
        board.update_status(obj)


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

    process_message(msg)
    return True


def handle_event(e=None):
    if e:
        return key_event(e)
    else:
        return polling()


if __name__ == '__main__':
    logging.basicConfig()

    _board_status = board.get_status()
    _pc, _px, _py, _pdir = piece.get_status()

    context = zmq.Context()

    # connect to tetris server
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5556")
    subscriber.setsockopt(zmq.SUBSCRIBE, ZMQ_PUBLISH_ID)

    # initialize poll set
    poller = zmq.Poller()
    poller.register(subscriber, zmq.POLLIN)

    # ui
    ui_tkinter.init_ui(_board_status, _pc, _px, _py, _pdir, handle_event)
    piece.status_changed.connect(ui_tkinter.redraw_piece)
    board.status_changed.connect(ui_tkinter.redraw_board)
    ui_tkinter.main_loop()
