#! /usr/bin/env python3

"""ProblemViewWidget の実装ファイル
:file: problemviewwidget.py
:author: Yusuke Matsunaga (松永 裕介)

Copyright (C) 2019, 2020 Yusuke Matsunaga
All rights reserved.
"""

import math as m
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.problem import Problem
from core.position import Position
from gui.viewwidget import ViewWidget


class ProblemViewWidget(ViewWidget):
    """問題を表示するウィジェット"""

    def __init__(self, parent=None):
        super(ProblemViewWidget, self).__init__(parent)

        # 問題
        self.__Problem = None

        # サイズ関係の初期化
        self.set_size(0, 0)

    def set_problem(self, problem):
        """問題をセットする．
        :param Problem problem: 問題
        """

        self.__Problem = problem

        # サイズを計算する．
        # ブロックの最大幅と最大高さを求め，
        # すべてのブロックにそのサイズの矩形を割り当てる．
        max_width = 3
        max_height = 3
        for block in problem.block_list:
            if max_width < block.width:
                max_width = block.width
            if max_height < block.height:
                max_height = block.height
        self.__WidthUnit = max_width + 1
        self.__HeightUnit = max_height + 1

        # ブロック数の平方をもとめ，それを行数，列数にする．
        # もちろん，その値を切り上げた整数値を求める．
        n = problem.block_num
        ncols = m.ceil(m.sqrt(n))
        nrows = (n + ncols - 1) // ncols
        self.set_size(ncols * self.__WidthUnit, nrows * self.__HeightUnit)

        # 各ブロックの配置位置を計算する．
        self.__BlockPosDict = dict()
        x_pos = 0
        y_pos = 0
        for block in problem.block_list:
            x1 = x_pos * self.__WidthUnit
            y1 = y_pos * self.__HeightUnit
            self.__BlockPosDict[block.block_id] = Position(x1, y1)
            x_pos += 1
            if x_pos == ncols:
                x_pos = 0
                y_pos += 1

    def paintEvent(self, event):
        """paint イベント
        :param Event event: イベント構造体
        """
        painter = self.draw_init()

        painter.save()

        # ブロックの描画
        for block in self.__Problem.block_list:
            p0 = self.__BlockPosDict[block.block_id]
            # ブロックの実際の大きさを考慮して配置位置を補正する．
            dx = ((self.__WidthUnit - block.width) / 2) * self.grid_size
            dy = (self.__HeightUnit - block.height - 1) * self.grid_size

            pos0 = self.pos_to_local(p0) + self.base_pos
            pos0 += QPointF(dx, dy)
            self.draw_block(painter, block, pos0)

            # ブロック番号の描画
            self.set_text_pen(painter)
            p1 = p0 + Position(0, self.__HeightUnit - 1)
            pos1 = self.pos_to_local(p1) + self.base_pos
            w1 = self.__WidthUnit * self.grid_size
            h1 = self.grid_size
            painter.drawText(QRect(pos1.x(), pos1.y(), w1, h1),
                             Qt.AlignCenter,
                             'BLOCK#{}'.format(block.block_id))
        painter.restore()
