I_PIECE = 0x0f
J_PIECE = 0x2e
L_PIECE = 0x47
O_PIECE = 0x66
S_PIECE = 0xC6
T_PIECE = 0x27
Z_PIECE = 0x6C



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
