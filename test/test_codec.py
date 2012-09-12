# -*- coding: utf-8 -*-
import logging
import unittest

import codec
import boards
import pieces


class TestCodec(unittest.TestCase):
    def test_piece_codec(self):
        piece_id = pieces.J_PIECE
        px, py = 5, 7
        piece_direction = 2
        piece_status = (piece_id, px, py, piece_direction)

        expect = codec.PIECE_HEADER, piece_status

        code_str = codec.encode_piece(piece_status)
        result = codec.decode(code_str)

        self.assertEqual(result, expect)

    def test_board_codec(self):
        """
        board = [['_', '_', '_', '_', ...],
                 ...,
                 ['_', '_', '_', '_', ...],
                 ['_', 'S', '_', '_', ...],
                 ['_', 'S', 'S', '_', ...],
                 ['_', 'T', 'S', '_', ...],
                 ['T', 'T', 'T', '_', ...]]
        """
        board = boards.create_board_lines(boards.BOARD_HEIGHT, '_')
        board[-1][0] = board[-1][1] = board[-1][2] = board[-2][1] = 'T'
        board[-2][2] = board[-3][1] = board[-3][2] = board[-4][1] = 'S'

        expect = codec.BOARD_HEADER, board

        code_str = codec.encode_board(board)
        result = codec.decode(code_str)

        self.assertEqual(result, expect)

    def test_score_codec(self):
        score = 10
        expect = codec.SCORE_HEADER, score

        code_str = codec.encode_score(score)
        result = codec.decode(code_str)

        self.assertEqual(result, expect)


if __name__ == "__main__":
#    import sys;sys.argv = ['TestCodec', 'Test.test_piece_codec']
    logging.basicConfig()
    unittest.main()
