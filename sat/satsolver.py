#! /usr/bin/env python3

"""SAT ソルバ用のインターフェイスクラス
:file: satsolver.py
:author: Yusuke Matsunaga (松永 裕介)

Copyright (C) 2017 Yusuke Matsunaga
All rights reserved.
"""


from enum import Enum
import tempfile
import os
import subprocess

from sat.satbool3 import SatBool3


class SatSolver:
    """SAT ソルバを表すクラス
    このクラスは内部でSATソルバのプログラムを呼び出している．
    同じインターフェイスで内部で SAT を解くクラスを(主にC++で)
    実装しても良い．
    """

    def __init__(self, satprog):
        """初期化
        :param str satprog: SATソルバのプログラム名
        """
        self._var_count = 0
        self._clause_list = []
        self._satprog = satprog
        # デバッグフラグ
        self._debug = False

    def new_variable(self):
        """変数を作る．
        :return: 変数番号を返す．
        """
        self._var_count += 1
        return self._var_count

    def add_clause(self, *args):
        """節を追加する．
        :param list[int] args: 節のリテラルのリスト
        リテラルは 0 以外の整数で，絶対値が番号を
        符号が極性を表す．
        たとえば 3 なら 3番目の変数の肯定
        -1 なら 1番目の変数の否定を表す．
        """
        tmp_list = []
        for arg in args:
            if isinstance(arg, int):
                # singleton の場合
                lit = arg
                if self._check_lit(lit):
                    tmp_list.append(lit)
            else:
                # リストの場合
                for lit in arg:
                    if not self._check_lit(lit):
                        return
                    tmp_list.append(lit)
        self._clause_list.append(tmp_list)

    def solve(self, assumption_list=[]):
        """SAT問題を解く．
        :param list[int] assumption_list: 仮定する割り当てリスト
        :return: (result, model) を返す．
        - result は SatBool3
        - model は結果の各変数に対する値を格納したリスト
        変数番号が 1番の変数の値は model[1] に入っている．
        値は SatBool3
        """

        # デフォルトの返り値
        result = SatBool3.X
        model = []

        # dimacs 形式のファイルを作る．
        # fh は使わない．
        (fh, dimacs_file) = tempfile.mkstemp()
        fout = open(dimacs_file, 'w')
        if not fout:
            msg = 'Error: could not create {} for DIMACS input.'
            print(msg.format(dimacs_file))
            return

        # ヘッダを書き出す．
        var_num = self._var_count
        clause_num = len(self._clause_list)
        fout.write(f'p cnf {var_num} {clause_num}\n')

        # 節の内容を書き出す．
        for lit_list in self._clause_list:
            for lit in lit_list:
                fout.write(f' {lit}')
            fout.write(' 0\n')

        # assumption を単一リテラル節の形で書き出す．
        for lit in assumption_list:
            fout.write(f' {lit} 0\n')
        fout.close()

        # SATソルバを起動する．
        (fh, output_file) = tempfile.mkstemp()
        command_line = [self._satprog, dimacs_file, output_file]
        if self._debug:
            print(f'SAT program: {self._satprog}')
            print(f'INPUT:       {dimacs_file}')
            print(f'OUTPUT:      {output_file}')
            dout = None
            derr = None
        else:
            dout = subprocess.DEVNULL
            derr = subprocess.DEVNULL
        subprocess.run(command_line, stdout=dout, stderr=derr)
        if not self._debug:
            os.remove(dimacs_file)

        # 結果のファイルを読み込む．
        with open(output_file, 'r') as fin:
            lines = fin.readlines()

            # 1行目が結果
            if lines[0] == 'SAT\n':
                assert len(lines) == 2
                result = SatBool3.TRUE
                # 割り当て結果を model に反映させる．
                val_list = lines[1].split()
                model = [SatBool3.X for i in range(var_num + 1)]
                for val_str in val_list:
                    val = int(val_str)
                    if val > 0:
                        model[val] = SatBool3.TRUE
                    elif val < 0:
                        model[-val] = SatBool3.FALSE
            elif lines[0] == 'UNSAT\n':
                result = SatBool3.FALSE
        if not self._debug:
            os.remove(output_file)

        return result, model

    def _check_lit(self, lit):
        """リテラルが適正な値かチェックする．"""
        if lit > 0:
            varid = lit
        elif lit < 0:
            varid = -lit
        else:
            msg = 'Error in add_clause(), 0 is not allowed as a literal value.'
            print(msg)
            return False
        if varid > self._var_count:
            print('Error in add_clause(), {} is out of range'.format(lit))
            return False
        return True
