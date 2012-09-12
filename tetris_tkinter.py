# -*- coding: utf-8 -*-
import pieces
import tetris_core
import ui_tkinter


#===============================================================================
# status
#===============================================================================
piece = tetris_core.Piece()
board = tetris_core.Board()
score = tetris_core.Score()


#===============================================================================
# action
#===============================================================================
def switch_pause():
    global pause, valid_keys
    assert isinstance(pause, bool), pause
    pause = (not pause)
    if pause:
        valid_keys = PAUSE_KEYS
    else:
        valid_keys = NORMAL_KEYS


def game_over():
    print "GAME OVER: score %i" % score.get_score() # game over 的狀況
    quit_game()


def quit_game():
    exit()


#===============================================================================
# 鍵盤控制
#===============================================================================
drop_piece = lambda: tetris_core.drop_piece(piece, board)
rotate_piece = lambda: tetris_core.rotate_piece(piece, board)
move_piece_left = lambda: tetris_core.move_piece_left(piece, board)
move_piece_right = lambda: tetris_core.move_piece_right(piece, board)


KEY_ACTION_MAP = {
    # switch_pause
    'p': switch_pause,
    # quit_game
    'q': quit_game,
    # drop_piece
    'down': drop_piece,
    'j': drop_piece,
    # rotate_piece
    'up': rotate_piece,
    'k': rotate_piece,
    # move_piece_left
    'left': move_piece_left,
    'h': move_piece_left,
    # move_piece_right
    'right': move_piece_right,
    'l': move_piece_right,
}


NORMAL_KEYS = set(['up', 'down', 'left', 'right', 'h', 'j', 'k', 'l', 'p', 'q'])
PAUSE_KEYS = set(['p', 'q'])


def perform_key_action(key):
    lkey = key.lower()
    if lkey not in valid_keys:
        return
    act_func = KEY_ACTION_MAP[lkey]
    act_func()


#===============================================================================
# event handler
#===============================================================================
def handle_event(e=None):
    if e:
        key = e.keysym # get key event
        perform_key_action(key)
        return

    if pause:
        return

    pc, px, py, pdir = piece.get_status()
    if not tetris_core.collide(pc, px, py + 1, pdir, board):
        piece.update_status(pc, px, py + 1, pdir)
        return

    if py < 0:
        game_over()
        return

    tetris_core.place_piece(piece, board)

    npc, npx, npy, npdir = pieces.new_piece()
    piece.update_status(npc, npx, npy, npdir)

    complete_lines = board.get_complete_lines()
    if not complete_lines:
        return

    board.strip_board_lines(complete_lines)
    score.incr_score(2 ** len(complete_lines))


#===============================================================================
# initial
#===============================================================================
if __name__ == '__main__':
    _pc, _px, _py, _pdir = pieces.new_piece() # 第一個piece
    piece.update_status(_pc, _px, _py, _pdir)

    valid_keys = NORMAL_KEYS
    pause = False

    # ui
    ui_tkinter.init_ui(handle_event)
    piece.status_changed.connect(ui_tkinter.redraw_piece)
    board.status_changed.connect(ui_tkinter.redraw_board)
    ui_tkinter.main_loop()
