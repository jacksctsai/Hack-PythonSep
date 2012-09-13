# -*- coding=utf8 -*-
import time

import codec
import sound
import tetris_core
import ui
import zmq_pubsub


#===============================================================================
# 設定值
#===============================================================================
N, T = 100, 0.5
ZMQ_PUBLISH_ENDPOINT = 'tcp://*:5556'
ZMQ_PUBLISH_ID = 'TETRIS'


#===============================================================================
# status
#===============================================================================
piece = tetris_core.Piece()
board = tetris_core.Board()
score = tetris_core.Score()


#===============================================================================
# 
#===============================================================================
def register_publish_encoder(encode_func):
    assert callable(encode_func)
    def pub_encode(*args, **kwargs):
        code_str = encode_func(*args, **kwargs)
        return publisher.publish(code_str)
    return pub_encode


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
    print "GAME OVER: score %i" % score.get_score() # game over 的狀況
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
        fall_rc = tetris_core.try_to_fall_piece(piece, board)
        if fall_rc == tetris_core.FALL_SUCCESS:
            pass

        elif fall_rc == tetris_core.FALL_NO_SPACE: #Game over
            game_over()
            return

        else: # fall_rc == tetris_core.FALL_ON_GROUND
            #到底
            tetris_core.place_piece(piece, board)

            # 檢查消去
            complete_lines = board.get_complete_lines()
            if complete_lines:
                # 消去
                sound.distroy_sound.play()
                board.strip_board_lines(complete_lines)
                ui.clear_ui_lines(complete_lines)
                score.incr_score(2 ** len(complete_lines))

            ui.new_focus()
            piece.rand_new_piece()

        t_stamp[0] = t_stamp[1]

    key = ui.get_key()
    if key:
        perform_key_action(key)


if __name__ == '__main__':
    valid_keys = NORMAL_KEYS

    # publisher
    publisher = zmq_pubsub.ZmqPublisher(ZMQ_PUBLISH_ENDPOINT, ZMQ_PUBLISH_ID)

    # ui
    ui.init_ui()

    # publish
    pub_piece_func = register_publish_encoder(codec.encode_piece)
    pub_board_func = register_publish_encoder(codec.encode_board)
    pub_score_func = register_publish_encoder(codec.encode_score)

    # signal
    piece.status_changed.connect(pub_piece_func)
    piece.status_changed.connect(ui.update_focus) # 方塊位置變更
    board.status_changed.connect(pub_board_func)
    score.value_changed.connect(pub_score_func)

    # 第一個piece
    ui.new_focus()
    piece.rand_new_piece()

    # sound
    sound.init_sound()

    while 1: # mainloop
        ui.set_animation_rate(N)
        tick()
