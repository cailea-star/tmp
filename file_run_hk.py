from level_select import n_Fermi_ThreeLevelList, p_Fermi_ThreeLevelList

KEY_WORDs = ["if [ $ind -eq 1 ]; then", 
             "elif [ $ind -eq 2 ]; then", 
             "elif [ $ind -eq 3 ]; then"]


blocking_levels = {
    "n_NPPS=":1,
    "n_NPNS=":2,
    "n_PPPS=":3,
    "n_PPNS=":4,
    "p_NPPS=":5,
    "p_NPNS=":6,
    "p_PPPS=":7,
    "p_PPNS=":8
}


def replace_blocking_levels(blocking_levels, index, file_path="run.hk"):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # 找到三个关键字行的行号
    KEY_LINEs = []
    for i, line in enumerate(lines):
        if line.strip() in KEY_WORDs:
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


if __name__ == "__main__":
    replace_blocking_levels(blocking_levels, index=1, file_path="run.hk")
    replace_blocking_levels(blocking_levels, index=2, file_path="run.hk")
    replace_blocking_levels(blocking_levels, index=3, file_path="run.hk")