# -*- coding=utf8 -*-

'''
* 參考 weijr 老師的 tetris in tkinter -- ``http://weijr-note.blogspot.tw/2007/04/tetris-program-in-lines.html``

* full documents of Vpython -- ``http://vpython.org/contents/docs/visual/index.html``
'''

# update: 2012.07.29 完成大部分功能
# update: 2012.09.01 加入暫停與 hjkl 方向鍵控制 (Vim 操作練習?!)

from __future__ import division
import copy
import random
import sound
import time
import ui
any = __builtins__.any


#===============================================================================
# 設定值
#===============================================================================
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
PIECE_INIT_X = 3
PIECE_INIT_Y = -2

#===============================================================================
# piece
#===============================================================================
I_PIECE = 0x0f
J_PIECE = 0x2e
L_PIECE = 0x47
O_PIECE = 0x66
S_PIECE = 0xC6
T_PIECE = 0x27
Z_PIECE = 0x6C


ALL_PIECES = [
    I_PIECE,
    J_PIECE,
    L_PIECE,
    O_PIECE,
    S_PIECE,
    T_PIECE,
    Z_PIECE
]


"""
shape = lambda pc: [((z >> 2) + 1, z & 3) for z in range(16) if (pc >> z) & 1]
"""
PIECE_SHAPE = {
    I_PIECE: [(1, 0), (1, 1), (1, 2), (1, 3)],
    J_PIECE: [(1, 1), (1, 2), (1, 3), (2, 1)],
    L_PIECE: [(1, 0), (1, 1), (1, 2), (2, 2)],
    O_PIECE: [(1, 1), (1, 2), (2, 1), (2, 2)],
    S_PIECE: [(1, 1), (1, 2), (2, 2), (2, 3)],
    T_PIECE: [(1, 0), (1, 1), (1, 2), (2, 1)],
    Z_PIECE: [(1, 2), (1, 3), (2, 1), (2, 2)]
}


PIECE_COLOR = {
    I_PIECE: (0, 0, 1),
    J_PIECE: (0, 1, 1),
    L_PIECE: (1, 0, 1),
    O_PIECE: (1, 0.6, 0),
    S_PIECE: (1, 0, 0),
    T_PIECE: (0, 1, 0),
    Z_PIECE: (1, 1, 0)
}


def new_piece():
    """
    new_piece = lambda pc: ([((z >> 2) + 1, z & 3) for z in xrange(16) if (pc >> z) & 1], 3, -2, pc)
    """
    p = random.choice(ALL_PIECES)
    p_shape = copy.deepcopy(PIECE_SHAPE[p])
    return p_shape, PIECE_INIT_X, PIECE_INIT_Y, p


score, N, T = 0, 100, 0.5


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
def collide(piece, px, py):
    assert isinstance(px, int), px
    assert isinstance(py, int), py
    for (i, j) in piece:
        x = px + i
        y = py + j
        if not (0 <= x < BOARD_WIDTH):
            return True
        if y >= BOARD_HEIGHT:
            return True
        if y < 0:
            continue
        if board[y][x]:
            return True
    return False


#===============================================================================
# board
#===============================================================================
def new_board_lines(num):
    assert isinstance(num, int), num
    return [[0] * BOARD_WIDTH for j in range(num)]


board = new_board_lines(BOARD_HEIGHT)


def place_piece(piece, px, py, pc):
    """
    for i, j in piece:
        board[j + py][i + px] = pc
    """
    for i, j in piece:
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
        if 0 in line:
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
def game_over():
    print "GAME OVER: score %i" % get_score() # game over 的狀況
    quit_game()


def quit_game():
    ui.distory_ui()
    exit()


#===============================================================================
# move
#===============================================================================
def move(key):
    # 鍵盤控制
    global piece, px, py
    if key in ('down', 'j'):
        py = (j for j in xrange(py, BOARD_HEIGHT) if collide(piece, px, j + 1)).next()# 找出第一個會碰撞的
    elif key in ('up', 'k'):
        sound.rotate_sound.play()
        npiece = [(j, 3 - i) for (i, j) in piece]
        if not collide(npiece, px, py): piece = npiece
    elif key in ('left', 'right', 'h', 'H', 'l', 'L'):
        npx = px + (-1 if key in ('left', 'h', 'H') else 1)
        if not collide(piece, npx, py): px = npx


#===============================================================================
# tick
#===============================================================================
def tick(t_stamp=[time.time(), 0]):
  global piece, px, py, pc

  # 自動處理
  t_stamp[1] = time.time()
  if t_stamp[1] - t_stamp[0] > T and not ui.is_pause():
    if not collide(piece, px, py + 1): #自動落下
      py += 1

    elif py < 0: #Game over
      game_over()
      return

    else:  #到底
      place_piece(piece, px, py, pc)

      # 檢查消去
      fn = clear_complete_lines()
      if fn:
        incr_score(2 ** len(fn))

      piece, px, py, pc = new_piece()
      ui.new_focus(piece, PIECE_COLOR[pc])

    t_stamp[0] = t_stamp[1]

  key = ui.get_key()
  if key:
    if key == 'p':
      ui.switch_pause()
    elif key == 'q':
      quit_game()

    if not ui.is_pause():
      move(key)

  # 方塊位置變更
  ui.update_focus(piece, px, py)


# mainloop
ui.init_ui(BOARD_WIDTH, BOARD_HEIGHT)
sound.init_sound()

piece, px, py, pc = new_piece()
ui.new_focus(piece, PIECE_COLOR[pc])
while 1:
    ui.set_animation_rate(N)
    tick()




#### Debug 用的工具

#print [py+y for x,y in piece if 0 not in board[py+y]]
#fill_line = {py+y for x,y in piece if 0 not in board[py+y]}
#for line in board: print line, 0 not in line
#from arrow import draw_arrow ;draw_arrow(AL=BH)
#for y in xrange(BH): print '%2d:'%y+''.join('%5d'%board[y][x] for x in xrange(BW)) #for debug
