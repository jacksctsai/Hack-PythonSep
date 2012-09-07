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
import ui


#===============================================================================
# 設定值
#===============================================================================
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

EMPTY = '_'

score, N, T = 0, 100, 0.5


#===============================================================================
# event
#===============================================================================
def piece_changed_event():
    # 方塊位置變更
    ui.update_focus(pc, px, py, pdir)


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
# collide
#===============================================================================
"""
collide = lambda piece, px, py: [1 for (i, j) in piece if board[j + py][i + px]] #是否碰撞
"""
def collide(pc, px, py, pdir):
    assert isinstance(px, int), px
    assert isinstance(py, int), py
    assert isinstance(pdir, int), pdir
    p_shape = pieces.get_piece_shape(pc, pdir)
    for (i, j) in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < BOARD_WIDTH):
            return True
        if y >= BOARD_HEIGHT:
            return True
        if y < 0:
            continue
        if board[y][x] != EMPTY:
            return True
    return False


#===============================================================================
# board
#===============================================================================
def new_board_lines(num):
    assert isinstance(num, int), num
    return [[EMPTY] * BOARD_WIDTH for _ in range(num)]


board = new_board_lines(BOARD_HEIGHT)


def place_piece(pc, px, py, pdir):
    """
    for i, j in piece:
        board[j + py][i + px] = pc
    """
    p_shape = pieces.get_piece_shape(pc, pdir)
    for i, j in p_shape:
        x = px + i
        y = py + j
        if not (0 <= x < BOARD_WIDTH):
            continue
        if not (0 <= y < BOARD_HEIGHT):
            continue
        board[y][x] = pc


def clear_complete_lines():
    global board

    nb = []
    fn = []
    for j, line in enumerate(board):
        if EMPTY in line:
            nb.append(line)
        else:
            fn.append(j)

    if not fn:
        return fn

    board = new_board_lines(len(fn)) + nb

    # 消去
    sound.distroy_sound.play()
    ui.clear_ui_lines(fn)
    return fn


#===============================================================================
# 
#===============================================================================
def drop_piece():
    """
    py = (j for j in xrange(py, BOARD_HEIGHT) if collide(pc, px, j + 1, pdir)).next()# 找出第一個會碰撞的
    """
    global py
    for j in range(py, BOARD_HEIGHT):
        if collide(pc, px, j + 1, pdir):
            py = j
            break
    piece_changed_event()


def rotate_piece():
    global pdir
    sound.rotate_sound.play()
    npdir = (pdir + 1) % 4
    if collide(pc, px, py, npdir):
        return
    pdir = npdir
    piece_changed_event()


def move_piece_left():
    global px
    npx = px - 1
    if collide(pc, npx, py, pdir):
        return
    px = npx
    piece_changed_event()


def move_piece_right():
    global px
    npx = px + 1
    if collide(pc, npx, py, pdir):
        return
    px = npx
    piece_changed_event()


def switch_pause():
    ui.switch_pause()


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
NORMAL_ACTION_MAP = {
    # switch_pause
    'p': switch_pause,
    'P': switch_pause,
    # quit_game
    'q': quit_game,
    'Q': quit_game,
    # drop_piece
    'down': drop_piece,
    'j': drop_piece,
    'J': drop_piece,
    # rotate_piece
    'up': rotate_piece,
    'k': rotate_piece,
    'K': rotate_piece,
    # move_piece_left
    'left': move_piece_left,
    'h': move_piece_left,
    'H': move_piece_left,
    # move_piece_right
    'right': move_piece_right,
    'l': move_piece_right,
    'L': move_piece_right,
}


PAUSE_ACTION_MAP = {
    # switch_pause
    'p': switch_pause,
    'P': switch_pause,
    # quit_game
    'q': quit_game,
    'Q': quit_game,
}


def get_action(key, action_map):
    try:
        return action_map[key]
    except KeyError:
        no_action = lambda *args, **kwargs: None
        return no_action


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
            piece_changed_event()

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
        if is_pause():
            action_map = PAUSE_ACTION_MAP
        else:
            action_map = NORMAL_ACTION_MAP
        act_func = get_action(key, action_map)
        act_func()


if __name__ == '__main__':
    ui.init_ui(BOARD_WIDTH, BOARD_HEIGHT)
    sound.init_sound()

    pc, px, py, pdir = pieces.new_piece()
    ui.new_focus(pc, px, py, pdir)

    while 1: # mainloop
        ui.set_animation_rate(N)
        tick()


#### Debug 用的工具

#print [py+y for x,y in piece if 0 not in board[py+y]]
#fill_line = {py+y for x,y in piece if 0 not in board[py+y]}
#for line in board: print line, 0 not in line
#from arrow import draw_arrow ;draw_arrow(AL=BH)
#for y in xrange(BH): print '%2d:'%y+''.join('%5d'%board[y][x] for x in xrange(BW)) #for debug
