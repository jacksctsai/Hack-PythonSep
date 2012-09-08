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

import boards
import pieces
import signals
import sound
import ui


#===============================================================================
# 設定值
#===============================================================================
score, N, T = 0, 100, 0.5


#===============================================================================
# signal
#===============================================================================
piece_changed = signals.Signal()


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
# core function
#===============================================================================
def collide(pc, px, py, pdir):
    """
    collide = lambda piece, px, py: [1 for (i, j) in piece if board[j + py][i + px]] #是否碰撞
    """
    assert isinstance(px, int), px
    assert isinstance(py, int), py
    assert isinstance(pdir, int), pdir
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


def place_piece(pc, px, py, pdir):
    """
    for i, j in piece:
        board[j + py][i + px] = pc
    """
    p_shape = pieces.get_piece_shape(pc, pdir)
    for i, j in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < boards.BOARD_WIDTH):
            continue
        if not (0 <= y < boards.BOARD_HEIGHT):
            continue
        board[y][x] = pc


def clear_complete_lines():
    global board

    nb = []
    fn = []
    for j, line in enumerate(board):
        if pieces.EMPTY in line:
            nb.append(line)
        else:
            fn.append(j)

    if not fn:
        return fn

    board = boards.create_board_lines(len(fn), pieces.EMPTY) + nb

    # 消去
    sound.distroy_sound.play()
    ui.clear_ui_lines(fn)
    return fn


#===============================================================================
# action
#===============================================================================
def drop_piece():
    """
    py = (j for j in xrange(py, BOARD_HEIGHT) if collide(pc, px, j + 1, pdir)).next()# 找出第一個會碰撞的
    """
    global py
    for j in range(py, boards.BOARD_HEIGHT):
        if collide(pc, px, j + 1, pdir):
            py = j
            break
    piece_changed.emit(pc, px, py, pdir)


def rotate_piece():
    global pdir
    sound.rotate_sound.play()
    npdir = (pdir + 1) % 4
    if collide(pc, px, py, npdir):
        return
    pdir = npdir
    piece_changed.emit(pc, px, py, pdir)


def move_piece_left():
    global px
    npx = px - 1
    if collide(pc, npx, py, pdir):
        return
    px = npx
    piece_changed.emit(pc, px, py, pdir)


def move_piece_right():
    global px
    npx = px + 1
    if collide(pc, npx, py, pdir):
        return
    px = npx
    piece_changed.emit(pc, px, py, pdir)


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
    global pc, px, py, pdir

    # 自動處理
    t_stamp[1] = time.time()
    if t_stamp[1] - t_stamp[0] > T and not is_pause():
        if not collide(pc, px, py + 1, pdir): #自動落下
            py += 1
            piece_changed.emit(pc, px, py, pdir)

        elif py < 0: #Game over
            game_over()
            return

        else:  #到底
            place_piece(pc, px, py, pdir)

            # 檢查消去
            fn = clear_complete_lines()
            if fn:
                incr_score(2 ** len(fn))

            pc, px, py, pdir = pieces.new_piece()
            ui.new_focus(pc, px, py, pdir)

        t_stamp[0] = t_stamp[1]

    key = ui.get_key()
    if key:
        perform_key_action(key)


if __name__ == '__main__':
    board = boards.create_board_lines(boards.BOARD_HEIGHT, pieces.EMPTY)
    pc, px, py, pdir = pieces.new_piece()
    valid_keys = NORMAL_KEYS

    # ui
    ui.init_ui(boards.BOARD_WIDTH, boards.BOARD_HEIGHT)
    piece_changed.connect(ui.update_focus) # 方塊位置變更
    ui.new_focus(pc, px, py, pdir)

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
