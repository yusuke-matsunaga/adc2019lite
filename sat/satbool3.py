#! /usr/bin/env python3

"""3値のブール値を表すクラス

:file: satbool3.py
:author: Yusuke Matsunaga (松永 裕介)

Copyright (C) 2017 Yusuke Matsunaga
All rights reserved.
"""

from enum import Enum


class SatBool3(Enum):
    """SAT の結果を表す列挙型
    真(B3True)，偽(B3False) の他に不定値を表す B3X
    がある．
    """
    X     =  0
    TRUE  =  1
    FALSE = -1

    def negate(self):
        """否定を返す．"""
        if self == SatBool3.X:
            return SatBool3.X
        if self == SatBool3.TRUE:
            return SatBool3.FALSE
        if self == SatBool3.FALSE:
            return SatBool3.TRUE
        assert False

    def __repr__(self):
        """文字列表現を返す．"""
        if self == SatBool3.X:
            return 'X(unknown)'
        if self == SatBool3.TRUE:
            return 'True'
        if self == SatBool3.FALSE:
            return 'False'
        assert False
