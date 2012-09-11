# -*- coding=utf8 -*-

'''
* 參考 weijr 老師的 tetris in tkinter -- ``http://weijr-note.blogspot.tw/2007/04/tetris-program-in-lines.html``

* full documents of Vpython -- ``http://vpython.org/contents/docs/visual/index.html``
'''

# update: 2012.07.29 完成大部分功能
# update: 2012.09.01 加入暫停與 hjkl 方向鍵控制 (Vim 操作練習?!)

#===============================================================================
# TODO: 觀戰
#   1. 遊戲開始後，可在任何時間加入觀戰
#   2. 傳送給觀戰者的資料:
#     - 當下 board 的狀態
#     - 移動中的 piece
#     - 分數
#     - 是否暫停
#     - 是否 game over
#   3. 需要制定:
#     - 資料傳送格式
#     - 更新 UI 用的 API
#===============================================================================

import time

import pieces
import sound
import tetris_core
import ui


#===============================================================================
# 設定值
#===============================================================================
score, N, T = 0, 100, 0.5


#===============================================================================
# status
#===============================================================================
piece = tetris_core.Piece()
board = tetris_core.Board()


#===============================================================================
# score
#===============================================================================
def reset_score():
    global score
    score = 0


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
    global valid_keys
    ui.switch_pause()
    if ui.is_pause():
        valid_keys = PAUSE_KEYS
    else:
        valid_keys = NORMAL_KEYS


def is_pause():
    return ui.is_pause()


def game_over():
    print "GAME OVER: score %i" % get_score() # game over 的狀況
    quit_game()


def quit_game():
    ui.distory_ui()
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
# tick
#===============================================================================
def tick(t_stamp=[time.time(), 0]):
    # 自動處理
    t_stamp[1] = time.time()
    if t_stamp[1] - t_stamp[0] > T and not is_pause():
        pc, px, py, pdir = piece.get_status()
        if not tetris_core.collide(pc, px, py + 1, pdir, board): #自動落下
            piece.update_status(pc, px, py + 1, pdir)

        elif py < 0: #Game over
            game_over()
            return

        else:  #到底
            tetris_core.place_piece(piece, board)

            # 檢查消去
            complete_lines = board.get_complete_lines()
            if complete_lines:
                # 消去
                sound.distroy_sound.play()
                board.strip_board_lines(complete_lines)
                ui.clear_ui_lines(complete_lines)
                incr_score(2 ** len(complete_lines))

            pc, px, py, pdir = pieces.new_piece()
            ui.new_focus(pc, px, py, pdir)
            piece.update_status(pc, px, py, pdir)

        t_stamp[0] = t_stamp[1]

    key = ui.get_key()
    if key:
        perform_key_action(key)


if __name__ == '__main__':
    _pc, _px, _py, _pdir = pieces.new_piece() # 第一個piece
    piece.update_status(_pc, _px, _py, _pdir)
    valid_keys = NORMAL_KEYS

    # ui
    ui.init_ui()
    piece.status_changed.connect(ui.update_focus) # 方塊位置變更
    ui.new_focus(_pc, _px, _py, _pdir)

    # sound
    sound.init_sound()

    while 1: # mainloop
        ui.set_animation_rate(N)
        tick()


#### Debug 用的工具

#print [py+y for x,y in piece if 0 not in board[py+y]]
#fill_line = {py+y for x,y in piece if 0 not in board[py+y]}
#for line in board: print line, 0 not in line
#from arrow import draw_arrow ;draw_arrow(AL=BH)
#for y in xrange(BH): print '%2d:'%y+''.join('%5d'%board[y][x] for x in xrange(BW)) #for debug
