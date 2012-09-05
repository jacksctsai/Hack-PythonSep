# -*- coding: utf-8 -*-
import unittest

import codec
import pieces


class TestCodec(unittest.TestCase):
    def test_piece_codec(self):
        piece_id = pieces.J_PIECE
        px, py = 5, 7
        piece_direction = 2
        expect = (piece_id, px, py, piece_direction)

        code_str = codec.encode_piece(piece_id, px, py, piece_direction)
        result = codec.decode(code_str)

        self.assertEqual(result, expect)


if __name__ == "__main__":
#    import sys;sys.argv = ['TestCodec', 'Test.test_piece_codec']
    unittest.main()
