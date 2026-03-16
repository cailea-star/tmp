# -*- coding: utf-8 -*-
# Author: Cailea
# Date: 2024-06-20
# Description: 运行示例脚本，展示如何使用 level_select.py 中的函数来提取费米面附近的能级，并将其应用于替换 run.hk 中的参数，并执行 run.sh 脚本。

# Functions:
# - run_sh_command: 后台执行 run.sh 脚本并返回 process 对象。
# - run_example: 根据给定的参数索引，生成阻塞参数组合，

import time
from pathlib import Path
from level_select import n_GetFermiThreeLevelList, p_GetFermiThreeLevelList
from replace_content import replace_blocking_levels
from replace_content import replace_sh_command, replace_sh_NZ
from replace_content import replace_hk_startB4, replace_hk_params
from replace_content import Indexs2blocking


WSCSM1_DIR = Path.home() / "wscsm1"
sh_file_path = str(WSCSM1_DIR / "run.sh")
hk_file_path = str(WSCSM1_DIR / "run.hk")
log_file_path = str(WSCSM1_DIR / "run.log")




def run_sh_command():
    """后台执行 run.sh 脚本并返回进程ID。"""
    import subprocess
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            ["bash", sh_file_path],
            shell=False,
            cwd=str(WSCSM1_DIR),
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
        )
    return process


def run_example(n1Index, p1Index, p2Index, count, n_ThreeFermiList, p_ThreeFermiList):
    blocking1, blocking2, blocking3 = Indexs2blocking(n1Index, p1Index, p2Index, n_ThreeFermiList, p_ThreeFermiList)
    print("示例阻塞参数组合:")
    print("形变1:", blocking1)
    print("形变2:", blocking2)
    print("形变3:", blocking3)
    replace_blocking_levels(blocking1, 1, hk_file_path)
    replace_blocking_levels(blocking2, 2, hk_file_path)
    replace_blocking_levels(blocking3, 3, hk_file_path)
    replace_sh_command(KEY_NAME, count, sh_file_path)
    process = run_sh_command()
    print(f"已启动测试脚本，进程ID: {process.pid}")
    process.wait()  # 等待进程完成
    print("测试脚本已完成。")



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
    replace_hk_startB4(start_B4, hk_file_path)
    replace_hk_params(line1, line2, hk_file_path)
    replace_sh_NZ(proton_num, neutron_num, sh_file_path)

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
        run_example(n1Index, p1Index, p2Index, count, n_ThreeFermiList, p_ThreeFermiList)


# python3 run_example.py