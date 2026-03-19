# -*- coding: utf-8 -*-
# Author: Cailea
# Date: 2024-06-20
# Description: 包含了用于替换 run.hk 和 run.sh 中参数的函数，以及一个示例函数 run_example 来展示如何使用这些替换函数来设置参数并执行 run.sh 脚本。

# Functions:
# - Indexs2blocking: 根据给定的能级索引和费米面附近的能级列表，生成对应的阻塞参数字典。
# - replace_blocking_levels: 替换 run.hk 中对应块(1,2,3)的阻塞参数。
# - replace_hk_startB4: 替换 run.hk 中 start_B4 参数值。
# - replace_hk_params: 替换 run.hk 中 $DEFFI 行及其下一行的参数行。
# - replace_sh_command: 替换 run.sh 中 run.hk 与 run.mp 行，直接覆盖为 {cmd} $Z $Z $N $N KEY_NAME{count}。
# - replace_sh_NZ: 替换 run.sh 中 "Z=" 与 "N=" 开头的行，直接覆盖为 "Z={Z}" 与 "N={N}"。


import os
import re
import time
from pathlib import Path
from level_select import Select_FermiThreeLevelList


KEY_SH_COMMANDS = ["run.hk", "run.mp"]


blocking_levels = {
    "n1_PP=":0,
    "n1_NP=":0,
    "n2_PP=":0,
    "n2_NP=":0,
    "p1_PP=":0,
    "p1_NP=":0,
    "p2_PP=":0,
    "p2_NP=":0,
}


def Indexs2blocking(n1Index, n2Index, p1Index, p2Index, n_ThreeFermiList, p_ThreeFermiList):
    blocking1 = blocking_levels.copy()
    blocking2 = blocking_levels.copy()
    blocking3 = blocking_levels.copy()
    if n1Index != 0:
        for n1 in range(len(n_ThreeFermiList)):
            if n_ThreeFermiList[n1].level1.index == n1Index: break
        if n_ThreeFermiList[n1].level1.index != n1Index: raise IndexError("n1Index")
        n1_parity = n_ThreeFermiList[n1].level1.parity
        if n1_parity == "+":
            blocking1["n1_PP="] = n_ThreeFermiList[n1].level1.Idx
            blocking2["n1_PP="] = n_ThreeFermiList[n1].level2.Idx
            blocking3["n1_PP="] = n_ThreeFermiList[n1].level3.Idx
        else:
            blocking1["n1_NP="] = n_ThreeFermiList[n1].level1.Idx
            blocking2["n1_NP="] = n_ThreeFermiList[n1].level2.Idx
            blocking3["n1_NP="] = n_ThreeFermiList[n1].level3.Idx
    if n2Index != 0:
        for n2 in range(len(n_ThreeFermiList)):
            if n_ThreeFermiList[n2].level1.index == n2Index: break
        if n_ThreeFermiList[n2].level1.index != n2Index: raise IndexError("n2Index")
        n2_parity = n_ThreeFermiList[n2].level1.parity
        if n2_parity == "+":
            blocking1["n2_PP="] = n_ThreeFermiList[n2].level1.Idx
            blocking2["n2_PP="] = n_ThreeFermiList[n2].level2.Idx
            blocking3["n2_PP="] = n_ThreeFermiList[n2].level3.Idx
        else:
            blocking1["n2_NP="] = n_ThreeFermiList[n2].level1.Idx
            blocking2["n2_NP="] = n_ThreeFermiList[n2].level2.Idx
            blocking3["n2_NP="] = n_ThreeFermiList[n2].level3.Idx
    if p1Index != 0:
        for p1 in range(len(p_ThreeFermiList)):
            if p_ThreeFermiList[p1].level1.index == p1Index: break
        if p_ThreeFermiList[p1].level1.index != p1Index: raise IndexError("p1Index")
        p1_parity = p_ThreeFermiList[p1].level1.parity
        if p1_parity == "+":
            blocking1["p1_PP="] = p_ThreeFermiList[p1].level1.Idx
            blocking2["p1_PP="] = p_ThreeFermiList[p1].level2.Idx
            blocking3["p1_PP="] = p_ThreeFermiList[p1].level3.Idx
        else:
            blocking1["p1_NP="] = p_ThreeFermiList[p1].level1.Idx
            blocking2["p1_NP="] = p_ThreeFermiList[p1].level2.Idx
            blocking3["p1_NP="] = p_ThreeFermiList[p1].level3.Idx
    if p2Index != 0:
        for p2 in range(len(p_ThreeFermiList)):
            if p_ThreeFermiList[p2].level1.index == p2Index: break
        if p_ThreeFermiList[p2].level1.index != p2Index: raise IndexError("p2Index")
        p2_parity = p_ThreeFermiList[p2].level1.parity
        if p2_parity == "+":
            blocking1["p2_PP="] = p_ThreeFermiList[p2].level1.Idx
            blocking2["p2_PP="] = p_ThreeFermiList[p2].level2.Idx
            blocking3["p2_PP="] = p_ThreeFermiList[p2].level3.Idx
        else:
            blocking1["p2_NP="] = p_ThreeFermiList[p2].level1.Idx
            blocking2["p2_NP="] = p_ThreeFermiList[p2].level2.Idx
            blocking3["p2_NP="] = p_ThreeFermiList[p2].level3.Idx
    return blocking1, blocking2, blocking3


