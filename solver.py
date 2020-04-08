#! /usr/bin/env python3

### @file adc2019enc.py
### @brief ADC2019 の問題をCNF論理式にエンコードするプログラム
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2020 Yusuke Matsunaga
### All rights reserved.


if __name__ == '__main__' :
    import sys
    from core.adc2019parser import Adc2019Parser
    from sat.adc2019enc import solve_adc2019

    if len(sys.argv) != 5 :
        print('USAGE: {} <problem-filename> <width> <height> <sat-program>'.format(sys.argv[0]))
        exit(1)

    ifile = sys.argv[1]

    width = int(sys.argv[2])
    height = int(sys.argv[3])

    satprog = sys.argv[4]

    parser = Adc2019Parser()

    with open(ifile, 'rt') as fin :
        problem = parser.read_problem(fin)
        if not problem :
            print('{}: read failed.'.format(ifile))
            exit(-1)

        ans = solve_adc2019(problem, width, height, satprog)

        if ans is not None :
            ans.print()
