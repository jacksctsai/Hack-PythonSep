# -*- coding: utf-8 -*-
import boards
import pieces
import signals


#===============================================================================
# Piece
#===============================================================================
class Piece(object):
    def __init__(self):
        self.status = (pieces.EMPTY, pieces.PIECE_INIT_X, pieces.PIECE_INIT_Y, pieces.PIECE_INIT_DIRECTION)


#===============================================================================
# signal
#===============================================================================
piece_changed = signals.Signal()
board_changed = signals.Signal()


#===============================================================================
# piece status
#===============================================================================
piece = Piece()

def update_piece_status(pc, px, py, pdir):
    piece.status = (pc, px, py, pdir)
    piece_changed.emit(*piece.status)


def get_piece_status():
    return piece.status


#===============================================================================
# board status
#===============================================================================
board_status = boards.create_board_lines(boards.BOARD_HEIGHT, pieces.EMPTY)

def get_board_status():
    return board_status


def is_piece_on_board(x, y, pc):
    assert isinstance(x, int), x
    assert isinstance(y, int), y
    assert (0 <= x < boards.BOARD_WIDTH), x
    assert (0 <= y < boards.BOARD_HEIGHT), y
    return (pc == board_status[y][x])


def change_piece_on_board(x, y, pc):
    assert isinstance(x, int), x
    assert isinstance(y, int), y
    if not (0 <= x < boards.BOARD_WIDTH):
        return False
    if not (0 <= y < boards.BOARD_HEIGHT):
        return False
    if pc == board_status[y][x]:
        return False
    board_status[y][x] = pc
    return True


def get_complete_lines():
    line_idx_list = [idx for (idx, line) in enumerate(board_status) if pieces.EMPTY not in line]
    return line_idx_list


def strip_board_lines(line_idx_list):
    global board_status
    line_idx_set = set(line_idx_list)
    nb = [line for (idx, line) in enumerate(board_status) if idx not in line_idx_set] # 不要被消除的
    add_num = boards.BOARD_HEIGHT - len(nb)
    board_status = boards.create_board_lines(add_num, pieces.EMPTY) + nb
    commit_board_status()


def commit_board_status():
    board_changed.emit(board_status)



#===============================================================================
# collide
#===============================================================================
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
        if not is_piece_on_board(x, y, pieces.EMPTY):
            return True
    return False


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


def place_piece():
    """
    for i, j in piece:
        board[j + py][i + px] = pc
    """
    pc, px, py, pdir = get_piece_status()
    p_shape = pieces.get_piece_shape(pc, pdir)
    for i, j in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < boards.BOARD_WIDTH):
            continue
        if not (0 <= y < boards.BOARD_HEIGHT):
            continue
        change_piece_on_board(x, y, pc)
    commit_board_status()
