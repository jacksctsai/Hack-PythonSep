# -*- coding: utf-8 -*-
import logging

PIECE_HEADER = 'PIECE'


#===============================================================================
# encode
#===============================================================================
def encode_piece(piece_id, px, py, piece_direction):
    code_str = '%s %s %s %s %s' % (PIECE_HEADER, piece_id, px, py, piece_direction)
    return code_str


#===============================================================================
# decode
#===============================================================================
def decode(code_str):
    _log = logging.getLogger('decode')
    code_list = code_str.split()
    if not code_list:
        _log.error('[DECODE] fail to decode -- invalid code_str [%s]' % code_str)
        return

    code_header = code_list[0]
    code_args = code_list[1:]
    decode_func = HEADER_DECODE_TABLE.get(code_header)
    if not decode_func:
        _log.error('[DECODE] fail to decode -- invalid header in code_str [%s]' % code_str)
        return

    return decode_func(*code_args)


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


HEADER_DECODE_TABLE = {
    PIECE_HEADER: decode_piece,
}
