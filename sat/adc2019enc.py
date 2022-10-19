#! /usr/bin/env python3

"""ADC2019 の問題をCNF論理式にエンコードするプログラム
:file: adc2019enc.py
:author: Yusuke Matsunaga (松永 裕介)

Copyright (C) 2020 Yusuke Matsunaga
All rights reserved.
"""

from core.answer import Answer
from core.position import Position
from sat.satbool3 import SatBool3
from sat.satsolver import SatSolver


class Adc2019Enc:
    """ADC2019 の問題をCNF論理式にエンコードするクラス
    :param Solver solver: SATソルバ
    :param Problem problem: 問題
    :param int width: 幅
    :param int height: 高さ
    """
    def __init__(self, solver, problem, width, height):
        self.__solver = solver
        self.__problem = problem
        self.__width = width
        self.__height = height
        self.__gridpos_list = list()
        for y in range(self.__height):
            for x in range(self.__width):
                self.__gridpos_list.append(Position(x, y))
        self.__x_var_dict = dict()
        self.__y_var_dict = dict()
        self.__g_var_dict = dict()
        self.__b_var_dict = dict()
        self.__l_var_dict = dict()
        self.__t_var_dict = dict()
        self.__e_var_dict = dict()

    def gen_placement_constraint(self):
        """配置制約を作る．
        """
        # 各ブロックの左上の座標を表す変数を作る．
        # ここでは One-Hot 符号化を用いる．
        # 各ブロックに付き width 個と height 個の変数を用意する．
        # 作った変数はブロック番号とx/y座標のペアをキーにした
        # 辞書で管理する．
        for block in self.__problem.block_list:
            # block のX座標を表す変数を作る．
            var_list = []
            for x in range(self.__width):
                var = self.__solver.new_variable()
                key = block.block_id, x
                self.__x_var_dict[key] = var
                if x + block.width >= self.__width:
                    # 右端からはみ出るので置けない．
                    self.__solver.add_clause(-var)
                else:
                    var_list.append(var)
            self.__gen_one_hot_constraint(var_list)

            # block のY座標を表す変数を作る．
            var_list = []
            for y in range(self.__height):
                var = self.__solver.new_variable()
                key = block.block_id, y
                self.__y_var_dict[key] = var
                if y + block.height >= self.__height:
                    # 下端からはみ出るので置けない．
                    self.__solver.add_clause(-var)
                else:
                    var_list.append(var)
            self.__gen_one_hot_constraint(var_list)

        # 盤面の各グリッドがどのブロックに使用されているか
        # を表す変数．
        # 各グリッド毎に nblock 個の変数を用意する．
        # こちらは At-Most-One 符号化を用いる．
        for pos in self.__gridpos_list:
            var_list = []
            # このグリッドがいずれかのブロックで使われている時に
            # True となる変数を作る．
            b_var = self.__solver.new_variable()
            self.__b_var_dict[pos] = b_var
            for block in self.__problem.block_list:
                # このグリッドが block で使われている時に
                # True となる変数
                var = self.__solver.new_variable()
                key = pos, block.block_id
                self.__g_var_dict[key] = var
                # var1_list = list()
                for pos1 in block.pos_list:
                    pos2 = pos - pos1
                    if pos2.is_in_range(self.__width, self.__height):
                        x_var = self.__block_x_var(block.block_id, pos2.x)
                        y_var = self.__block_y_var(block.block_id, pos2.y)
                        self.__solver.add_clause(-x_var, -y_var, var)
                        self.__solver.add_clause(-x_var, -y_var, b_var)
                        # var1 = self.__solver.new_variable()
                        # self.__solver.add_clause(-x_var, -y_var,  var1)
                        # self.__solver.add_clause( x_var,         -var1)
                        # self.__solver.add_clause(         y_var, -var1)
                        # var1_list.append(var1)
                        # self.__solver.add_clause(-var1, var)
                # self.__solver.add_clause(-var, var1_list)
                var_list.append(var)
                # self.__solver.add_clause(-var, b_var)
            self.__gen_at_most_one_constraint(var_list)
            # 実は add_clause は変数とリストの混在もかける．
            self.__solver.add_clause(-b_var, var_list)

        # ブロック位置の変数と盤面のラベルの変数の間の関係
        # を表す制約を作る．
        for pos in self.__gridpos_list:
            for block in self.__problem.block_list:
                # pos のグリッドを block が占めている時の条件を作る．
                for pos1 in block.pos_list:
                    pos0 = pos - pos1
                    if pos0.is_in_range(self.__width, self.__height):
                        # block が pos0 に置かれた時に pos1 の位置がちょうど pos になる．
                        # ので pos のラベルを block_id にする．
                        x_var = self.__block_x_var(block.block_id, pos0.x)
                        y_var = self.__block_y_var(block.block_id, pos0.y)
                        g_var = self.__grid_var(pos, block.block_id)
                        self.__solver.add_clause(-x_var, -y_var, g_var)

    def gen_routing_constraint(self):
        """配線制約を作る．"""
        # 盤面上の線分ラベルを表す変数を作る．
        # 一つのグリッドに対して線分数の数だけ用意する．
        for pos in self.__gridpos_list:
            var_list = []
            for line_id in self.__problem.line_id_list:
                var = self.__solver.new_variable()
                key = pos, line_id
                self.__l_var_dict[key] = var
                var_list.append(var)
            # 一つのグリッド上では高々1つの線分しか選ばれない．
            # 一つも選ばれない場合もあるので one-hot ではない．
            self.__gen_at_most_one_constraint(var_list)

            # このグリッドがブロックに覆われている(線分として使えない)時に
            # True となる変数．
            b_var = self.__b_var_dict[pos]

            # pos にいずれかの端子が置かれる時に True になる変数．
            t_all_var = self.__solver.new_variable()
            self.__t_var_dict[pos] = t_all_var
            t_var_list = []
            for line_id in self.__problem.line_id_list:
                # pos に line_id の端子が置かれる時に True になる変数
                t1_var = self.__solver.new_variable()
                key = pos, line_id
                xyvar_list = []
                for block_id, pos1 in self.__problem.terminals(line_id):
                    pos0 = pos - pos1
                    if pos0.is_in_range(self.__width, self.__height):
                        # block_id のブロックが pos0 に置かれた時に
                        # pos のグリッドが line_id の線分の端子となる．
                        x_var = self.__block_x_var(block_id, pos0.x)
                        y_var = self.__block_y_var(block_id, pos0.y)
                        xyvar_list.append((x_var, y_var))

                n = len(xyvar_list)
                if n == 0:
                    self.__solver.add_clause(-t1_var)
                elif n == 1:
                    x_var, y_var = xyvar_list[0]
                    self.__solver.add_clause(-x_var, -y_var,  t1_var)
                    self.__solver.add_clause( x_var,         -t1_var)
                    self.__solver.add_clause(         y_var, -t1_var)
                elif n == 2:
                    var_list = []
                    for x_var, y_var in xyvar_list:
                        var = self.__solver.new_variable()
                        self.__solver.add_clause(-x_var, -y_var,  var)
                        self.__solver.add_clause( x_var,         -var)
                        self.__solver.add_clause(         y_var, -var)
                        var_list.append(var)
                    var1, var2 = var_list
                    self.__solver.add_clause(-var1,         t1_var)
                    self.__solver.add_clause(       -var2,  t1_var)
                    self.__solver.add_clause( var1,  var2, -t1_var)

                # t1_var が True の時には線分番号 line_id のラベルがつく．
                l_var = self.__line_var(pos, line_id)
                self.__solver.add_clause(-t1_var, l_var)

                # t1_var が True の時には pos に端子が置かれる．
                self.__solver.add_clause(-t1_var, t_all_var)
                t_var_list.append(t1_var)
            # t_var が True の時，t_var_list の中の1つは必ず True となる．
            self.__solver.add_clause(-t_all_var, t_var_list)

            # t_all_var が False で b_var が True の場合線分ラベルは 0 となる．
            for line_id in self.__problem.line_id_list:
                l_var = self.__line_var(pos, line_id)
                self.__solver.add_clause(t_all_var, -b_var, -l_var)

        # グリッド間の枝を表す変数を作る．
        self.__e_var_dict = {}

        # 縦方向の枝
        for x in range(self.__width):
            for y in range(self.__height - 1):
                var = self.__solver.new_variable()

                # (x, y) から s 方向の枝という意味
                key = Position(x, y), 's'
                self.__e_var_dict[key] = var

                # (x, y + 1) から n 方向の枝という意味
                key = Position(x, y + 1), 'n'
                self.__e_var_dict[key] = var

        # 横方向の枝
        for y in range(self.__height):
            for x in range(self.__width - 1):
                var = self.__solver.new_variable()

                # (x, y) から e 方向の枝という意味
                key = Position(x, y), 'e'
                self.__e_var_dict[key] = var

                # (x + 1, y) から w 方向の枝という意味
                key = Position(x + 1, y), 'w'
                self.__e_var_dict[key] = var

        # 各グリッドに接続する枝に関する制約を作る．
        for pos in self.__gridpos_list:
            var_list = list()
            for dir in ('n', 'e', 's', 'w'):
                key = pos, dir
                if key not in self.__e_var_dict:
                    continue

                var = self.__e_var_dict[key]
                var_list.append(var)

            t_var = self.__t_var_dict[pos]
            b_var = self.__b_var_dict[pos]

            # pos が線分の端子の場合
            # 1個の変数が選ばれる．
            self.__gen_one_hot_constraints_with_cond(var_list, t_var)

            # pos が端子以外のブロックの場合，
            # 変数は選ばれない．
            for var in var_list:
                self.__solver.add_clause(-b_var, t_var, -var)

            # pos がそれ以外の場合
            # 0 個か 2 個の変数が選ばれる．
            self.__gen_zero_or_two_hot_constraints_with_cond(var_list, -b_var)

        # 枝が選択されている時にその両端のグリッドの線分番号が等しくなるという制約
        for pos1 in self.__gridpos_list:
            for dir in ('n', 'e', 's', 'w'):
                key = pos1, dir
                if key not in self.__e_var_dict:
                    continue

                e_var = self.__e_var_dict[key]
                pos2 = pos1.adjacent_pos(dir)
                for line_id in self.__problem.line_id_list:
                    l1_var = self.__line_var(pos1, line_id)
                    l2_var = self.__line_var(pos2, line_id)
                    self.__solver.add_clause(-e_var,  l1_var, -l2_var)
                    self.__solver.add_clause(-e_var, -l1_var,  l2_var)

        # コの字制約を作る．
        for pos in self.__gridpos_list:
            key1 = pos, 's'
            if key1 not in self.__e_var_dict:
                continue
            e1_var = self.__e_var_dict[key1]

            key2 = pos, 'e'
            if key2 not in self.__e_var_dict:
                continue
            e2_var = self.__e_var_dict[key2]

            pos2 = pos + Position(0, 1)
            key3 = pos2, 'e'
            e3_var = self.__e_var_dict[key3]

            pos3 = pos + Position(1, 0)
            key4 = pos3, 's'
            e4_var = self.__e_var_dict[key4]

            # e1, e2, e3, e4 のうち3つ以上同時に true にならない．
            self.__solver.add_clause(-e1_var, -e2_var, -e3_var         )
            self.__solver.add_clause(-e1_var, -e2_var,          -e4_var)
            self.__solver.add_clause(-e1_var,          -e3_var, -e4_var)
            self.__solver.add_clause(         -e2_var, -e3_var, -e4_var)

    def get_answer(self, model):
        """解を作る．
        :param Model model: SAT問題の解
        """

        ans = Answer(self.__width, self.__height)

        # ブロック位置を得る．
        for block_id in self.__problem.block_id_list:
            for x in range(self.__width):
                var = self.__block_x_var(block_id, x)
                if model[var] == SatBool3.TRUE:
                    break
            else:
                assert False

            for y in range(self.__height):
                var = self.__block_y_var(block_id, y)
                if model[var] == SatBool3.TRUE:
                    break
            else:
                assert False

            ans.set_block_pos(block_id, Position(x, y))

        # 線分ラベルを得る．
        # 基本的には self.__l_var_dict に入っている線分番号用の
        # 変数の値を読めばよいが，SAT問題の都合上，線分でない
        # 部分にも非0の値がつくことがあるので端子間を結ぶ
        # 線分を取り出す．
        for line_id in self.__problem.line_id_list:
            t1, t2 = self.__problem.terminals(line_id)
            (block_id1, pos1) = t1
            (block_id2, pos2) = t2
            gpos1 = ans.block_pos(block_id1) + pos1
            gpos2 = ans.block_pos(block_id2) + pos2
            route = self.__get_route(model, gpos1, gpos2, line_id)
            for pos in route:
                key = pos, line_id
                var = self.__l_var_dict[key]
                assert model[var] == SatBool3.TRUE
                ans.set_label(pos, line_id)

        return ans

    def __get_route(self, model, pos1, pos2, line_id):
        """経路を求める．"""
        key1 = pos1, line_id
        var1 = self.__l_var_dict[key1]
        assert model[var1] == SatBool3.TRUE

        key2 = pos2, line_id
        var2 = self.__l_var_dict[key2]
        assert model[var2] == SatBool3.TRUE

        pos = pos1
        route = []
        prev_pos = None
        while True:
            route.append(pos)
            if pos == pos2:
                break
            for dir in ('n', 'e', 's', 'w'):
                key = pos, dir
                if key not in self.__e_var_dict:
                    continue
                e_var = self.__e_var_dict[key]
                if model[e_var] == SatBool3.TRUE:
                    next_pos = pos.adjacent_pos(dir)
                    if prev_pos is not None and next_pos == prev_pos:
                        continue
                    break
            else:
                assert False
            prev_pos = pos
            pos = next_pos

        return route

    def __gen_at_most_one_constraint(self, var_list):
        """At-Most-One 制約を作る．
        :param list[int] var_list: 対象の変数のリスト
        """
        # 単純に O(n^2) の節を作っている．
        nv = len(var_list)
        for i1 in range(0, nv - 1):
            v1 = var_list[i1]
            for i2 in range(i1 + 1, nv):
                v2 = var_list[i2]
                self.__solver.add_clause(-v1, -v2)

    def __gen_one_hot_constraint(self, var_list):
        """One-Hot 制約を作る．
        :param list[int] 対象の変数のリスト
        """

        # 2つの変数が同時に True にならないという制約
        self.__gen_at_most_one_constraint(var_list)

        # 最低1つの変数が True になるという制約
        self.__solver.add_clause(var_list)

    def __gen_one_hot_constraints_with_cond(self, var_list, cond):
        """条件付きの One-Hot 制約を作る．
        :param list[int] var_list: 対象の変数のリスト
        :param int cond: 条件となるリテラル
        """
        # 単純に O(n^2) の節を作っている．
        nv = len(var_list)
        for i1 in range(0, nv - 1):
            v1 = var_list[i1]
            for i2 in range(i1 + 1, nv):
                v2 = var_list[i2]
                self.__solver.add_clause(-cond, -v1, -v2)
        self.__solver.add_clause(-cond, var_list)

    def __gen_zero_or_two_hot_constraints_with_cond(self, var_list, cond):
        """条件付きの 0 or 2 Hot 制約を作る．
        :param list[int] var_list: 対象の変数のリスト
        :param int cond: 条件となるリテラル
        """
        # たかだか4つなので全てのパタンを列挙する．
        # 対称性があるのでわかりやすい．
        nv = len(var_list)
        if nv < 2:
            assert False
        elif nv == 2:
            # どちらか一方だけ True のパタンを禁止する．
            v1, v2 = var_list
            self.__solver.add_clause(-cond, -v1,  v2)
            self.__solver.add_clause(-cond,  v1, -v2)
        elif nv == 3:
            v1, v2, v3 = var_list
            # 一つの変数のみ True となるパタンを禁止する．
            self.__solver.add_clause(-cond, -v1,  v2,  v3)
            self.__solver.add_clause(-cond,  v1, -v2,  v3)
            self.__solver.add_clause(-cond,  v1,  v2, -v3)
            # 3つの変数が True となるパタンを禁止する．
            self.__solver.add_clause(-cond, -v1, -v2, -v3)
        elif nv == 4:
            v1, v2, v3, v4 = var_list
            # 一つの変数のみ True となるパタンを禁止する．
            self.__solver.add_clause(-cond, -v1,  v2,  v3,  v4)
            self.__solver.add_clause(-cond,  v1, -v2,  v3,  v4)
            self.__solver.add_clause(-cond,  v1,  v2, -v3,  v4)
            self.__solver.add_clause(-cond,  v1,  v2,  v3, -v4)
            # 3つ以上の変数が True となるパタンを禁止する．
            self.__solver.add_clause(-cond, -v1, -v2, -v3     )
            self.__solver.add_clause(-cond, -v1, -v2,      -v4)
            self.__solver.add_clause(-cond, -v1,      -v3, -v4)
            self.__solver.add_clause(-cond,      -v2, -v3, -v4)
        else:
            assert False

    def __block_x_var(self, block_id, x):
        """ブロックのX座標を表す変数を返す．
        :param int block_id: ブロック番号
        :param int x: X座標
        :return: 対象の変数(SatLiteral)を返す．
        この変数が True の時，このブロックのX座標はxとなっている．
        """
        key = block_id, x
        return self.__x_var_dict[key]

    def __block_y_var(self, block_id, y):
        """ブロックのY座標を表す変数を返す．
        :param int block_id: ブロック番号
        :param int y: Y座標
        :return: 対象の変数(SatLiteral)を返す．
        この変数が True の時，このブロックのY座標はyとなっている．
        """
        key = block_id, y
        return self.__y_var_dict[key]

    def __grid_var(self, pos, block_id):
        """グリッドのブロック番号を表す変数を返す．
        :param Position pos: グリッドの位置
        :param int block_id: ブロック番号
        :return: 対象の変数(SatLiteral)を返す．
        この変数が True の時，このグリッドは block_id のブロックに使用されている．
        """
        key = pos, block_id
        return self.__g_var_dict[key]

    def __line_var(self, pos, line_id):
        """グリッドの線分番号を表す変数を返す．
        :param Position pos: グリッドの位置
        :param int line_id: 線分番号
        :return: 対象の変数(SatLiteral)を返す．
        この変数が True の時，このグリッドは line_id の線分に使用されている．
        """
        key = pos, line_id
        return self.__l_var_dict[key]


def solve_adc2019(problem, width, height, satprog):
    """ADC2019 問題を解く
    :param Problem problem: 問題
    :param int width: 幅
    :param int height: 高さ
    problem の幅と高さではなく
    与えられた幅と高さの盤面で
    答を求める．
    """

    solver = SatSolver(satprog)

    enc = Adc2019Enc(solver, problem, width, height)

    # 配置制約を作る．
    enc.gen_placement_constraint()

    # 配線制約を作る．
    enc.gen_routing_constraint()

    # SAT問題を解く
    stat, model = solver.solve()

    if stat == SatBool3.TRUE:
        # 答を作る．
        ans = enc.get_answer(model)
        return ans
    else:
        print('UNSAT')
        return None
