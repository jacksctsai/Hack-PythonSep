# -*- coding: utf-8 -*-
import boards
import pieces
import signals


#===============================================================================
# signal
#===============================================================================
piece_changed = signals.Signal()
board_changed = signals.Signal()


#===============================================================================
# piece status
#===============================================================================
piece_status = (pieces.EMPTY, pieces.PIECE_INIT_X, pieces.PIECE_INIT_Y, pieces.PIECE_INIT_DIRECTION)

def update_piece_status(pc, px, py, pdir):
    global piece_status
    piece_status = (pc, px, py, pdir)
    piece_changed.emit(*piece_status)


def get_piece_status():
    return piece_status


#===============================================================================
# action
#===============================================================================
"""
    npx = px + (-1 if keys == "Left" else (1 if keys == "Right" else 0)) # 左-1右1否則0
    npiece = [(j, 3 - i) for (i, j) in piece] if keys == "Up" else piece   #rotate

    if not collide(npiece, npx, py):
        piece, px = npiece, npx

    if keys == "Down":
        py = (j for j in range(py, BOARD_HEIGHT) if collide(piece, px, j + 1)).next()
"""
def move_piece_left():
    pc, px, py, pdir = get_piece_status()
    npx = px - 1
    if collide(pc, npx, py, pdir):
        return
    update_piece_status(pc, npx, py, pdir)


def move_piece_right():
    pc, px, py, pdir = get_piece_status()
    npx = px + 1
    if collide(pc, npx, py, pdir):
        return
    update_piece_status(pc, npx, py, pdir)


def rotate_piece():
    pc, px, py, pdir = get_piece_status()
    npdir = (pdir + 1) % 4
    if collide(pc, px, py, npdir):
        return
    update_piece_status(pc, px, py, npdir)


def drop_piece():
    pc, px, py, pdir = get_piece_status()
    for j in range(py, boards.BOARD_HEIGHT):
        if collide(pc, px, j + 1, pdir):
            update_piece_status(pc, px, j, pdir)
            break


def collide(pc, px, py, pdir):
    """
    collide = lambda piece, px, py: [1 for (i, j) in piece if board[j + py][i + px]] #是否碰撞
    """
    assert isinstance(px, int), px
    assert isinstance(py, int), py
    p_shape = pieces.get_piece_shape(pc, pdir)
    for (i, j) in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < boards.BOARD_WIDTH):
            return True
        if y >= boards.BOARD_HEIGHT:
            return True
        if y < 0:
            continue
        if board[y][x] != pieces.EMPTY:
            return True
    return False


