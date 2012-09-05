# -*- coding: utf-8 -*-
import random


PIECE_INIT_X = 3
PIECE_INIT_Y = -2
PIECE_INIT_DIRECTION = 0


I_PIECE = 'I' # 0x0f
J_PIECE = 'J' # 0x2e
L_PIECE = 'L' # 0x47
O_PIECE = 'O' # 0x66
S_PIECE = 'S' # 0xC6
T_PIECE = 'T' # 0x27
Z_PIECE = 'Z' # 0x6C


ALL_PIECES = [
    I_PIECE,
    J_PIECE,
    L_PIECE,
    O_PIECE,
    S_PIECE,
    T_PIECE,
    Z_PIECE
]


"""
shape = lambda pc: [((z >> 2) + 1, z & 3) for z in range(16) if (pc >> z) & 1]
"""
PIECE_SHAPE = {
    I_PIECE: [(1, 0), (1, 1), (1, 2), (1, 3)],
    J_PIECE: [(1, 1), (1, 2), (1, 3), (2, 1)],
    L_PIECE: [(1, 0), (1, 1), (1, 2), (2, 2)],
    O_PIECE: [(1, 1), (1, 2), (2, 1), (2, 2)],
    S_PIECE: [(1, 1), (1, 2), (2, 2), (2, 3)],
    T_PIECE: [(1, 0), (1, 1), (1, 2), (2, 1)],
    Z_PIECE: [(1, 2), (1, 3), (2, 1), (2, 2)]
}


def new_piece():
    """
    new_piece = lambda pc: ([((z >> 2) + 1, z & 3) for z in xrange(16) if (pc >> z) & 1], 3, -2, pc)
    """
    p = random.choice(ALL_PIECES)
    return p, PIECE_INIT_X, PIECE_INIT_Y, PIECE_INIT_DIRECTION


def get_piece_shape(piece_id, direction=0):
    """
    J_PIECE
            . . . . .    . . . . .    . . ._. .    . . . . .
            . ._._. .    . ._. . .    . . | | .    ._._._. .
            . | ._| .    . | |_._.    . ._| | .    |_._. | .
            . | | . .    . |_._._|    . |_._| .    . . |_| .
            . |_| . .    . . . . .    . . . . .    . . . . .
    direction : 0            1            2            3
    """
    assert (piece_id in PIECE_SHAPE), piece_id
    assert isinstance(direction, int), direction
    assert (0 <= direction <= 3), direction

    piece_shape = PIECE_SHAPE[piece_id]
    if direction == 0:
        return piece_shape
    elif direction == 1:
        return [(j, 3 - i) for (i, j) in piece_shape]
    elif direction == 2:
        return [(3 - i, 3 - j) for (i, j) in piece_shape]
    else: # direction == 3
        return [(3 - j, i) for (i, j) in piece_shape]
