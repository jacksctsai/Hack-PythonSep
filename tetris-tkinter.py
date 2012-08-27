# -*- coding: utf-8 -*-
import random
import Tkinter

score, bw, bh, H, W = 0, 10, 20, 30, 30
blk = {0xf:"red", 0x2e:"#0f0", 0x27:"blue", 0x47:"#ff0", 0x66:"#0ff", 0xC6:"#38f", 0x6C:"#f0f"}
board = [ [0xf if j == bh else 0] * bw + [0xf] * 2 for j in range(bh + 2 + 1) ]
new_piece = lambda pc: ([((z >> 2) + 1, z & 3) for z in range(16) if (pc >> z) & 1], 3, -2, pc)
collide = lambda piece, px, py: [1 for (i, j) in piece if board[j + py][i + px]] #是否碰撞
piece, px, py, pc = new_piece(random.choice(blk.keys())) # 第一個piece

def tick(e=None):
    global piece, px, py, pc, tickcnt, board, score

    keys = e.keysym if e else  "" # get key event

    npx = px + (-1 if keys == "Left" else (1 if keys == "Right" else 0)) # 左-1右1否則0
    npiece = [(j, 3 - i) for (i, j) in piece] if keys == "Up" else piece   #rotate
    if not collide(npiece, npx, py): piece, px = npiece, npx
    if keys == "Down": py = (j for j in range(py, bh) if collide(piece, px, j + 1)).next()

    if e == None:
        if collide(piece, px, py + 1):
            if py < 0: sys.exit("GAME OVER: score %i" % score) # game over 的狀況
            for i, j in piece: board[j + py][i + px] = pc
            piece, px, py, pc = new_piece(random.choice(blk.keys()))
        else: py += 1

        nb = [l for l in board[:bh] if 0 in l] + board[bh:] # 沒有被填滿的
        s = len(board) - len(nb)
        if s: score, board = score + 2 ** s, [board[-1][:] for j in range(s)] + nb
        scr.after(300, tick)
    scr.delete("all")

    for i, j, c in [(i, j, blk.get(board[j][i], "#000")) for i in range(bw) for j in range(bh)]:
        scr.create_rectangle(i * W, j * H, (i + 1) * W, (j + 1) * H, fill=blk[pc] if (i - px, j - py) in piece else c)

#  for line in board: print '\t'.join(str(v) for v in line)
#  print len(board)
#  print px,py

if __name__ == '__main__':
    scr = Tkinter.Canvas(width=bw * W, height=bh * H, bg="#000")
    scr.after(300, tick)
    scr.bind_all("<Key>", tick)
    scr.pack()
    scr.mainloop()
