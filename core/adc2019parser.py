#! /usr/bin/env python3

### @file adc2019parser.py
### @brief Adc2019Parser の実装ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2019, 2020 Yusuke Matsunaga
### All rights reserved.

from core.problem import Problem
from core.answer import Answer
from core.position import Position
import re


### @brief ADC2019 の問題ファイルを読み込むためのクラス
class Adc2019Parser :

    ### @brief 初期化
    def __init__(self) :
        # 正規表現のパタンを作る．
        # 'SIZE' 行のパタン
        self.__pSIZE = re.compile('SIZE +([1-9][0-9]*) *X *([1-9][0-9]*)', re.IGNORECASE)
        # 'BLOCK_NUM' 行のパタン
        self.__pBLOCK_NUM = re.compile('BLOCK_NUM +([1-9][0-9]*)', re.IGNORECASE)
        # 'BLOCK' 行のパタン(問題)
        self.__pBLOCK = re.compile('BLOCK#([1-9][0-9]*) +([1-9][0-9]*) *X *([1-9][0-9]*)', re.IGNORECASE)
        # 'BLOCK' 行のパタン(解答)
        self.__pBLOCK2 = re.compile('BLOCK#([1-9][0-9]*) +@\(([0-9]+) *, *([0-9]+)\)', re.IGNORECASE)


    ### @brief 問題ファイルを読み込む
    ### @param[in] fin 読み込み対象のファイルオブジェクト
    ### @return Problem を返す．
    ###
    ### エラーが起きたら None を返す．
    def read_problem(self, fin) :
        self.__in = fin
        self.__nerr = 0
        self.__width = 0
        self.__height = 0
        self.__cur_lineno = 0
        self.__has_SIZE = False
        self.__has_BLOCK_NUM = False

        # 1行ずつ読みこんで処理を行う．
        # EOF の時には readline() が False を返す．
        while self.readline() :

            # SIZE 行の処理
            if self.read_SIZE() :
                continue

            # BLOCK_NUM 行の処理
            if self.read_BLOCK_NUM() :
                continue

            # BLOCK 行の処理
            if self.read_BLOCK() :
                if self.__problem.block_num == self.__block_num :
                    break
                continue

            # それ以外はエラー
            self.error('syntax error')

        # エラーがなければ Problem を返す．
        if self.__nerr == 0 :
            return self.__problem
        else :
            return None


    ### @brief SIZE 行の読み込み
    def read_SIZE(self) :
        # SIZE行のパタンにマッチするか調べる．
        m = self.__pSIZE.match(self.__cur_line)
        if m is None :
            # マッチしなかった
            return False

        if self.__has_SIZE :
            # すでに別のSIZE行があった．
            self.error("Duplicated 'SIZE' line, previously defined at line {}".format(self.SIZE_lineno))
            # 処理はしたので True を返す．
            return True

        width = int(m.group(1))
        height = int(m.group(2))
        self.__problem = Problem(width, height)

        self.__has_SIZE = True
        self.__SIZE_lineno = self.__cur_lineno

        return True


    ### @brief BLOCK_NUM 行の読み込み
    def read_BLOCK_NUM(self) :
        # BLOCK_NUM 行のパタンにマッチするか調べる．
        m = self.__pBLOCK_NUM.match(self.__cur_line)
        if m is None :
            # マッチしなかった
            return False

        if self.__has_BLOCK_NUM :
            # すでに別のBLOCK_NUM行があった．
            self.error("Duplicated 'BLOCK_NUM' line, previously defined at line {}".format(self.BLOCK_NUM_lineno))
            # 処理はしたので True を返す．
            return True

        self.__block_num = int(m.group(1))

        return True


    ### @brief BLOCK行の読み込み
    def read_BLOCK(self) :
        # BLOCK行のパタンにマッチするか調べる．
        m = self.__pBLOCK.match(self.__cur_line)
        if m is None :
            # マッチしなかった
            return False

        block_id = int(m.group(1))
        block_width = int(m.group(2))
        block_height = int(m.group(3))

        pos_list = list()
        label_dict = dict()
        for y in range(block_height) :
            line = self.__in.readline()
            pat_list = line.split(',')
            if len(pat_list) != block_width :
                self.error("# of block patterns mismach.")
                return True

            for x in range(block_width) :
                pat = (pat_list[x].rstrip()).lstrip()
                if pat == '+' :
                    # ラベルなしの値を 0 にすればよかったのに
                    label = 0
                else :
                    label = int(pat)
                    if label == 0 :
                        # こちらは領域外．こっちを0以外の記号にしたらよかった．
                        continue
                pos = Position(x, y)
                pos_list.append(pos)
                label_dict[pos] = label
        self.__problem.add_block(block_id, pos_list, label_dict)

        return True


    ### @brief 解答ファイルを読み込む．
    def read_answer(self, fin, block_num) :
        self.__in = fin
        self.__nerr = 0
        self.__cur_lineno = 0

        if not self.readline() :
            self.error('[A1] syntax error')
            return None

        p = self.read_SIZE2()
        if p is None :
            self.error("[A2] 'SIZE' expected")
            return None

        width, height = p
        answer = Answer(width, height)

        label_array = [ 0 for i in range(width * height) ]
        for y in range(height) :
            stat = self.readline()
            if not stat :
                self.error("[A3] syntax error")
                return None
            pat_list = self.__cur_line.split(',')
            if len(pat_list) != width :
                self.error("[A4] syntax error")
                return None
            for x in range(width) :
                pat = pat_list[x].rstrip().lstrip()
                if pat != '+' :
                    label = int(pat)
                    answer.set_label(Position(x, y), label)

        for block_id in range(1, block_num + 1) :
            act_block_id, pos = self.read_BLOCK2()
            if not pos :
                return None
            if act_block_id != block_id :
                self.error('[A5] wrong BLOCK#, {} expected.'.format(block_id))
                return None
            answer.set_block_pos(block_id, pos)

        return answer


    ### @brief SIZE 行の読み込み(解答ファイル用)
    def read_SIZE2(self) :
        # SIZE行のパタンにマッチするか調べる．
        m = self.__pSIZE.match(self.__cur_line)
        if m is None :
            # マッチしなかった
            return None

        width = int(m.group(1))
        height = int(m.group(2))

        return width, height

    ### @brief BLOCK行の読み込み(解答ファイル用)
    def read_BLOCK2(self) :
        stat = self.readline()
        if not stat :
            self.error('[A6] syntax error')
            return 0, None

        # BLOCK行のパタンにマッチするか調べる．
        m = self.__pBLOCK2.match(self.__cur_line)
        if m is None :
            # マッチしなかった
            self.error('[A7] syntax error')
            return 0, None

        block_id = int(m.group(1))
        x = int(m.group(2))
        y = int(m.group(3))
        return block_id, Position(x, y)

    ### @brief 1行読み込む．
    ### @retval True 正しく読み込めた
    ### @retval False EOF に達した．
    def readline(self) :
        while True :
            line = self.__in.readline()
            self.__cur_lineno += 1
            if line == '' :
                # EOF
                return False

            line = line.rstrip()
            if line != '' :
                self.__cur_line = line
                return True

    ### @brief エラー処理
    def error(self, msg) :
        print('Error at line {}: {}'.format(self.__cur_lineno, msg))
        print('     {}'.format(self.__cur_line))
        self.__nerr += 1


# テストプログラム
# 標準入力から読み込んで標準出力に出力する．
if __name__ == "__main__" :
    import sys

    parser = Adc2019Parser()

    problem = parser.read_problem(sys.stdin)

    if problem :
        problem.print()
