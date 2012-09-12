# -*- coding: utf-8 -*-
import random

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

    def update_status(self, piece_status):
        self.status = piece_status
        self.status_changed.emit(self.status)

    def get_status(self):
        return self.status

    def rand_new_piece(self):
        """
        new_piece = lambda pc: ([((z >> 2) + 1, z & 3) for z in xrange(16) if (pc >> z) & 1], 3, -2, pc)
        """
        p = random.choice(pieces.ALL_PIECES)
        np = (p, pieces.PIECE_INIT_X, pieces.PIECE_INIT_Y, pieces.PIECE_INIT_DIRECTION)
        self.update_status(np)


#===============================================================================
# Board
#===============================================================================
class Board(object):
    status_changed = signals.Signal()

    def __init__(self):
        self.status = boards.create_board_lines(boards.BOARD_HEIGHT, pieces.EMPTY)

    def get_status(self):
        return self.status

    def update_status(self, board_status):
        self.status = board_status
        self.status_changed.emit(self.status)

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
        self.commit_status()

    def commit_status(self):
        self.status_changed.emit(self.status)


#===============================================================================
# Score
#===============================================================================
class Score(object):
    value_changed = signals.Signal()

    def __init__(self):
        self._value = 0

    def get_score(self):
        return self._value

    def update_value(self, value):
        assert isinstance(value, int), value
        self._value = value
        self.value_changed.emit(self._value)

    def reset_score(self):
        self.update_value(0)

    def incr_score(self, value):
        assert isinstance(value, int), value
        self.update_value(self._value + value)


#===============================================================================
# collide
#===============================================================================
def collide(piece, board):
    """
    collide = lambda piece, px, py: [1 for (i, j) in piece if board[j + py][i + px]] #是否碰撞
    """
    pc, px, py, pdir = piece
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
FALL_SUCCESS, FALL_NO_SPACE, FALL_ON_GROUND = 0, 1, 2
def try_to_fall_piece(piece, board):
    """
    #自動落下
    np = (pc, px, py + 1, pdir)
    if not tetris_core.collide(np, board):
        piece.update_status(np)
    """
    pc, px, py, pdir = piece.get_status()
    np = (pc, px, py + 1, pdir)
    if not collide(np, board):
        piece.update_status(np)
        return FALL_SUCCESS
    if py < 0:
        return FALL_NO_SPACE
    return FALL_ON_GROUND


"""
    npx = px + (-1 if keys == "Left" else (1 if keys == "Right" else 0)) # 左-1右1否則0
    npiece = [(j, 3 - i) for (i, j) in piece] if keys == "Up" else piece   #rotate

    if not collide(npiece, npx, py):
        piece, px = npiece, npx

    if keys == "Down":
        py = (j for j in range(py, BOARD_HEIGHT) if collide(piece, px, j + 1)).next()
"""
def move_piece_left(piece, board):
    pc, px, py, pdir = piece.get_status()
    np = (pc, px - 1, py, pdir)
    if collide(np, board):
        return
    piece.update_status(np)


def move_piece_right(piece, board):
    pc, px, py, pdir = piece.get_status()
    np = (pc, px + 1, py, pdir)
    if collide(np, board):
        return
    piece.update_status(np)


def rotate_piece(piece, board):
    pc, px, py, pdir = piece.get_status()
    npdir = (pdir + 1) % 4
    np = (pc, px, py, npdir)
    if collide(np, board):
        return
    piece.update_status(np)


def drop_piece(piece, board):
    pc, px, py, pdir = piece.get_status()
    for j in range(py, boards.BOARD_HEIGHT):
        np_next = (pc, px, j + 1, pdir)
        if not collide(np_next, board):
            continue
        if j == py:
            break
        np = (pc, px, j, pdir)
        piece.update_status(np)
        break


def place_piece(piece, board):
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
    board.commit_status()
