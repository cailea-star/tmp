import math
from level_define import LevelData, ThreeLevelData, ThreeList2OneList, match_ThreeLevelData_list
from level_extract import N_extract_ThreeLevelList_in_file, P_extract_ThreeLevelList_in_file


def input_number_list(string):
    number_list = []
    input_str = input(string + "(以逗号分隔或者以范围表示，例如 1-5) : ")
    if not input_str:
        print("未输入任何索引")
        return number_list
    for num_str in input_str.split(","):
        num_str = num_str.strip()
        if '-' in num_str:
            start, end = map(int, num_str.split('-'))
            number_list.extend(range(start, end + 1))
        else:
            number_list.append(int(num_str))
    return number_list


def select_levels_manual(ThreeLevelData_list):
    print("请手动选择匹配的能级(以','分隔, 以回车结束)...")
    print(ThreeLevelData.header())
    for i in range(len(ThreeLevelData_list)):
        print(ThreeLevelData_list[i])

    # 解析输入的索引列表, 允许用户使用 [x ,] 或者 [x-y,] 的格式输入索引范围 
    selected_indices = input_number_list("请输入选择的第一列能级索引【 Index) 】")
    if len(selected_indices) == 0:
        return ThreeLevelData_list # 如果用户没有输入任何索引, 则返回原始的能级列表
    selected_ThreeLevelData_list = []
    for idx in selected_indices:
        isfound = False
        for i in range(len(ThreeLevelData_list)):
            if ThreeLevelData_list[i].level1.index == idx:
                selected_ThreeLevelData_list.append(ThreeLevelData_list[i])
                isfound = True
                break
        if not isfound:
            print(f"警告: 无法找到索引为 {idx}) 的能级")
    print(ThreeLevelData.header())
    for i in range(len(selected_ThreeLevelData_list)):
        print(selected_ThreeLevelData_list[i])
    print("*" * 170)
    return selected_ThreeLevelData_list



# 主函数: 给定质子数和中子数，提取对应的中子费米面附近的能级，并进行匹配比较
def match_neutron_levels(proton_num, neutron_num, file_path, level_range=10, is_manual_selection=False):
    print(f"\n正在读取文件 {file_path}...")
    print(f"正在提取质子数 {proton_num} 和中子数 {neutron_num} 的【中子】费米面附近能级...")
    proton_fermi = math.ceil(proton_num / 2)
    neutron_fermi = math.ceil(neutron_num / 2)

    n_ThreeLevel_list = N_extract_ThreeLevelList_in_file(file_path)
    n1_level_list = ThreeList2OneList(n_ThreeLevel_list, level_num=1)
    n1_fermi_list = n1_level_list[neutron_fermi-level_range : neutron_fermi+level_range]
    n_ThreeLevel_list = match_ThreeLevelData_list(n1_fermi_list, n_ThreeLevel_list)

    if is_manual_selection:
        return select_levels_manual(n_ThreeLevel_list)
    else:
        print(ThreeLevelData.header())
        for i in range(len(n_ThreeLevel_list)):
            print(n_ThreeLevel_list[i])
        return n_ThreeLevel_list


# 主函数: 给定质子数和中子数，提取对应的质子费米面附近的能级，并进行匹配比较
def match_proton_levels(proton_num, neutron_num, file_path, level_range=10, is_manual_selection=False):
    print(f"\n正在读取文件 {file_path}...")
    print(f"正在提取质子数 {proton_num} 和中子数 {neutron_num} 的【质子】费米面附近能级...")
    proton_fermi = math.ceil(proton_num / 2)
    neutron_fermi = math.ceil(neutron_num / 2)

    p_ThreeLevel_list = P_extract_ThreeLevelList_in_file(file_path)
    p1_level_list = ThreeList2OneList(p_ThreeLevel_list, level_num=1)
    p1_fermi_list = p1_level_list[proton_fermi-level_range : proton_fermi+level_range]
    p_ThreeLevel_list = match_ThreeLevelData_list(p1_fermi_list, p_ThreeLevel_list)

    if is_manual_selection:
        return select_levels_manual(p_ThreeLevel_list)
    else:
        print(ThreeLevelData.header())
        for i in range(len(p_ThreeLevel_list)):
            print(p_ThreeLevel_list[i])
        return p_ThreeLevel_list




if __name__ == "__main__":
    proton_num = 120
    neutron_num = 170

    level_range = 10
    file_path = "hk.out"
    match_neutron_levels(proton_num, neutron_num, file_path, level_range, is_manual_selection=False)
    match_proton_levels(proton_num, neutron_num, file_path, level_range, is_manual_selection=False)
