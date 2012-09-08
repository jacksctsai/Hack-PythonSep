# -*- coding: utf-8 -*-
BOARD_WIDTH = 10
BOARD_HEIGHT = 20


def create_board_lines(line_num, empty_piece):
    assert isinstance(line_num, int), line_num
    return [[empty_piece] * BOARD_WIDTH for _ in range(line_num)]
