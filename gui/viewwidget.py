#! /usr/bin/env python3

### @file viewwidget.py
### @brief ViewWidget の実装ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2019, 2020 Yusuke Matsunaga
### All rights reserved.

import math as m
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.position import Position

### @brief 向きを表す文字列を正規化する．
def make_dir(label1, label2) :
    if label1 == 'n' :
        if label2 == 'e' :
            return 'ne'
        elif label2 == 'w' :
            return 'nw'
        elif label2 == 'n' :
            return None
        else :
            assert False
    elif label1 == 'e' :
        if label2 == 'n' :
            return 'ne'
        elif label2 == 's' :
            return 'se'
        elif label2 == 'e' :
            return None
        else :
            assert False
    elif label1 == 's' :
        if label2 == 'e' :
            return 'se'
        elif label2 == 'w' :
            return 'sw'
        elif label2 == 's' :
            return None
        else :
            assert False
    elif label1 == 'w' :
        if label2 == 'n' :
            return 'nw'
        elif label2 == 's' :
            return 'sw'
        elif label2 == 'w' :
            return None
        else :
            assert False
    else :
        assert False

### @brief ブロックを囲むセグメントのリストを作る．
def make_segment_list(block) :

    grid_set = set()
    for pos in block.pos_list :
        grid_set.add(pos)

    segment_dict = dict()
    dpos_n  = Position( 0, -1)
    dpos_e  = Position( 1,  0)
    dpos_s  = Position( 0,  1)
    dpos_w  = Position(-1,  0)
    dpos_se = Position( 1,  1)
    for pos in block.pos_list :
        pos_n = pos.adjacent_pos('n')
        pos_e = pos.adjacent_pos('e')
        pos_s = pos.adjacent_pos('s')
        pos_w = pos.adjacent_pos('w')
        pos_se = pos_s.adjacent_pos('e')
        if pos_n not in grid_set :
            segment_dict[pos] = (pos_e, 'n')
        if pos_e not in grid_set :
            segment_dict[pos_e] = (pos_se, 'e')
        if pos_s not in grid_set :
            segment_dict[pos_se] = (pos_s, 's')
        if pos_w not in grid_set :
            segment_dict[pos_s] = (pos, 'w')

    # segment_dict の要素を一つ取り出す．
    for first_pos, (last_pos, dlabel) in segment_dict.items() :
        break
    else :
        assert False

    segment_list = list()
    dlabel0 = dlabel
    while True :
        pos1, dlabel1 = segment_dict[last_pos]
        d = make_dir(dlabel, dlabel1)
        if d is not None :
            segment_list.append( (last_pos, d) )
        if pos1 == first_pos :
            break
        last_pos = pos1
        dlabel = dlabel1
    d = make_dir(dlabel0, dlabel1)
    segment_list.append( (first_pos, d) )
    return segment_list


