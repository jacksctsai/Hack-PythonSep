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
import signals
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


#===============================================================================
# signal
#===============================================================================
board_changed = signals.Signal()


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
        board = obj
        board_changed.emit(board)


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

    board = boards.create_board_lines(boards.BOARD_HEIGHT, pieces.EMPTY)
    pc, px, py, pdir = (pieces.EMPTY, -4, -4, 0)

    context = zmq.Context()

    # connect to tetris server
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5556")
    subscriber.setsockopt(zmq.SUBSCRIBE, ZMQ_PUBLISH_ID)

    # initialize poll set
    poller = zmq.Poller()
    poller.register(subscriber, zmq.POLLIN)

    # ui
    ui_tkinter.init_ui(board, pc, px, py, pdir, handle_event)
    piece.status_changed.connect(ui_tkinter.redraw_piece)
    board_changed.connect(ui_tkinter.redraw_board)
    ui_tkinter.main_loop()
