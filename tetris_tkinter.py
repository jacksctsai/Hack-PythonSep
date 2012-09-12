# -*- coding: utf-8 -*-
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

    fall_rc = tetris_core.try_to_fall_piece(piece, board)
    if fall_rc == tetris_core.FALL_SUCCESS:
        return

    if fall_rc == tetris_core.FALL_NO_SPACE:
        game_over()
        return

    # fall_rc == tetris_core.FALL_ON_GROUND
    tetris_core.place_piece(piece, board)

    piece.rand_new_piece()

    complete_lines = board.get_complete_lines()
    if not complete_lines:
        return

    board.strip_board_lines(complete_lines)
    score.incr_score(2 ** len(complete_lines))


#===============================================================================
# initial
#===============================================================================
if __name__ == '__main__':
    valid_keys = NORMAL_KEYS
    pause = False

    # ui
    ui_tkinter.init_ui(handle_event)

    # signal
    piece.status_changed.connect(ui_tkinter.redraw_piece)
    board.status_changed.connect(ui_tkinter.redraw_board)

    # 第一個piece
    piece.rand_new_piece()

    # main loop
    ui_tkinter.main_loop()
