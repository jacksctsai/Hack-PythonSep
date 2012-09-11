# -*- coding: utf-8 -*-
import pieces
import tetris_core
import ui_tkinter


#===============================================================================
# status
#===============================================================================
piece = tetris_core.Piece()


#===============================================================================
# score
#===============================================================================
def get_score():
    return score


def incr_score(value):
    global score
    assert isinstance(value, int), value
    score += value


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
    print "GAME OVER: score %i" % get_score() # game over 的狀況
    quit_game()


def quit_game():
    exit()


#===============================================================================
# 鍵盤控制
#===============================================================================
drop_piece = lambda: tetris_core.drop_piece(piece)
rotate_piece = lambda: tetris_core.rotate_piece(piece)
move_piece_left = lambda: tetris_core.move_piece_left(piece)
move_piece_right = lambda: tetris_core.move_piece_right(piece)


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
    if not tetris_core.collide(pc, px, py + 1, pdir):
        piece.update_status(pc, px, py + 1, pdir)
        return

    if py < 0:
        game_over()
        return

    tetris_core.place_piece(piece)

    npc, npx, npy, npdir = pieces.new_piece()
    piece.update_status(npc, npx, npy, npdir)

    complete_lines = tetris_core.get_complete_lines()
    if not complete_lines:
        return

    tetris_core.strip_board_lines(complete_lines)
    incr_score(2 ** len(complete_lines))


#===============================================================================
# initial
#===============================================================================
if __name__ == '__main__':
    _board = tetris_core.board.get_status()

    _pc, _px, _py, _pdir = pieces.new_piece() # 第一個piece
    piece.update_status(_pc, _px, _py, _pdir)

    score = 0
    valid_keys = NORMAL_KEYS
    pause = False

    # ui
    ui_tkinter.init_ui(_board, _pc, _px, _py, _pdir, handle_event)
    piece.status_changed.connect(ui_tkinter.redraw_piece)
    tetris_core.board.status_changed.connect(ui_tkinter.redraw_board)
    ui_tkinter.main_loop()
