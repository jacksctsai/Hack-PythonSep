# -*- coding=utf8 -*-

'''
* 參考 weijr 老師的 tetris in tkinter -- ``http://weijr-note.blogspot.tw/2007/04/tetris-program-in-lines.html``

* full documents of Vpython -- ``http://vpython.org/contents/docs/visual/index.html``
'''

# update: 2012.07.29 完成大部分功能
# update: 2012.09.01 加入暫停與 hjkl 方向鍵控制 (Vim 操作練習?!)

from __future__ import division
from random import choice
import sound
import time
import visual
any = __builtins__.any


#===============================================================================
# 設定值
#===============================================================================
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

blk = { 0x0f:(0, 0, 1), 0x2e:(0, 1, 1), 0x27:(0, 1, 0), 0x47:(1, 0, 1), 0xC6:(1, 0, 0), 0x6C:(1, 1, 0), 0x66:(1, 0.6, 0) }
score, R, N, T = 0, 0.9, 100, 0.5

new_piece = lambda pc: ([((z >> 2) + 1, z & 3) for z in xrange(16) if (pc >> z) & 1], 3, -2, pc)


#===============================================================================
# ui
#===============================================================================
def init_ui():
    visual.scene.center = ((BOARD_WIDTH - 1) / 2, (BOARD_HEIGHT - 1) / 2)
    visual.scene.width = BOARD_WIDTH * 35
    visual.scene.height = BOARD_HEIGHT * 35
    visual.scene.forward = (0, 0, +1)
    visual.scene.up = 0, -1, 0
    visual.scene.lights = [
        visual.distant_light(direction=(0.22, 0.44, -0.88), color=visual.color.gray(0.8)),
        visual.distant_light(direction=(-0.88, -0.22, +0.44), color=visual.color.gray(0.3))]
    visual.scene.autoscale = False
    #visual.scene.show_rendertime = 1
    visual.scene.pause = False

    visual.points(pos=[(x, y) for x in xrange(BOARD_WIDTH) for y in xrange(BOARD_HEIGHT)])


def set_animation_rate(rate):
    assert isinstance(rate, int), rate
    visual.rate(rate)


def clear_ui_lines(fn):
    d_line = [obj for obj in visual.scene.objects if type(obj) is visual.box and obj.y in fn]
    for _ in xrange(10):
        set_animation_rate(20)
        for obj in d_line:
            obj.opacity -= 1 / 10
    for obj in d_line:
        obj.visible = 0

    # 下降
    for n in fn:
        for obj in (obj for obj in visual.scene.objects if type(obj) is visual.box and obj.y < n):
            obj.y += 1


new_focus = lambda piece, pc: [visual.box(pos=p, color=blk[pc], size=(R, R, R)) for p in piece]


#===============================================================================
# ui : pause
#===============================================================================
def is_pause():
    return visual.scene.pause


def switch_pause():
    visual.scene.pause = (not visual.scene.pause)


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
    clear_ui_lines(fn)
    return fn


#===============================================================================
# 
#===============================================================================
def game_over():
    exit("GAME OVER: score %i" % get_score()) # game over 的狀況


#===============================================================================
# tick
#===============================================================================
def tick(t_stamp=[time.time(), 0]):
  global piece, px, py, pc, focus

  # 自動處理
  t_stamp[1] = time.time()
  if t_stamp[1] - t_stamp[0] > T and not is_pause():
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

      piece, px, py, pc = new_piece(choice(blk.keys()))
      focus = new_focus(piece, pc)

    t_stamp[0] = t_stamp[1]

  # 鍵盤控制
  def move(key):
    if key in ('down', 'j'):
      py = (j for j in xrange(py, BOARD_HEIGHT) if collide(piece, px, j + 1)).next()# 找出第一個會碰撞的
    elif key in ('up', 'k'):
      sound.rotate_sound.play()
      npiece = [(j, 3 - i) for (i, j) in piece]
      if not collide(npiece, px, py): piece = npiece
    elif key in ('left', 'right', 'h', 'H', 'l', 'L'):
      npx = px + (-1 if key in ('left', 'h', 'H') else 1)
      if not collide(piece, npx, py): px = npx

  if visual.scene.kb.keys:
    key = visual.scene.kb.getkey()

    if key == 'p':
      switch_pause()
    elif key == 'q':
      visual.scene.visible = False
      exit()

    if not scene.pause:
      move(key)

  # 方塊位置變更
  for i in xrange(4): focus[i].pos = visual.vector(px, py) + piece[i]


# mainloop
init_ui()
sound.init_sound()

piece, px, py, pc = new_piece(choice(blk.keys()))
focus = new_focus(piece, pc)
while 1:
    set_animation_rate(N)
    tick()




#### Debug 用的工具

#print [py+y for x,y in piece if 0 not in board[py+y]]
#fill_line = {py+y for x,y in piece if 0 not in board[py+y]}
#for line in board: print line, 0 not in line
#from arrow import draw_arrow ;draw_arrow(AL=BH)
#for y in xrange(BH): print '%2d:'%y+''.join('%5d'%board[y][x] for x in xrange(BW)) #for debug
