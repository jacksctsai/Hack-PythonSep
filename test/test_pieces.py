import unittest

import pieces


class TestPieces(unittest.TestCase):
    def test_get_piece_shape_J0(self):
        piece_id = pieces.J_PIECE
        direction = 0
        expect = [(1, 1), (1, 2), (1, 3), (2, 1)]
        result = pieces.get_piece_shape(piece_id, direction)
        self.assertEqual(result, expect)

    def test_get_piece_shape_J1(self):
        piece_id = pieces.J_PIECE
        direction = 1
        expect = [(1, 2), (2, 2), (3, 2), (1, 1)]
        result = pieces.get_piece_shape(piece_id, direction)
        self.assertEqual(result, expect)

    def test_get_piece_shape_J2(self):
        piece_id = pieces.J_PIECE
        direction = 2
        expect = [(2, 2), (2, 1), (2, 0), (1, 2)]
        result = pieces.get_piece_shape(piece_id, direction)
        self.assertEqual(result, expect)

    def test_get_piece_shape_J3(self):
        piece_id = pieces.J_PIECE
        direction = 3
        expect = [(2, 1), (1, 1), (0, 1), (2, 2)]
        result = pieces.get_piece_shape(piece_id, direction)
        self.assertEqual(result, expect)


if __name__ == "__main__":
#    import sys;sys.argv = ['', 'TestPieces.test_remap_piece']
    unittest.main()
