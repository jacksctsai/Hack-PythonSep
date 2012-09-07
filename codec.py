# -*- coding: utf-8 -*-
import logging


#===============================================================================
# decode
#===============================================================================
def decode(code_str):
    _log = logging.getLogger('decode')
    code_list = code_str.split()
    if not code_list:
        _log.error('[DECODE] fail to decode -- invalid code_str [%s]' % code_str)
        return

    header = code_list[0]
    code_args = code_list[1:]
    decode_func = HEADER_DECODE_TABLE.get(header)
    if not decode_func:
        _log.error('[DECODE] fail to decode -- invalid header in code_str [%s]' % code_str)
        return

    obj = decode_func(*code_args)
    if obj is None:
        return

    return header, obj


#===============================================================================
# codec : piece
#===============================================================================
PIECE_HEADER = 'PIECE'
def encode_piece(piece_id, px, py, piece_direction):
    code_str = '%s %s %s %s %s' % (PIECE_HEADER, piece_id, px, py, piece_direction)
    return code_str


def decode_piece(*args):
    _log = logging.getLogger('decode_piece')
    if len(args) != 4:
        _log.error('[DECODE] fail to decode piece -- invalid args [%s]' % ' '.join(args))
        return

    try:
        piece_id = args[0]
        px = int(args[1])
        py = int(args[2])
        piece_direction = int(args[3])
    except ValueError:
        _log.error('[DECODE] fail to decode piece -- invalid format in args [%s]' % ' '.join(args))
        return

    return piece_id, px, py, piece_direction


#===============================================================================
# codec : board
#===============================================================================
BOARD_HEADER = 'BOARD'
def encode_board(board_width, board_height, board):
    code_str_list = [BOARD_HEADER, str(board_width), str(board_height)]
    for j in range(board_height):
        for i in range(board_width):
            code_str_list.append(str(board[j][i]))
    code_str = ' '.join(code_str_list)
    return code_str


def decode_board(*args):
    _log = logging.getLogger('decode_board')
    if len(args) < 2:
        _log.error('[DECODE] fail to decode board -- invalid args [%s]' % ' '.join(args))
        return

    try:
        board_width = int(args[0])
        board_height = int(args[1])
    except ValueError:
        _log.error('[DECODE] fail to decode piece -- invalid format in args [%s]' % ' '.join(args))
        return

    if len(args) != (board_width * board_height + 2):
        _log.error('[DECODE] fail to decode board -- not enough args [%s]' % ' '.join(args))
        return

    board = []
    for j in range(board_height):
        line = []
        for i in range(board_width):
            pc = args[j * board_width + i + 2]
            try:
                pc = int(pc)
            except ValueError:
                pass
            line.append(pc)
        board.append(line)

    return board_width, board_height, board


#===============================================================================
# decode table
#===============================================================================
HEADER_DECODE_TABLE = {
    PIECE_HEADER: decode_piece,
    BOARD_HEADER: decode_board,
}
