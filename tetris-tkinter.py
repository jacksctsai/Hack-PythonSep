# -*- coding: utf-8 -*-
import random
import sys
import Tkinter

#===============================================================================
# global constant
#===============================================================================
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

#===============================================================================
# piece
#===============================================================================
I_PIECE = 0xf
J_PIECE = 0x2e # J
L_PIECE = 0x47 # L
O_PIECE = 0x66
S_PIECE = 0xC6 # S
T_PIECE = 0x27
Z_PIECE = 0x6C # Z

ALL_PIECES = [I_PIECE, J_PIECE, L_PIECE, O_PIECE, S_PIECE, T_PIECE, Z_PIECE]

PIECE_COLOR = {
    I_PIECE: "red",
    J_PIECE: "#0f0",
    L_PIECE: "#ff0",
    O_PIECE: "#0ff",
    S_PIECE: "#38f",
    T_PIECE: "blue",
    Z_PIECE: "#f0f"
}

#===============================================================================
# drawing transform
#===============================================================================
H, W = 30, 30
map_to_ui_x = lambda i: i * W
map_to_ui_y = lambda j: j * H

def ui_create_rect(i, j, color):
    assert isinstance(i, int)
    assert isinstance(j, int)
    x0 = map_to_ui_x(i)
    y0 = map_to_ui_y(j)
    x1 = map_to_ui_x(i + 1)
    y1 = map_to_ui_y(j + 1)
    scr.create_rectangle(x0, y0, x1, y1, fill=color)


def redraw_ui():
    scr.delete("all")

    for i, j in [(i, j) for i in range(BOARD_WIDTH) for j in range(BOARD_HEIGHT)]:
        if (i - px, j - py) in piece:
            color = PIECE_COLOR[pc]
        else:
            color = PIECE_COLOR.get(board[j][i], "#000")
        ui_create_rect(i, j, color)


#===============================================================================
# 
#===============================================================================
score = 0
board = [ [0xf if j == BOARD_HEIGHT else 0] * BOARD_WIDTH + [0xf] * 2 for j in range(BOARD_HEIGHT + 2 + 1) ]
new_piece = lambda pc: ([((z >> 2) + 1, z & 3) for z in range(16) if (pc >> z) & 1], 3, -2, pc)
collide = lambda piece, px, py: [1 for (i, j) in piece if board[j + py][i + px]] #是否碰撞
piece, px, py, pc = new_piece(random.choice(ALL_PIECES)) # 第一個piece

def tick(e=None):
    global piece, px, py, pc, tickcnt, board, score

    keys = e.keysym if e else  "" # get key event

    npx = px + (-1 if keys == "Left" else (1 if keys == "Right" else 0)) # 左-1右1否則0
    npiece = [(j, 3 - i) for (i, j) in piece] if keys == "Up" else piece   #rotate
    if not collide(npiece, npx, py): piece, px = npiece, npx
    if keys == "Down": py = (j for j in range(py, BOARD_HEIGHT) if collide(piece, px, j + 1)).next()

    if e == None:
        if collide(piece, px, py + 1):
            if py < 0: sys.exit("GAME OVER: score %i" % score) # game over 的狀況
            for i, j in piece: board[j + py][i + px] = pc
            piece, px, py, pc = new_piece(random.choice(ALL_PIECES))
        else: py += 1

        nb = [l for l in board[:BOARD_HEIGHT] if 0 in l] + board[BOARD_HEIGHT:] # 沒有被填滿的
        s = len(board) - len(nb)
        if s: score, board = score + 2 ** s, [board[-1][:] for j in range(s)] + nb
        scr.after(300, tick)

    redraw_ui()


#  for line in board: print '\t'.join(str(v) for v in line)
#  print len(board)
#  print px,py

if __name__ == '__main__':
    scr = Tkinter.Canvas(width=map_to_ui_x(BOARD_WIDTH), height=map_to_ui_y(BOARD_HEIGHT), bg="#000")
    scr.after(300, tick)
    scr.bind_all("<Key>", tick)
    scr.pack()
    scr.mainloop()
