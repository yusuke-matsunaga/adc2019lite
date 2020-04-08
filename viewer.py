#! /usr/bin/env python3

### @file viewer.py
### @brief ADC2019の問題と解答を表示するプログラム
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2017 Yusuke Matsunaga
### All rights reserved.

import sys
import os
import argparse

from core.adc2019parser import Adc2019Parser
from gui.problemviewwidget import ProblemViewWidget
from gui.answerviewwidget import AnswerViewWidget
from PyQt5.QtWidgets import *


# コマンドラインパーサーの作成
parser = argparse.ArgumentParser()
parser.add_argument('-a', '--answer', type = str,
                    help = 'specify the answer filename')
parser.add_argument('input', type = str,
                    help = 'problem filename')

# コマンド行の解析
args = parser.parse_args()
if not args :
    exit(-1)

# 入力ファイル名
ifile = args.input
# 出力ファイル名 or None
ofile = args.answer

parser = Adc2019Parser()
problem = None
answer = None
with open(ifile, 'rt') as fin :
    problem = parser.read_problem(fin)
    if not problem :
        print('{}: read failed.'.format(ifile))
        exit(-1)

    if ofile :
        with open(ofile, 'rt') as fin2 :
            answer = parser.read_answer(fin2, problem.block_num)
            if not answer :
                print('{}: read failed.'.format(ofile))
                exit(-1)

app = QApplication(sys.argv)

if answer :
    aview = AnswerViewWidget()
    aview.set_answer(problem, answer)
    aview.show()
else :
    pview = ProblemViewWidget()
    pview.set_problem(problem)
    pview.show()

app.exec_()