### @brief ブロックを描画するウィジェットの基底クラス
class ViewWidget(QWidget) :

    ### @brief 初期化
    def __init__(self, parent = None) :

        super(ViewWidget, self).__init__(parent)

        #
        # スタイルを定義しているパラメータ
        #

        # 周辺部分の幅
        self.__FringeSize  = 10
        # マスの大きさ
        self.__GridLength  = 50
        # 内枠の幅
        self.__InnerMargin = 5
        # 罫線の太さ
        self.__LineWidth   = 3
        # フォントサイズ
        self.__FontSize    = 16

        # グリッド描画用のサイズ
        self.__GridSize    = QSize(self.__GridLength, self.__GridLength)

        # 周辺部分の色
        self.__FrameColor  = QColor(180, 150, 100)

        # 盤面の色
        self.__BanColor    = QColor(0xB0, 0xB0, 0xB0)

        # ブロック用の色

        # Iブロックの色(Cyan)
        self.__I_BlockColor  = QColor(0x00, 0xFF, 0xFF)

        # Oブロックの色(Yellow)
        self.__O_BlockColor  = QColor(0xFF, 0xFF, 0x00)

        # Tブロックの色(Magenta)
        self.__T_BlockColor  = QColor(0xFF, 0x00, 0xFF)

        # Jブロックの色(Blue)
        self.__J_BlockColor  = QColor(0x00, 0x00, 0xFF)

        # Lブロックの色(Orange)
        self.__L_BlockColor  = QColor(0xFF, 0xA5, 0x00)

        # Sブロックの色(Green)
        self.__S_BlockColor  = QColor(0x00, 0xFF, 0x00)

        # Zブロックの色(Red)
        self.__Z_BlockColor  = QColor(0xFF, 0x00, 0x00)

        # 罫線用のペン
        self.__LinePen     = self.new_pen(QColor(0, 0, 0), self.__LineWidth)

        # テキスト用のペン
        self.__TextPen     = QPen()

        # 数字用のフォント
        self.__NumFont = QFontDatabase.systemFont(QFontDatabase.GeneralFont)
        self.__NumFont.setBold(True)
        self.__NumFont.setPointSize(self.__FontSize)

        # フォントメトリックを計算しておく．
        fm = QFontMetrics(self.__NumFont)
        self.__NumWidth = float(fm.width("99")) * 1.4
        self.__NumHeight = float(fm.height()) * 1.4

        # ウィジェット全体のサイズ
        self.__BanWidth = 0
        self.__BanHeight = 0

        # ビューポートのパラメータ
        self.__X0 = 0
        self.__Y0 = 0
        self.__W = 0
        self.__H = 0

        self.setMouseTracking(True)

        self.set_size(0, 0)


    ### @brief サイズヒントを返す．
    def sizeHint(self) :
        return QSize(self.__BanWidth, self.__BanHeight)


    ### @brief 盤面のサイズを設定する．
    ### @param[in] width 幅
    ### @param[in] height 高さ
    ###
    ### 以前の内容はクリアされる．
    def set_size(self, width, height) :
        self.__ColNum = width
        self.__RowNum = height

        self.__BanWidth = width * self.__GridLength + self.__FringeSize * 2
        self.__BanHeight = height * self.__GridLength + self.__FringeSize * 2


    ### @brief paintEvent() の初期化処理
    ### @return ペインタを返す．
    def draw_init(self) :

        # ウインドウサイズの縦横比と盤面の縦横比が異なる時の補正
        w = self.width()
        h = self.height()

        w1_f = (self.__BanWidth * h) / float(self.__BanHeight)
        h1_f = (self.__BanHeight * w) / float(self.__BanWidth)
        w1 = int(w1_f)
        h1 = int(h1_f)

        if w1 > w :
            assert h1 <= h
            self.__X0 = 0
            self.__Y0 = (h - h1) / 2
            self.__W = w
            self.__H = h1
        else :
            self.__X0 = (w - w1) / 2
            self.__Y0 = 0
            self.__W = w1
            self.__H = h

        # ペインタの生成
        painter = QPainter(self)

        painter.setWindow(0, 0, self.__BanWidth, self.__BanHeight)
        painter.setViewport(self.__X0, self.__Y0, self.__W, self.__H)
        painter.setFont(self.__NumFont)

        # 外枠の描画
        painter.fillRect(0, 0, self.__BanWidth, self.__BanHeight, self.__FrameColor)

        # 盤
        painter.fillRect(self.__FringeSize, self.__FringeSize,
                         self.__BanWidth - self.__FringeSize * 2,
                         self.__BanHeight - self.__FringeSize * 2,
                         self.__BanColor)

        return painter


    ### @brief ブロックを描画する．
    ### @param[in] painter ペインタ
    ### @param[in] block 対象のブロック
    ### @param[in] pos0 ブロックの左上隅の座標
    def draw_block(self, painter, block, pos0) :
        polygon = QPolygonF()
        for pos1, d1 in make_segment_list(block) :
            lpos = self.block_pos(pos1, d1) + pos0
            polygon << lpos
        path = QPainterPath()
        path.addPolygon(polygon)
        if block.type == 'I' :
            painter.fillPath(path, self.__I_BlockColor)
        elif block.type == 'O' :
            painter.fillPath(path, self.__O_BlockColor)
        elif block.type == 'T' :
            painter.fillPath(path, self.__T_BlockColor)
        elif block.type == 'J' :
            painter.fillPath(path, self.__J_BlockColor)
        elif block.type == 'L' :
            painter.fillPath(path, self.__L_BlockColor)
        elif block.type == 'S' :
            painter.fillPath(path, self.__S_BlockColor)
        elif block.type == 'Z' :
            painter.fillPath(path, self.__Z_BlockColor)

        for pos1, label in block.pos_label_list :
            lpos = self.pos_to_local(pos1) + pos0
            painter.setPen(self.__LinePen)
            painter.drawRect(lpos.x() + self.__InnerMargin, lpos.y() + self.__InnerMargin,
                             self.__GridLength - self.__InnerMargin * 2,
                             self.__GridLength - self.__InnerMargin * 2)
            if label < 10 :
                buff = '{:1d}'.format(label)
            else :
                buff = '{:2d}'.format(label)
            painter.setPen(self.__TextPen)
            painter.drawText(QRect(lpos.x(), lpos.y(), self.__GridLength, self.__GridLength),
                             Qt.AlignCenter, buff)


    ### @brief 描画領域の左上隅の座標を得る．
    @property
    def base_pos(self) :
        return QPointF(self.__FringeSize, self.__FringeSize)


    ### @brief 格子座標からローカル座標を得る．
    ### @param[in] grid_pos 格子座標 ( Position or (int, int) )
    ### @return ローカル座標
    def pos_to_local(self, *args) :
        if len(args) == 1 and isinstance(args[0], Position) :
            grid_pos = args[0]
            x = grid_pos.x
            y = grid_pos.y
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int) :
            x = args[0]
            y = args[1]
        lx = x * self.__GridLength
        ly = y * self.__GridLength
        return QPointF(lx, ly)


    ### @brief ブロックの角の座標を求める．
    ### @param[in] grid_pos 格子座標
    ### @param[in] 角の方角 ( 'ne', 'se', 'sw', 'nw' のいづれか )
    def block_pos(self, grid_pos, d) :
        if d == 'ne' :
            dpos = QPointF(- self.__InnerMargin,   self.__InnerMargin)
        elif d == 'se' :
            dpos = QPointF(- self.__InnerMargin, - self.__InnerMargin)
        elif d == 'sw' :
            dpos = QPointF(  self.__InnerMargin, - self.__InnerMargin)
        elif d == 'nw' :
            dpos = QPointF(  self.__InnerMargin,   self.__InnerMargin)
        else :
            print('d = {}'.format(d))
            assert False
        return self.pos_to_local(grid_pos) + dpos


    ### @brief グリッドサイズを返す．
    @property
    def grid_size(self) :
        return self.__GridLength


    ### @brief グリッド内側のマージンを返す．
    @property
    def inner_margin(self) :
        return self.__InnerMargin


    ### @brief 盤面の幅を返す．
    @property
    def col_num(self) :
        return self.__ColNum


    ### @brief 盤面の高さを返す．
    @property
    def row_num(self) :
        return self.__RowNum


    ### @brief テキスト用のペンをセットする．
    ### @param[in] painter ペインタ
    def set_text_pen(self, painter) :
        painter.setPen(self.__TextPen)


    ### @brief 色と太さを設定したペンを作成する．
    @staticmethod
    def new_pen(color, width) :
        pen = QPen(color)
        pen.setWidth(width)
        return pen
