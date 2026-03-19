# -*- coding: utf-8 -*-
# Author: Cailea
# Date: 2024-06-20
# Description: 设计了 LevelData 和 ThreeLevelData 两个数据类来表示能级数据块的结构，并提供了比较函数来评估两个能级数据块之间的差别大小。

# Functions:
# - LevelData: 表示单个能级数据块的类，包含了能级的索引、能量、宇称、Nillson 量子数等属性，并提供了一个比较函数来评估两个能级数据块之间的差别大小。
# - ThreeLevelData: 表示三个能级数据块组合的类，包含了 level1、level2 和 level3 三个 LevelData 对象，并提供了一个 __str__ 方法来格式化输出。
# - ThreeList2OneList: 将一个包含 ThreeLevelData 对象的列表转换为一个包含 LevelData 对象的列表，指定要提取的 level_num。
# - match_ThreeLevelData_list: 将费米面附近的能级列表与提取的 ThreeLevelData 列表进行匹配比较，返回一个包含匹配结果的 ThreeLevelData 列表。

# 设计数据块结构
class LevelData:
    index: int
    energy: float
    parity: str
    parity_index: int
    N: float
    nz: float
    Lambda: float
    Omega: float

    def __init__(self, index, energy, parity, parity_index, N, nz, Lambda, Omega):
            self.index = index
            self.energy = energy
            self.parity = parity
            self.parity_index = parity_index
            self.N = N
            self.nz = nz
            self.Lambda = Lambda
            self.Omega = Omega

    # 打印函数
    def __str__(self):
        # 设置宽度和格式（与 header 保持一致的列宽）
        index_str = f"{self.index:>5})"
        parity_local_str = f"{self.parity:>1} ({self.parity_index:>3})"
        Nillson_str = f"{self.N:>3.1f}, {self.nz:>3.1f}, {self.Lambda:>3.1f}, {self.Omega:>4.2f}"
        return f"{index_str} {parity_local_str} {Nillson_str}"
    # 表头函数
    @staticmethod
    def header():
        # 使用与 __str__ 相同的列宽，确保表头与数据严格对齐
        index_str = f"{'Index':>5})"
        parity_local_str = f"{'π':>1} ({'Idx':>3})"
        Nillson_str = f"{'N':>3}, {'nz':>3}, {'Λ':>3}, {'Ω':>4}"
        return f"{index_str} {parity_local_str} {Nillson_str}"


    # 比较函数, 对比差别, 返回差别大小
    def compare(self, other):
        index_diff = abs(self.index - other.index)
        N_diff      = abs(self.N - other.N)
        nz_diff    = abs(self.nz - other.nz)
        Lambda_diff = abs(self.Lambda - other.Lambda)
        Omega_diff  = abs(self.Omega - other.Omega) 
        if self.parity != other.parity:
            return float('inf')  # 无穷大表示完全不同
        if index_diff > 5:
            return float('inf')  # 索引差别过大表示完全不同
        if N_diff > 1.0 :
            return float('inf')  # N差别过大表示完全不同
        if nz_diff > 1.0 :
            return float('inf')  # n_z差别过大表示完全不同
        if Omega_diff > 0.5:
            return float('inf')  # Omega差别过大表示完全不同

        # N 与 n_z 的差别权重较大，Lambda 和 Omega 的差别权重较小
        return 3 * N_diff + 3 * nz_diff + Lambda_diff + 3 * Omega_diff


class ThreeLevelData:
    level1: LevelData
    level2: LevelData
    level3: LevelData
    
    def __init__(self, level1, level2, level3):
        self.level1 = level1
        self.level2 = level2
        self.level3 = level3

    def __str__(self):
        return f"{self.level1}  |  {self.level2}  |  {self.level3}"
    
    @staticmethod
    def header():
        return f"{LevelData.header()}  |  {LevelData.header()}  |  {LevelData.header()}"
    

def ThreeList2OneList(ThreeLevelData_list, level_num=1):
    one_list = []
    for three_level in ThreeLevelData_list:
        if level_num == 1:
            one_list.append(three_level.level1)
        elif level_num == 2:
            one_list.append(three_level.level2)
        elif level_num == 3:
            one_list.append(three_level.level3)
    return one_list


def match_ThreeLevelData_list(Fermi_Level_list, ThreeLevel_list):
    matched_ThreeLevel_list = []
    for fermi_level in Fermi_Level_list:
        best1 = ThreeLevel_list[0].level1
        best2 = ThreeLevel_list[0].level2
        best3 = ThreeLevel_list[0].level3
        best_diff1 = fermi_level.compare(best1)
        best_diff2 = fermi_level.compare(best2)
        best_diff3 = fermi_level.compare(best3)
        for three_level in ThreeLevel_list:
            diff1 = fermi_level.compare(three_level.level1)
            diff2 = fermi_level.compare(three_level.level2)
            diff3 = fermi_level.compare(three_level.level3)
            if diff1 < best_diff1:
                best_diff1 = diff1
                best1 = three_level.level1
            if diff2 < best_diff2:
                best_diff2 = diff2
                best2 = three_level.level2
            if diff3 < best_diff3:
                best_diff3 = diff3
                best3 = three_level.level3
        if best_diff1 == float('inf'):
            print(f"警告: 无法找到与费米面能级 {fermi_level.index}) 匹配的 level1 能级")
            continue
        if best_diff2 == float('inf'):
            print(f"警告: 无法找到与费米面能级 {fermi_level.index}) 匹配的 level2 能级")
            continue
        if best_diff3 == float('inf'):
            print(f"警告: 无法找到与费米面能级 {fermi_level.index}) 匹配的 level3 能级")
            continue
        matched_ThreeLevel_list.append(ThreeLevelData(best1, best2, best3))
    return matched_ThreeLevel_list

# 一些常见符号的直接映射, 方便后续使用简要打印:
# \pi : π
# \nu : ν
# \Lambda : Λ
# \Omega : Ω