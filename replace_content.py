import os
import re
import time
from pathlib import Path
from level_select import n_GetFermiThreeLevelList, p_GetFermiThreeLevelList

KEY_BLOCKING_LEVELS = ["if [ $ind -eq 1 ]; then", 
             "elif [ $ind -eq 2 ]; then", 
             "elif [ $ind -eq 3 ]; then"]


KEY_SH_COMMANDS = ["run.hk", "run.mp"]


blocking_levels = {
    "n1_PP=":1,
    "n1_NP=":2,
    "p1_PP=":3,
    "p1_NP=":4,
    "p2_PP=":5,
    "p2_NP=":6,
}


def Indexs2blocking(n1Index, p1Index, p2Index, n_ThreeFermiList, p_ThreeFermiList):
    n1 = p1 = p2 = 0
    for n_ThreeLevel in n_ThreeFermiList:
        if n_ThreeLevel.level1.index == n1Index:
            n1 = n_ThreeLevel.index
            break
    for p_ThreeLevel in p_ThreeFermiList:
        if p_ThreeLevel.level1.index == p1Index:
            p1 = p_ThreeLevel.index
            break
    for p_ThreeLevel in p_ThreeFermiList:
        if p_ThreeLevel.level1.index == p2Index:
            p2 = p_ThreeLevel.index
            break
    blocking1 = blocking_levels.copy()
    blocking2 = blocking_levels.copy()
    blocking3 = blocking_levels.copy()
    n1_parity = n_ThreeFermiList[n1].level1.parity
    p1_parity = p_ThreeFermiList[p1].level1.parity
    p2_parity = p_ThreeFermiList[p2].level1.parity
    if n1_parity == "+":
        blocking1["n1_PP="] = n_ThreeFermiList[n1].level1.parity_index
        blocking2["n1_PP="] = n_ThreeFermiList[n1].level2.parity_index
        blocking3["n1_PP="] = n_ThreeFermiList[n1].level3.parity_index
    else:
        blocking1["n1_NP="] = n_ThreeFermiList[n1].level1.parity_index
        blocking2["n1_NP="] = n_ThreeFermiList[n1].level2.parity_index
        blocking3["n1_NP="] = n_ThreeFermiList[n1].level3.parity_index
    if p1_parity == "+":
        blocking1["p1_PP="] = p_ThreeFermiList[p1].level1.parity_index
        blocking2["p1_PP="] = p_ThreeFermiList[p1].level2.parity_index
        blocking3["p1_PP="] = p_ThreeFermiList[p1].level3.parity_index
    else:
        blocking1["p1_NP="] = p_ThreeFermiList[p1].level1.parity_index
        blocking2["p1_NP="] = p_ThreeFermiList[p1].level2.parity_index
        blocking3["p1_NP="] = p_ThreeFermiList[p1].level3.parity_index
    if p2_parity == "+":
        blocking1["p2_PP="] = p_ThreeFermiList[p2].level1.parity_index
        blocking2["p2_PP="] = p_ThreeFermiList[p2].level2.parity_index
        blocking3["p2_PP="] = p_ThreeFermiList[p2].level3.parity_index
    else:
        blocking1["p2_NP="] = p_ThreeFermiList[p2].level1.parity_index
        blocking2["p2_NP="] = p_ThreeFermiList[p2].level2.parity_index
        blocking3["p2_NP="] = p_ThreeFermiList[p2].level3.parity_index
    return blocking1, blocking2, blocking3


def replace_blocking_levels(blocking_levels, index, hk_file_path):
    """替换run.hk中对应块(1,2,3)的阻塞参数
    """
    with open(hk_file_path, 'r') as file:
        lines = file.readlines()

    # 找到三个关键字行的行号
    KEY_LINEs = []
    for i, line in enumerate(lines):
        if line.strip() in KEY_BLOCKING_LEVELS:
            KEY_LINEs.append(i)

    # 确定要替换的行范围
    start = KEY_LINEs[index - 1] + 1
    if index < len(KEY_LINEs):
        end = KEY_LINEs[index]
    else:
        # 最后一个块，找到 fi 行作为结束
        end = start
        for i in range(start, len(lines)):
            if lines[i].strip() == 'fi':
                end = i
                break

    # 在目标范围内替换变量赋值
    for i in range(start, end):
        for key, value in blocking_levels.items():
            if lines[i].strip().startswith(key):
                lines[i] = key + str(value) + '\n'
                break

    # 写回文件
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


if __name__ == "__main__":
    KEY_NAME = "Ds269-HKpr1n2p"
    proton_num = 110
    neutron_num = 159
    level_range = 8
    out_file_path = "hk.out"

    # 获取费米面附近的三个单粒子态列表
    n_ThreeFermiList = n_GetFermiThreeLevelList(proton_num, neutron_num, out_file_path, level_range=level_range, is_manual_selection=False)
    p_ThreeFermiList = p_GetFermiThreeLevelList(proton_num, neutron_num, out_file_path, level_range=level_range, is_manual_selection=False)

    # 参数设置
    start_B4=-0.053
    line1 = " \$DEFFI NB2=8, NGA=8, BET20=0.13,GAM0=0.075, NAZWIT=4,"
    line2 = "        DB2=0.02, DGA=0.02, NNNSTP=2, NNPSTP=2,"
    replace_hk_startB4(start_B4)
    replace_hk_params(line1, line2)

    # 运行示例
    example_list = [
        # n1, p1, p2
        (73, 55, 56),
        (73, 55, 57),
        (73, 55, 58),
    ]

    countBegin = 14
    for i, (n1Index, p1Index, p2Index) in enumerate(example_list):
        count = countBegin + i
        print(f"正在运行示例 {i+1}，参数索引: Index(n1)={n1Index}, Index(p1)={p1Index}, Index(p2)={p2Index}")
        blocking1, blocking2, blocking3 = Indexs2blocking(n1Index, p1Index, p2Index, n_ThreeFermiList, p_ThreeFermiList)
        replace_blocking_levels(blocking1, 1)
        replace_blocking_levels(blocking2, 2)
        replace_blocking_levels(blocking3, 3)
        replace_sh_command(KEY_NAME, count)
        time.sleep(10)