def replace_blocking_levels(blocking, index, hk_file_path):
    """替换run.hk中对应块(1,2,3)的阻塞参数
    """
    blocking_count = {key: 0 for key in blocking}
    with open(hk_file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        for key in blocking.keys():
            if line.strip().startswith(key):
                blocking_count[key] += 1
                if blocking_count[key] == index:
                    lines[i] = key + str(blocking[key]) + '\n'
                break

    with open(hk_file_path, 'w') as file:
        file.writelines(lines)

def replace_hk_startB4(start_B4, hk_file_path):
    """替换run.hk中start_B4=其他的参数值"""
    # start_B4=-0.053
    with open(hk_file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("start_B4="):
            lines[i] = f"start_B4={start_B4}\n"
            break

    with open(hk_file_path, 'w') as file:
        file.writelines(lines)


def replace_hk_params(line1, line2, hk_file_path):
    """替换run.hk中$DEFFI行及其下一行的参数行"""
    # line1 = " \$DEFFI NB2=8, NGA=8, BET20=0.13,GAM0=0.075, NAZWIT=4,"
    # line2 = "        DB2=0.02, DGA=0.02, NNNSTP=2, NNPSTP=2,"
    with open(hk_file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if "DEFFI" in line:
            lines[i] = line1 + "\n"
            lines[i + 1] = line2 + "\n"
            break

    with open(hk_file_path, 'w') as file:
        file.writelines(lines)


def replace_sh_command(KEY_NAME, count, sh_file_path):
    """替换run.sh中run.hk与run.mp行，直接覆盖为 {cmd} $Z $Z $N $N KEY_NAME{count}
    """
    with open(sh_file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        for cmd in KEY_SH_COMMANDS:
            if line.strip().startswith(cmd):
                lines[i] = f"{cmd} $Z $Z $N $N {KEY_NAME}{count}\n"
                break
    
    with open(sh_file_path, 'w') as file:
        file.writelines(lines)

def replace_sh_NZ(Z, N, sh_file_path):
    """替换 run.sh 中 "Z=" 与 "N=" 开头的行，直接覆盖为 "Z={Z}" 与 "N={N}"
    """
    with open(sh_file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("Z="):
            lines[i] = f"Z={Z}\n"
        elif line.strip().startswith("N="):
            lines[i] = f"N={N}\n"

    with open(sh_file_path, 'w') as file:
        file.writelines(lines)


if __name__ == "__main__":
    ROOT_DIR = Path(__file__).parent
    sh_file_path = str(ROOT_DIR / "run.sh")
    hk_file_path = str(ROOT_DIR / "run.hk")
    log_file_path = str(ROOT_DIR / "run.log")

    KEY_NAME = "Ds269-HKpr1n2p"
    proton_num = 110
    neutron_num = 159
    level_range = 8
    out_file_path = "hk.out"


    # 参数设置
    start_B4=-0.053
    line1 = r" \$DEFFI NB2=10, NGA=10, BET20=0.13,GAM0=0.075, NAZWIT=4,"
    line2 = r"        DB2=0.02, DGA=0.02, NNNSTP=2, NNPSTP=2,"
    replace_hk_startB4(start_B4, hk_file_path)
    replace_hk_params(line1, line2, hk_file_path)
    replace_sh_NZ(proton_num, neutron_num, sh_file_path)


    # 获取费米面附近的三个单粒子态列表
    n_ThreeFermiList, p_ThreeFermiList = Select_FermiThreeLevelList(proton_num, neutron_num, out_file_path, level_range)

    # 运行示例
    example_list = [
       # n1, n2, p1, p2
        (0 ,  0,  0,  0),
        (0 , 73, 55, 56),
        (0 , 73, 55, 57),
        (0 , 73, 55, 58),
    ]

    countBegin = 14
    for i, (n1Index, n2Index, p1Index, p2Index) in enumerate(example_list):
        count = countBegin + i
        print(f"正在运行示例 {count}，参数索引: Index(n1)={n1Index}, Index(n2)={n2Index}, Index(p1)={p1Index}, Index(p2)={p2Index}")
        blocking1, blocking2, blocking3 = Indexs2blocking(n1Index, n2Index, p1Index, p2Index, n_ThreeFermiList, p_ThreeFermiList)
        replace_blocking_levels(blocking1, 1, hk_file_path)
        replace_blocking_levels(blocking2, 2, hk_file_path)
        replace_blocking_levels(blocking3, 3, hk_file_path)
        replace_sh_command(KEY_NAME, count, sh_file_path)
        time.sleep(10)
