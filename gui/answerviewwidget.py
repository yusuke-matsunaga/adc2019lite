#! /usr/bin/env python3

"""AnswerViewWidget の実装ファイル
:file: answerviewwidget.py
:author: Yusuke Matsunaga (松永 裕介)

Copyright (C) 2019, 2020 Yusuke Matsunaga
All rights reserved.
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui.viewwidget import ViewWidget


class AnswerViewWidget(ViewWidget):
    """解答を表示するウィジェット"""

    def __init__(self, parent=None):
        super(AnswerViewWidget, self).__init__(parent)

        # 線分の太さ
        self.__WireWidth = 15

        # 線分用のペン
        self.__WirePen = self.new_pen(QColor(100, 100, 100), self.__WireWidth)

        # 問題
        self.__Problem = None

        # 解答
        self.__Answer = None

        # サイズ関係の初期化
        self.set_size(0, 0)

    def set_answer(self, problem, answer):
        """解答をセットする．
        :param Problem problem: 問題
        :param Answer answer: 解答
        """
        self.__Problem = problem
        self.__Answer = answer
        self.set_size(answer.width, answer.height)
        self.__terminal_set = set()
        for block in problem.block_list:
            block_id = block.block_id
            pos0 = answer.block_pos(block_id)
            for pos1, label in block.pos_label_list:
                pos = pos0 + pos1
                self.__terminal_set.add((pos.x, pos.y))

    def paintEvent(self, event):
        """paint イベント
        :param Event event: イベント構造体
        """
        painter = self.draw_init()

        # ブロックの描画
        painter.save()
        for block in self.__Problem.block_list:
            block_id = block.block_id
            p0 = self.__Answer.block_pos(block_id)
            pos0 = self.pos_to_local(p0) + self.base_pos
            self.draw_block(painter, block, pos0)
        painter.restore()

        # 線分の描画
        painter.save()
        painter.setPen(self.__WirePen)
        for x in range(self.col_num - 1):
            for y in range(self.row_num):
                x0, y0 = x,     y
                x1, y1 = x + 1, y
                val0 = self.__Answer.label(x0, y0)
                val1 = self.__Answer.label(x1, y1)

                if val0 != val1 or val0 == 0:
                    continue

                pos0 = self.pos_to_local(x0, y0) + self.base_pos
                cx0 = pos0.x() + self.grid_size / 2
                cx1 = cx0 + self.grid_size
                cy = pos0.y() + self.grid_size / 2

                dx = self.grid_size - self.inner_margin + self.__WireWidth / 2
                if self.is_terminal(x0, y0):
                    cx0 = pos0.x() + dx
                if self.is_terminal(x1, y1):
                    cx1 = pos0.x() + dx

                painter.drawLine(cx0, cy, cx1, cy)

        for y in range(self.row_num - 1):
            for x in range(self.col_num):
                x0, y0 = x, y
                x1, y1 = x, y + 1
                val0 = self.__Answer.label(x0, y0)
                val1 = self.__Answer.label(x1, y1)

                if val0 != val1 or val0 == 0:
                    continue

                pos0 = self.pos_to_local(x0, y0) + self.base_pos
                cx = pos0.x() + self.grid_size / 2
                cy0 = pos0.y() + self.grid_size / 2
                cy1 = cy0 + self.grid_size

                dy = self.grid_size - self.inner_margin + self.__WireWidth / 2
                if self.is_terminal(x0, y0):
                    cy0 = pos0.y() + dy
                if self.is_terminal(x1, y1):
                    cy1 = pos0.y() + dy

                painter.drawLine(cx, cy0, cx, cy1)

        painter.restore()

    def is_terminal(self, x, y):
        """端子かどうか調べる．
        :param int x, y: 座標
        """
        if (x, y) in self.__terminal_set:
            return True
        return False
