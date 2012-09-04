# -*- coding=utf8 -*-

import visual

import pieces

R = 0.9

PIECE_COLOR = {
    pieces.I_PIECE: (0, 0, 1),
    pieces.J_PIECE: (0, 1, 1),
    pieces.L_PIECE: (1, 0, 1),
    pieces.O_PIECE: (1, 0.6, 0),
    pieces.S_PIECE: (1, 0, 0),
    pieces.T_PIECE: (0, 1, 0),
    pieces.Z_PIECE: (1, 1, 0)
}


def init_ui(board_width, board_height):
    visual.scene.center = ((board_width - 1) / 2, (board_height - 1) / 2)
    visual.scene.width = board_width * 35
    visual.scene.height = board_height * 35
    visual.scene.forward = (0, 0, +1)
    visual.scene.up = 0, -1, 0
    visual.scene.lights = [
        visual.distant_light(direction=(0.22, 0.44, -0.88), color=visual.color.gray(0.8)),
        visual.distant_light(direction=(-0.88, -0.22, +0.44), color=visual.color.gray(0.3))]
    visual.scene.autoscale = False
    #visual.scene.show_rendertime = 1
    visual.scene.pause = False

    visual.points(pos=[(x, y) for x in xrange(board_width) for y in xrange(board_height)])


def distory_ui():
    visual.scene.visible = False


def set_animation_rate(rate):
    assert isinstance(rate, int), rate
    visual.rate(rate)


def get_key():
    if visual.scene.kb.keys:
        return visual.scene.kb.getkey()
    return None


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


focus = None
def new_focus(pc, pdir):
    global focus
    color = PIECE_COLOR[pc]
    p_shape = pieces.get_piece_shape(pc, pdir)
    focus = [visual.box(pos=p, color=color, size=(R, R, R)) for p in p_shape]


def update_focus(pc, px, py, pdir):
    p_shape = pieces.get_piece_shape(pc, pdir)
    for i in xrange(4): focus[i].pos = visual.vector(px, py) + p_shape[i]


#===============================================================================
# ui : pause
#===============================================================================
def is_pause():
    return visual.scene.pause


def switch_pause():
    visual.scene.pause = (not visual.scene.pause)
