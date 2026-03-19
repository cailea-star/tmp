# -*- coding: utf-8 -*-
# Author: Cailea
# Date: 2024-06-20
# Description: 运行示例脚本，展示如何使用 level_select.py 中的函数来提取费米面附近的能级，并将其应用于替换 run.hk 中的参数，并执行 run.sh 脚本。

# Functions:
# - input_number_list: 解析用户输入的索引列表，支持逗号分隔和范围表示。
# - select_levels_manual: 提供一个交互式界面，让用户手动选择匹配的能级。
# - n_GetFermiThreeLevelList: 提取中子费米面附近的能级列表，并进行匹配比较, 返回一个包含 ThreeLevelData 对象的列表。
# - p_GetFermiThreeLevelList: 提取质子费米面附近的能级列表，并进行匹配比较, 返回一个包含 ThreeLevelData 对象的列表。


import math
from pathlib import Path
from level_define import LevelData, ThreeLevelData, ThreeList2OneList, match_ThreeLevelData_list
from level_extract import N_extract_ThreeLevelList_in_file, P_extract_ThreeLevelList_in_file


def write_ThreeLevelList_to_file(ThreeLevelData_list, output_path):
    """将能级列表写入文件, 以便后续解析和使用
    """
    with open(output_path, 'w') as f:
        f.write(ThreeLevelData.header() + "\n")
        for data in ThreeLevelData_list:
            f.write(str(data) + "\n")
    print(f"已将能级列表写入文件 {output_path}")


def read_ThreeLevelList_from_file(input_path):
    """将文件中的能级列表读取到内存, 以便后续解析和使用
    1. 将数据中的 ")", "()", "|" 替换为逗号, 以便后续解析
    2. 将数据中的 空格 全部去除, 以便后续解析
    3. 注意处理表头, 以便后续使用字典解析数据行, 以便后续解析
    """
    ThreeLevelList = []
    with open(input_path, 'r') as f:
        lines = f.readlines()
    # 1 清洗表格的分割符号, 以便后续解析
    for i in range(len(lines)):
        line = lines[i]
        line = line.replace(")", ",")
        line = line.replace("(", ",")
        line = line.replace("|", ",")
        line = line.replace(" ", "")
        lines[i] = line
    # 2 解析表头, 以便后续解析
    header = lines[0].strip()
    header_fields = header.split(",")
    # 3 解析数据行, 以便后续解析
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        fields = line.split(",")
        dict_data = dict(zip(header_fields, fields))
        levels = []
        for beta_idx in range(3):
            real_idx = beta_idx + 1
            energy = 0.0
            Index   = int(dict_data[f"Index{real_idx}"])
            parity  = str(dict_data[f"π{real_idx}"])
            Idx     = int(dict_data[f"Idx{real_idx}"])
            N       = float(dict_data[f"N{real_idx}"])
            nz      = float(dict_data[f"nz{real_idx}"])
            Lambda  = float(dict_data[f"Λ{real_idx}"])
            Omega   = float(dict_data[f"Ω{real_idx}"])
            level   = LevelData(Index, energy, parity, Idx, N, nz, Lambda, Omega)
            levels.append(level)
        ThreeLevel = ThreeLevelData(levels[0], levels[1], levels[2])
        ThreeLevelList.append(ThreeLevel)
    print(f"已从文件 {input_path} 中读取 {len(ThreeLevelList)} 条能级数据:")
    print(ThreeLevelData.header())
    for ThreeLevel in ThreeLevelList:
        print(ThreeLevel)
    return ThreeLevelList



# 主函数: 给定质子数和中子数，提取对应的中子费米面附近的能级，并进行匹配比较
def N_GetFermiThreeLevelList(proton_num, neutron_num, hkout_path, level_range=10):
    print(f"\n正在读取文件 {hkout_path}...")
    print(f"正在提取质子数 {proton_num} 和中子数 {neutron_num} 的【中子】费米面附近能级...")
    proton_fermi = math.ceil(proton_num / 2)
    neutron_fermi = math.ceil(neutron_num / 2)

    n_ThreeLevelList = N_extract_ThreeLevelList_in_file(hkout_path)
    n1_level_list = ThreeList2OneList(n_ThreeLevelList, beta_idx=1)
    n1_fermi_list = n1_level_list[neutron_fermi-level_range : neutron_fermi+level_range]
    n_ThreeFermiList = match_ThreeLevelData_list(n1_fermi_list, n_ThreeLevelList)

    print(ThreeLevelData.header())
    for n_ThreeLeval in n_ThreeFermiList:
        print(n_ThreeLeval)
    return n_ThreeFermiList


