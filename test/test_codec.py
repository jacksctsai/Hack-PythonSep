# -*- coding: utf-8 -*-
import logging
import unittest

import codec
import pieces


class TestCodec(unittest.TestCase):
    def test_piece_codec(self):
        piece_id = pieces.J_PIECE
        px, py = 5, 7
        piece_direction = 2

        expect = codec.PIECE_HEADER, (piece_id, px, py, piece_direction)

        code_str = codec.encode_piece(piece_id, px, py, piece_direction)
        result = codec.decode(code_str)

        self.assertEqual(result, expect)

    def test_board_codec(self):
        board_width = 3
        board_height = 5
        board = [[0, 0, 0], [0, 'S', 0], [0, 'S', 'S'], [0, 'T', 'S'], ['T', 'T', 'T']]

        expect = codec.BOARD_HEADER, (board_width, board_height, board)

        code_str = codec.encode_board(board_width, board_height, board)
        result = codec.decode(code_str)

        self.assertEqual(result, expect)


if __name__ == "__main__":
#    import sys;sys.argv = ['TestCodec', 'Test.test_piece_codec']
    logging.basicConfig()
    unittest.main()
