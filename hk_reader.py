# 读取 hk.out 文件，提取其中的数值数据并进行处理
import re
import dataclasses
import math
import numpy as np


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
# index)  energy  parity  (local_index)  N, n_z, Lambda, Omega
#    15)  -.2869E+02  - (  8)   3.5, 0.7, 2.4, 2.50      
#   133)  0.5730E+00  - ( 69)   7.0, 4.5, 0.4, 0.50
int_pattern = r"\d+"
float_pattern = r"\d+\.\d+"
scientific_pattern = r"[+-]?\d*\.\d+E[+-]?\d+"
parity_pattern = r"[+-]"
level_match_pattern = rf"\s*({int_pattern})\)\s*({scientific_pattern})\s*({parity_pattern})\s*\(\s*({int_pattern})\s*\)\s*({float_pattern}),\s*({float_pattern}),\s*({float_pattern}),\s*({float_pattern})"




# 设计数据块结构
@dataclasses.dataclass
class LevelData:
    index: int
    energy: float
    parity: str
    local_index: int
    N: float
    n_z: float
    Lambda: float
    Omega: float

    # 打印函数
    def __str__(self):
        # 设置宽度和格式（与 header 保持一致的列宽）
        index_str = f"{self.index:>5})"
        parity_local_str = f"{self.parity:>6}   ({self.local_index:>3})"
        Nillson_str = f"{self.N:>4.1f}, {self.n_z:>4.1f}, {self.Lambda:>6.1f}, {self.Omega:>6.2f}"
        return f"{index_str} {parity_local_str} {Nillson_str}"
    # 表头函数
    @staticmethod
    def header():
        # 使用与 __str__ 相同的列宽，确保表头与数据严格对齐
        index_str = f"{'Index':>5})"
        parity_local_str = f"{'Parity':>6}   ({'Idx':>3})"
        Nillson_str = f"{'N':>4}, {'n_z':>4}, {'Lambda':>6}, {'Omega':>6}"
        return f"{index_str} {parity_local_str} {Nillson_str}"


    # 比较函数, 对比差别, 返回差别大小
    def compare(self, other):
        if self.parity != other.parity:
            return float('inf')  # 无穷大表示完全不同
        N_diff      = abs(self.N - other.N)
        n_z_diff    = abs(self.n_z - other.n_z)
        Lambda_diff = abs(self.Lambda - other.Lambda)
        Omega_diff  = abs(self.Omega - other.Omega) 
        if N_diff > 1.0 :
            return float('inf')  # N差别过大表示完全不同
        if n_z_diff > 1.0 :
            return float('inf')  # n_z差别过大表示完全不同

        # N 与 n_z 的差别权重较大，Lambda 和 Omega 的差别权重较小
        return 3 * N_diff + 3 * n_z_diff + Lambda_diff + Omega_diff


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
            index=int(match[0]),
            energy=float(match[1]),
            parity=match[2],
            local_index=int(match[3]),
            N=float(match[4]),
            n_z=float(match[5]),
            Lambda=float(match[6]),
            Omega=float(match[7])
        )
        data_blocks.append(thisblock)
    return data_blocks


# 提取数据块函数，返回一个包含 LevelData 对象的列表
def extract_level_in_block(file_path, start_line):
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
    level_block.sort(key=lambda x: x.index)
    return level_block


# 给定Fermi面的能级列表，寻找另外一个数据库中最匹配的能级列表
def find_matching_levels(fermi_levels, other_block):
    other_fermi_levels = []
    for level_index, fermi_level in enumerate(fermi_levels):
        # 初始化最佳匹配为同一索引的能级，并计算差别
        best_match = other_block[level_index]  # 默认匹配同一索引的能级
        best_diff = fermi_level.compare(best_match)
        for level in other_block:
            if abs(fermi_level.index - level.index) > 5:  # 只考虑索引相近的能级
                continue
            diff = fermi_level.compare(level)
            if diff < best_diff:
                best_diff = diff
                best_match = level
        # 如果最佳匹配的差别过大，说明没有找到合适的匹配
        if fermi_level.compare(best_match) == float('inf'):
            print(f"警告: 无法找到与 {fermi_level}) 的匹配能级")
        # 无论如何, 添加最佳匹配到结果列表中, 以保持结果列表的长度与输入的fermi_levels一致
        other_fermi_levels.append(best_match)
    return other_fermi_levels