# 主函数: 给定质子数和中子数，提取对应的质子费米面附近的能级，并进行匹配比较
def P_GetFermiThreeLevelList(proton_num, neutron_num, hkout_path, level_range=10):
    print(f"\n正在读取文件 {hkout_path}...")
    print(f"正在提取质子数 {proton_num} 和中子数 {neutron_num} 的【质子】费米面附近能级...")
    proton_fermi = math.ceil(proton_num / 2)
    neutron_fermi = math.ceil(neutron_num / 2)

    p_ThreeLevelList = P_extract_ThreeLevelList_in_file(hkout_path)
    p1_level_list = ThreeList2OneList(p_ThreeLevelList, beta_idx=1)
    p1_fermi_list = p1_level_list[proton_fermi-level_range : proton_fermi+level_range]
    p_ThreeFermiList = match_ThreeLevelData_list(p1_fermi_list, p_ThreeLevelList)

    print(ThreeLevelData.header())
    for p_ThreeLeval in p_ThreeFermiList:
        print(p_ThreeLeval)
    return p_ThreeFermiList


def Select_FermiThreeLevelList(proton_num, neutron_num, hkout_path, level_range=10):
    """写入费米面附近的能级列表到文件, 以便用户手动选择匹配的能级, 然后读取用户选择的能级列表, 返回一个包含 ThreeLevelData 对象的列表
    return: n_ThreeFermiList, p_ThreeFermiList
    """
    n_ThreeLevelList = N_extract_ThreeLevelList_in_file(hkout_path)
    p_ThreeLevelList = P_extract_ThreeLevelList_in_file(hkout_path)
    n_ThreeFermiList = N_GetFermiThreeLevelList(proton_num, neutron_num, hkout_path, level_range)
    p_ThreeFermiList = P_GetFermiThreeLevelList(proton_num, neutron_num, hkout_path, level_range)

    scripts_dir = Path(__file__).parent
    n_all_name = "n_ThreeAll.txt"
    p_all_name = "p_ThreeAll.txt"
    n_fermi_name = "n_ThreeFermi.txt"
    p_fermi_name = "p_ThreeFermi.txt"
    write_ThreeLevelList_to_file(n_ThreeLevelList, scripts_dir / n_all_name)
    write_ThreeLevelList_to_file(p_ThreeLevelList, scripts_dir / p_all_name)
    write_ThreeLevelList_to_file(n_ThreeFermiList, scripts_dir / n_fermi_name)
    write_ThreeLevelList_to_file(p_ThreeFermiList, scripts_dir / p_fermi_name)

    print(f"已写入 {n_all_name}, {p_all_name}, {n_fermi_name} 和 {p_fermi_name},")
    print("请打开文件查看费米面附近的能级列表，并根据需要进行手动选择匹配的能级。")
    is_continue = input("请输入 yes 或 no: ")
    if is_continue.lower() != "yes":
        print("程序已终止。")
        exit(0)
    
    print("正在读取用户选择的能级列表...")
    print(f"修复后的【中子能级】:")
    n_ThreeFermiList = read_ThreeLevelList_from_file(scripts_dir / n_fermi_name)
    print(f"修复后的【质子能级】:")
    p_ThreeFermiList = read_ThreeLevelList_from_file(scripts_dir / p_fermi_name)

    return n_ThreeFermiList, p_ThreeFermiList


if __name__ == "__main__":
    proton_num = 120
    neutron_num = 170

    level_range = 10
    hkout_path = "hk.out"
    Select_FermiThreeLevelList(proton_num, neutron_num, hkout_path, level_range)