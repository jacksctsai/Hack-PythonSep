import copy
import Tkinter

import boards
import pieces

UNIT_X = 30
UNIT_Y = 30

BACKGROUND_COLOR = '#000'

PIECE_COLOR = {
    pieces.I_PIECE: "red",
    pieces.J_PIECE: "#0f0",
    pieces.L_PIECE: "#ff0",
    pieces.O_PIECE: "#0ff",
    pieces.S_PIECE: "#38f",
    pieces.T_PIECE: "blue",
    pieces.Z_PIECE: "#f0f",
    pieces.EMPTY: BACKGROUND_COLOR
}


#===============================================================================
# redraw
#===============================================================================
UI_BOARD = []
UI_PIECE = []
def redraw_board(board):
    pc, px, py, pdir = UI_PIECE
    p_shape = pieces.get_piece_shape(pc, pdir)
    piece_region = [(i + px, j + py) for i, j in p_shape]

    for i, j in [(i, j) for i in range(boards.BOARD_WIDTH) for j in range(boards.BOARD_HEIGHT)]:
        if (i, j) in piece_region: # ignore piece region
            continue
        if board[j][i] == UI_BOARD[j][i]: # board (i, j) not change
            continue
        UI_BOARD[j][i] = board[j][i]
        color = PIECE_COLOR.get(board[j][i], BACKGROUND_COLOR)
        ui_change_rect_color(i, j, color)


def redraw_piece(pc, px, py, pdir):
    global UI_PIECE
    opc, opx, opy, opdir = UI_PIECE
    old_shape = pieces.get_piece_shape(opc, opdir)
    new_shape = pieces.get_piece_shape(pc, pdir)
    old_region = set([(i + opx, j + opy) for i, j in old_shape])
    new_region = set([(i + px, j + py) for i, j in new_shape])

    if pc == opc:
        change_region = old_region ^ new_region
    else:
        change_region = old_region | new_region

    for i, j in change_region:
        if i < 0:
            continue
        if j < 0:
            continue
        if (i, j) in new_region:
            color = PIECE_COLOR[pc]
        else:
            color = PIECE_COLOR.get(UI_BOARD[j][i], BACKGROUND_COLOR)

        ui_change_rect_color(i, j, color)

    UI_PIECE = [pc, px, py, pdir]


UI_RECT_ID = []
def ui_change_rect_color(i, j, color):
    rect_id = UI_RECT_ID[j][i]
    scr.itemconfig(rect_id, fill=color)


#===============================================================================
# tick
#===============================================================================
EVENT_CALLBACK = lambda *args, **kwargs: None


TICK_PERIOD = 300
def tick():
    more_event = True
    while more_event:
        more_event = EVENT_CALLBACK()
    scr.after(300, tick)


#===============================================================================
# init
#===============================================================================
scr = None
def init_ui(board, pc, px, py, pdir, event_callback):
    global scr, EVENT_CALLBACK
    global UI_BOARD, UI_RECT_ID, UI_PIECE

    EVENT_CALLBACK = event_callback

    scr = Tkinter.Canvas(width=map_to_ui_x(boards.BOARD_WIDTH), height=map_to_ui_y(boards.BOARD_HEIGHT), bg=BACKGROUND_COLOR)
    scr.bind_all("<Key>", EVENT_CALLBACK)
    scr.pack()

    UI_BOARD = copy.deepcopy(board)
    UI_PIECE = [pc, px, py, pdir]

    p_shape = pieces.get_piece_shape(pc, pdir)
    piece_region = [(i + px, j + py) for i, j in p_shape]

    UI_RECT_ID = []
    for j in range(boards.BOARD_HEIGHT):
        id_list = []
        for i in range(boards.BOARD_WIDTH):
            if (i, j) in piece_region:
                color = PIECE_COLOR[pc]
            else:
                color = BACKGROUND_COLOR
            rect_id = ui_create_rect(i, j, color)
            id_list.append(rect_id)
        UI_RECT_ID.append(id_list)


def map_to_ui_x(i):
    return i * UNIT_X


def map_to_ui_y(j):
    return j * UNIT_Y


def ui_create_rect(i, j, color):
    assert isinstance(i, int), i
    assert isinstance(j, int), j
    x0 = map_to_ui_x(i)
    y0 = map_to_ui_y(j)
    x1 = map_to_ui_x(i + 1)
    y1 = map_to_ui_y(j + 1)
    return scr.create_rectangle(x0, y0, x1, y1, fill=color)


#===============================================================================
# main loop
#===============================================================================
def main_loop():
    scr.after(300, tick)
    scr.mainloop()