# 主函数: 给定质子数和中子数，提取对应的中子费米面附近的能级，并进行匹配比较
def match_neutron_levels(proton_num, neutron_num, file_path, level_range=10):
    print(f"\n正在提取质子数 {proton_num} 和中子数 {neutron_num} 的【中子】费米面附近能级...")
    proton_fermi = math.ceil(proton_num / 2)
    neutron_fermi = math.ceil(neutron_num / 2)
    line_numbers = find_line_numbers(file_path, Nilsson_keywords)

    level_block_n1 = extract_level_in_block(file_path, line_numbers[0])
    level_block_n2 = extract_level_in_block(file_path, line_numbers[2])
    level_block_n3 = extract_level_in_block(file_path, line_numbers[4])

    raw_fermi_levels_n1 = level_block_n1[neutron_fermi-level_range:neutron_fermi+level_range]
    raw_fermi_levels_n2 = level_block_n2[neutron_fermi-level_range:neutron_fermi+level_range]
    raw_fermi_levels_n3 = level_block_n3[neutron_fermi-level_range:neutron_fermi+level_range]

    fermi_levels_n1 = raw_fermi_levels_n1
    fermi_levels_n2 = find_matching_levels(fermi_levels_n1, raw_fermi_levels_n2)
    fermi_levels_n3 = find_matching_levels(fermi_levels_n1, raw_fermi_levels_n3)
    
    # 打印表头
    print("\n"+"*"*40+"中子能级匹配结果:"+"*"*40)
    header_str = LevelData.header()
    print(header_str + "  |  " + header_str + "  |  " + header_str)
    # 打印每一行的匹配结果
    for i in range(len(fermi_levels_n1)):
        print(f"{fermi_levels_n1[i]}  |  {fermi_levels_n2[i]}  |  {fermi_levels_n3[i]}")
    
    return fermi_levels_n1, fermi_levels_n2, fermi_levels_n3


# 主函数: 给定质子数和中子数，提取对应的质子费米面附近的能级，并进行匹配比较
def match_proton_levels(proton_num, neutron_num, file_path, level_range=10):
    print(f"\n正在提取质子数 {proton_num} 和中子数 {neutron_num} 的【质子】费米面附近能级...")
    proton_fermi = math.ceil(proton_num / 2)
    neutron_fermi = math.ceil(neutron_num / 2)
    line_numbers = find_line_numbers(file_path, Nilsson_keywords)

    level_block_p1 = extract_level_in_block(file_path, line_numbers[1])
    level_block_p2 = extract_level_in_block(file_path, line_numbers[3])
    level_block_p3 = extract_level_in_block(file_path, line_numbers[5])

    raw_fermi_levels_p1 = level_block_p1[proton_fermi-level_range:proton_fermi+level_range]
    raw_fermi_levels_p2 = level_block_p2[proton_fermi-level_range:proton_fermi+level_range]
    raw_fermi_levels_p3 = level_block_p3[proton_fermi-level_range:proton_fermi+level_range]

    fermi_levels_p1 = raw_fermi_levels_p1
    fermi_levels_p2 = find_matching_levels(fermi_levels_p1, raw_fermi_levels_p2)
    fermi_levels_p3 = find_matching_levels(fermi_levels_p1, raw_fermi_levels_p3)

    # 打印表头
    print("\n"+"*"*40+"质子能级匹配结果:"+"*"*40)
    header_str = LevelData.header()
    print(header_str + "  |  " + header_str + "  |  " + header_str)
    # 打印每一行的匹配结果
    for i in range(len(fermi_levels_p1)):
        print(f"{fermi_levels_p1[i]}  |  {fermi_levels_p2[i]}  |  {fermi_levels_p3[i]}")
    
    return fermi_levels_p1, fermi_levels_p2, fermi_levels_p3



if __name__ == "__main__":
    print("正在读取 hk.out 文件并提取能级数据...")
    proton_num = 120
    neutron_num = 170

    level_range = 10
    file_path = "hk.out"
    match_neutron_levels(proton_num, neutron_num, file_path, level_range)
    match_proton_levels(proton_num, neutron_num, file_path, level_range)