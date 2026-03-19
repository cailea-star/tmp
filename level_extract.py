# -*- coding: utf-8 -*-
# Author: Cailea
# Date: 2024-06-20
# Description: 运行示例脚本，展示如何使用 level_select.py 中的函数来提取费米面附近的能级，并将其应用于替换 run.hk 中的参数，并执行 run.sh 脚本。

# Functions:
# - find_line_numbers: 返回包含【匹配字段】的行号。
# - judge_level_in_line: 判断行字符串中是否包含能级数据块的匹配字段。
# - extract_level_in_line: 提取行字符串中的数据块，返回一个包含 LevelData 对象的列表。
# - extract_level_list_in_block: 提取数据块函数，返回一个包含 LevelData 对象的列表。
# - N_extract_ThreeLevelList_in_file: 提取文件中全部的中子能级数据块，返回一个包含 ThreeLevelData 对象的列表。
# - P_extract_ThreeLevelList_in_file: 提取文件中全部的质子能级数据块，返回一个包含 ThreeLevelData 对象的列表。

import re
from level_define import LevelData, ThreeLevelData


# Nilsson 量子数 关键词
Nilsson_keywords = "NILSSON NUMBERS FOR WS-BASIS"


# 返回包含【匹配字段】的行号
def find_line_numbers(file_path, keyword):
    line_numbers = []
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if keyword in line:
                line_numbers.append(line_number)
    return line_numbers



# 数据匹配字段: 
# Index)  energy  parity  (Idx)  N, n_z, Lambda, Omega
#    15)  -.2869E+02  - (  8)   3.5, 0.7, 2.4, 2.50      
#   133)  0.5730E+00  - ( 69)   7.0, 4.5, 0.4, 0.50
int_pattern = r"\d+"
float_pattern = r"\d+\.\d+"
scientific_pattern = r"[+-]?\d*\.\d+E[+-]?\d+"
parity_pattern = r"[+-]"
level_match_pattern = rf"\s*({int_pattern})\)\s*({scientific_pattern})\s*({parity_pattern})\s*\(\s*({int_pattern})\s*\)\s*({float_pattern}),\s*({float_pattern}),\s*({float_pattern}),\s*({float_pattern})"


# 判断行字符串中是否包含能级数据块的匹配字段
def judge_level_in_line(line_string):
    matches = re.findall(level_match_pattern, line_string)
    return len(matches) > 0

# 提取行字符串中的数据块，返回一个包含 LevelData 对象的列表
def extract_level_in_line(line_string):
    matches = re.findall(level_match_pattern, line_string)
    data_blocks = []
    for match in matches:
        thisblock = LevelData(
            Index=int(match[0]),
            energy=float(match[1]),
            parity=match[2],
            Idx=int(match[3]),
            N=float(match[4]),
            nz=float(match[5]),
            Lambda=float(match[6]),
            Omega=float(match[7])
        )
        data_blocks.append(thisblock)
    return data_blocks


# 提取数据块函数，返回一个包含 LevelData 对象的列表
def extract_level_list_in_block(file_path, start_line):
    isbegin = False
    isend = False
    level_block = []
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if line_number < start_line:
                continue
            if (not isbegin) and judge_level_in_line(line):
                isbegin = True
            if isbegin and judge_level_in_line(line):
                level_block.extend(extract_level_in_line(line))
            if isbegin and (not judge_level_in_line(line)):
                isend = True
            if isend:
                break
    # 排序
    level_block.sort(key=lambda x: x.Index)
    return level_block


def N_extract_ThreeLevelList_in_file(file_path):
    line_numbers = find_line_numbers(file_path, Nilsson_keywords)
    # 提取neutron能级数据块, n1, p1, n2, p2, n3, p3
    neutron_block_n1 = extract_level_list_in_block(file_path, line_numbers[0])
    neutron_block_n2 = extract_level_list_in_block(file_path, line_numbers[2])
    neutron_block_n3 = extract_level_list_in_block(file_path, line_numbers[4])
    neutron_ThreeLevelData_list = []
    for i in range(len(neutron_block_n1)):
        three_level = ThreeLevelData(
            neutron_block_n1[i],
            neutron_block_n2[i],
            neutron_block_n3[i])
        neutron_ThreeLevelData_list.append(three_level)
    return neutron_ThreeLevelData_list

def P_extract_ThreeLevelList_in_file(file_path):
    line_numbers = find_line_numbers(file_path, Nilsson_keywords)
    # 提取proton能级数据块, n1, p1, n2, p2, n3, p3
    proton_block_p1 = extract_level_list_in_block(file_path, line_numbers[1])
    proton_block_p2 = extract_level_list_in_block(file_path, line_numbers[3])
    proton_block_p3 = extract_level_list_in_block(file_path, line_numbers[5])
    proton_ThreeLevelData_list = []
    for i in range(len(proton_block_p1)):
        three_level = ThreeLevelData(
            proton_block_p1[i], 
            proton_block_p2[i], 
            proton_block_p3[i])
        proton_ThreeLevelData_list.append(three_level)
    return proton_ThreeLevelData_list


if __name__ == "__main__":
    proton_num = 110
    neutron_num = 157

    file_path = "hk.out"
    print(f"\n正在提取文件 {file_path} 的能级数据...")
    proton_ThreeLevelData_List = P_extract_ThreeLevelList_in_file(file_path)
    neutron_ThreeLevelData_List = N_extract_ThreeLevelList_in_file(file_path)
    print('\n质子能级数据提取完成！')
    print(ThreeLevelData.header())
    for i in range(10):
        print(proton_ThreeLevelData_List[i])
    print("...")

    print('\n中子能级数据提取完成！')
    print(ThreeLevelData.header())
    for i in range(10):
        print(neutron_ThreeLevelData_List[i])
    print("...")