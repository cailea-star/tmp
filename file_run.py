import os
import re
import time
from pathlib import Path
from level_select import n_GetFermiThreeLevelList, p_GetFermiThreeLevelList

KEY_BLOCKING_LEVELS = ["if [ $ind -eq 1 ]; then", 
             "elif [ $ind -eq 2 ]; then", 
             "elif [ $ind -eq 3 ]; then"]


KEY_SH_COMMANDS = ["run.hk", "run.mp"]

WSCSM1_DIR = Path.home() / "wscsm1"
sh_file_path = str(WSCSM1_DIR / "run.sh")
hk_file_path = str(WSCSM1_DIR / "run.hk")
log_file_path = str(WSCSM1_DIR / "run.log")


blocking_levels = {
    "n1_PP=":1,
    "n1_NP=":2,
    "p1_PP=":3,
    "p1_NP=":4,
    "p2_PP=":5,
    "p2_NP=":6,
}


def num2blocking(n1Index, p1Index, p2Index, n_ThreeFermiList, p_ThreeFermiList):
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


def replace_blocking_levels(blocking_levels, index, file_path=hk_file_path):
    """替换run.hk中对应块(1,2,3)的阻塞参数
    """
    with open(file_path, 'r') as file:
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
    with open(file_path, 'w') as file:
        file.writelines(lines)


def replace_sh_command(KEY_NAME, count, file_path=sh_file_path):
    """替换run.sh中run.hk与run.mp行，直接覆盖为 {cmd} $Z $Z $N $N KEY_NAME{count}
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        for cmd in KEY_SH_COMMANDS:
            if line.strip().startswith(cmd):
                lines[i] = f"{cmd} $Z $Z $N $N {KEY_NAME}{count}\n"
                break
    
    with open(file_path, 'w') as file:
        file.writelines(lines)


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
    return process.pid


def monitor_process(PID):
    """监控指定PID进程, 若不存在直接返回true, 
    否则每隔10秒检查一次，直到进程结束返回true
    """
    if PID is None:
        return True
    import psutil
    while True:
        if not psutil.pid_exists(PID):
            return True
        time.sleep(10)


def run_example(n1Index, p1Index, p2Index, n_ThreeFermiList, p_ThreeFermiList):
    blocking1, blocking2, blocking3 = num2blocking(n1Index, p1Index, p2Index, n_ThreeFermiList, p_ThreeFermiList)
    print("示例阻塞参数组合:")
    print("组合1:", blocking1)
    print("组合2:", blocking2)
    print("组合3:", blocking3)
    replace_blocking_levels(blocking1, 1)
    replace_blocking_levels(blocking2, 2)
    replace_blocking_levels(blocking3, 3)
    replace_sh_command(KEY_NAME, 0)
    PID = run_sh_command()
    print(f"已启动测试脚本，进程ID: {PID}")
    return PID



if __name__ == "__main__":
    KEY_NAME = "Ds267-HKpr1n2p"
    proton_num = 110
    neutron_num = 157
    level_range = 7
    out_file_path = "hk.out"
    n_ThreeFermiList = n_GetFermiThreeLevelList(proton_num, neutron_num, hk_file_path, level_range=level_range, is_manual_selection=False)
    p_ThreeFermiList = p_GetFermiThreeLevelList(proton_num, neutron_num, hk_file_path, level_range=level_range, is_manual_selection=False)
    n1Index = n_ThreeFermiList[0].level1.index
    p1Index = p_ThreeFermiList[0].level1.index
    p2Index = p_ThreeFermiList[1].level1.index
    PID = run_example(n1Index, p1Index, p2Index, n_ThreeFermiList, p_ThreeFermiList)
    monitor_process(PID)
    print("测试脚本已结束。")