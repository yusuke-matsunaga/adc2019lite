#! /usr/bin/env python3

### @file problem.py
### @brief Problem の実装ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2019, 2020 Yusuke Matsunaga
### All rights reserved.

from core.position import Position
from core.block import Block
import sys


### @brief ブロックを出力する．
### @param[in] block 対象のブロック
### @param[in] fout 出力先のファイルオブジェクト
def print_block(block, fout) :
    w = block.width
    h = block.height
    fout.write('BLOCK#{} {}X{}\n'.format(block.block_id, w, h))
    for y in range(h) :
        first = True
        for x in range(w) :
            if first :
                first = False
            else :
                fout.write(',')
            pos = Position(x, y)
            l = block.label(pos)
            if l == -1 : # 範囲外
                fout.write(' 0')
            elif l == 0 : # 範囲内だけどラベルなし
                fout.write(' +')
            else :
                fout.write('{:2d}'.format(l))
        fout.write('\n')


### @brie ADC2019の問題を表すクラス
class Problem :

    ### @brief 初期化
    ### @param[in] width 最大幅
    ### @param[in] height 最大高さ
    def __init__(self, width, height) :
        self.set_size(width, height)

    ### @brief サイズを(再)設定する．
    ### @param[in] width 最大幅
    ### @param[in] height 最大高さ
    ###
    ### 以前の内容は消去される．
    def set_size(self, width, height) :
        self.__max_width = width
        self.__max_height = height
        self.__block_list = []
        self.__terminals_dict = dict()

    ### @brief ブロックを追加する．
    ### @param[in] block_id ブロック番号
    ### @param[in] pos_list ブロックの占める位置のリスト
    ### @param[in] label_dict ブロック上のラベル値の辞書．キーは位置
    ###
    ### - label_dict はラベルを持たない位置の値として0を持つ．
    ### - label_dict はブロックの領域外の位置の値は持たない．
    def add_block(self, block_id, pos_list, label_dict) :
        self.__block_list.append(Block(block_id, pos_list, label_dict))
        for pos, label in label_dict.items() :
            if label > 0 :
                if label not in self.__terminals_dict :
                    self.__terminals_dict[label] = list()
                self.__terminals_dict[label].append( (block_id, pos) )

    ### @brief 内容が設定されていたら True を返す．
    def is_valid(self) :
        return self.max_width > 0

    ### @brief 最大幅を返す．
    @property
    def max_width(self) :
        return self.__max_width

    ### @brief 最大高さを返す．
    @property
    def max_height(self) :
        return self.__max_height

    ### @brief ブロック数を返す．
    @property
    def block_num(self) :
        return len(self.__block_list)

    ### @brief ブロック番号のリストを返す．
    ###
    ### 正確にはブロックリストのジェネレーターを返す．
    @property
    def block_id_list(self) :
        for block in self.__block_list :
            yield block.block_id

    ### @brief ブロックのリストを返す．
    ###
    ### 正確にはブロックリストのジェネレーターを返す．
    @property
    def block_list(self) :
        for block in self.__block_list :
            yield block

    ### @brief ブロックを取り出す．
    ### @param[in] block_id ブロック番号
    def block(self, block_id) :
        assert 0 < block_id <= self.block_num
        block = self.__block_list[block_id - 1]
        assert block.block_id == block_id
        return block

    ### @brief 線分番号のリストを返す．
    ###
    ### 正確にはジェネレーターを返す．
    @property
    def line_id_list(self) :
        for line_id in sorted(self.__terminals_dict.keys()) :
            yield line_id

    ### @brief 端子の情報を返す．
    ### @param[in] line_id 線分番号
    ### @return (block_id, pos) のリスト(要素数は常に2)を返す．
    def terminals(self, line_id) :
        return self.__terminals_dict[line_id]

    ### @brief 内容を出力する．
    ### @param[in] fout 出力先のファイルオブジェクト(キーワード引数)
    def print(self, *, fout = sys.stdout) :
        fout.write('SIZE {}X{}\n'.format(self.max_width, self.max_height))
        fout.write('BLOCK_NUM {}\n'.format(self.block_num))
        for block in self.block_list :
            print_block(block, fout)
