# -*- coding: utf-8 -*-
import boards
import pieces
import signals


#===============================================================================
# Piece
#===============================================================================
class Piece(object):
    status_changed = signals.Signal()

    def __init__(self):
        self.status = (pieces.EMPTY, pieces.PIECE_INIT_X, pieces.PIECE_INIT_Y, pieces.PIECE_INIT_DIRECTION)

    def update_status(self, pc, px, py, pdir):
        self.status = (pc, px, py, pdir)
        self.status_changed.emit(*self.status)

    def get_status(self):
        return self.status


#===============================================================================
# Board
#===============================================================================
class Board(object):
    status_changed = signals.Signal()

    def __init__(self):
        self.status = boards.create_board_lines(boards.BOARD_HEIGHT, pieces.EMPTY)

    def get_status(self):
        return self.status

    def is_piece_on_board(self, x, y, pc):
        assert isinstance(x, int), x
        assert isinstance(y, int), y
        assert (0 <= x < boards.BOARD_WIDTH), x
        assert (0 <= y < boards.BOARD_HEIGHT), y
        return (pc == self.status[y][x])

    def change_piece(self, x, y, pc):
        assert isinstance(x, int), x
        assert isinstance(y, int), y
        if not (0 <= x < boards.BOARD_WIDTH):
            return False
        if not (0 <= y < boards.BOARD_HEIGHT):
            return False
        if pc == self.status[y][x]:
            return False
        self.status[y][x] = pc
        return True

    def get_complete_lines(self):
        line_idx_list = [idx for (idx, line) in enumerate(self.status) if pieces.EMPTY not in line]
        return line_idx_list

    def strip_board_lines(self, line_idx_list):
        line_idx_set = set(line_idx_list)
        nb = [line for (idx, line) in enumerate(self.status) if idx not in line_idx_set] # 不要被消除的
        add_num = boards.BOARD_HEIGHT - len(nb)
        self.status = boards.create_board_lines(add_num, pieces.EMPTY) + nb
        commit_board_status()


#===============================================================================
# board status
#===============================================================================
board = Board()





def commit_board_status():
    board.status_changed.emit(board.status)



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
        if not board.is_piece_on_board(x, y, pieces.EMPTY):
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
def move_piece_left(piece):
    pc, px, py, pdir = piece.get_status()
    npx = px - 1
    if collide(pc, npx, py, pdir):
        return
    piece.update_status(pc, npx, py, pdir)


def move_piece_right(piece):
    pc, px, py, pdir = piece.get_status()
    npx = px + 1
    if collide(pc, npx, py, pdir):
        return
    piece.update_status(pc, npx, py, pdir)


def rotate_piece(piece):
    pc, px, py, pdir = piece.get_status()
    npdir = (pdir + 1) % 4
    if collide(pc, px, py, npdir):
        return
    piece.update_status(pc, px, py, npdir)


def drop_piece(piece):
    pc, px, py, pdir = piece.get_status()
    for j in range(py, boards.BOARD_HEIGHT):
        if collide(pc, px, j + 1, pdir):
            piece.update_status(pc, px, j, pdir)
            break


def place_piece(piece):
    """
    for i, j in piece:
        board[j + py][i + px] = pc
    """
    pc, px, py, pdir = piece.get_status()
    p_shape = pieces.get_piece_shape(pc, pdir)
    for i, j in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < boards.BOARD_WIDTH):
            continue
        if not (0 <= y < boards.BOARD_HEIGHT):
            continue
        board.change_piece(x, y, pc)
    commit_board_status()
