# -*- coding: utf-8 -*-
# 运行示例的脚本，包含了参数替换、执行脚本和监控进程的功能。
import time
from pathlib import Path
from level_select import n_GetFermiThreeLevelList, p_GetFermiThreeLevelList
from replace_content import replace_blocking_levels, replace_sh_command, replace_hk_startB4, replace_hk_params
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
    print("组合1:", blocking1)
    print("组合2:", blocking2)
    print("组合3:", blocking3)
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
