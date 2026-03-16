import re
from level_select import n_Fermi_ThreeLevelList, p_Fermi_ThreeLevelList

KEY_BLOCKING_LEVELS = ["if [ $ind -eq 1 ]; then", 
             "elif [ $ind -eq 2 ]; then", 
             "elif [ $ind -eq 3 ]; then"]


KEY_SH_COMMANDS = ["run.hk", "run.mp"]

sh_file_path = "~/wscsm1/run.sh"
hk_file_path = "~/wscsm1/run.hk"

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


def replace_sh_command(KEY_NAME, number, file_path=sh_file_path):
    """替换run.sh中对应的命令(run.hk或run.mp)，将KEY_SH_NAME后的计数器替换为number
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # 匹配 run.hk/run.mp 行中 KEY_NAME 后的计数器数字并替换
    pattern = re.compile(r'(' + re.escape(KEY_NAME) + r')\d+')
    for i, line in enumerate(lines):
        for cmd in KEY_SH_COMMANDS:
            if line.strip().startswith(cmd):
                lines[i] = pattern.sub(r'\g<1>' + str(number), line)
                break

    with open(file_path, 'w') as file:
        file.writelines(lines)



def generate_run(proton_num, neutron_num, hkout_path, level_range, KEY_NAME):
    n_3Fermi_list = n_Fermi_ThreeLevelList(proton_num, neutron_num, hkout_path, level_range, is_manual_selection=False)
    p_3Fermi_list = p_Fermi_ThreeLevelList(proton_num, neutron_num, hkout_path, level_range, is_manual_selection=False)

    len_n = len(n_3Fermi_list)
    len_p = len(p_3Fermi_list)
    print(f"计算 Z = {proton_num}, N = {neutron_num} 的 2p-1n 阻塞组合")
    print(f'总计选取的质子单粒子态数: {len_p}, 中子单粒子态数: {len_n}')
    print(f"总计的阻塞组合数: {len_n * len_p * (len_p - 1) // 2}")
    ifRUN = input("是否批量运行生成的 run.hk 文件？(y/n): ")
    if ifRUN.lower() == 'y':
        print("正在生成并运行 run.hk 文件...")
    else:
        return 0

    count = 0
    for n1 in range(len_n):
        n11_localidx = n_3Fermi_list[n1].level1.local_index
        n12_localidx = n_3Fermi_list[n1].level2.local_index
        n13_localidx = n_3Fermi_list[n1].level3.local_index
        n1_parity = n_3Fermi_list[n1].level1.parity
        tmp_string1 = blocking_levels.copy()
        tmp_string2 = blocking_levels.copy()
        tmp_string3 = blocking_levels.copy()
        if n1_parity == "+":
            tmp_string1["n_PPNS="] = n11_localidx
            tmp_string2["n_PPPS="] = n12_localidx
            tmp_string3["n_PPNS="] = n13_localidx
        else:
            tmp_string1["n_NPNS="] = n11_localidx
            tmp_string2["n_NPPS="] = n12_localidx
            tmp_string3["n_NPNS="] = n13_localidx

        for p1 in range(len_p):
            p11_localidx = p_3Fermi_list[p1].level1.local_index
            p12_localidx = p_3Fermi_list[p1].level2.local_index
            p13_localidx = p_3Fermi_list[p1].level3.local_index
            p1_parity = p_3Fermi_list[p1].level1.parity
            if p1_parity == "+":
                tmp_string1["p_PPNS="] = p11_localidx
                tmp_string2["p_PPPS="] = p12_localidx
                tmp_string3["p_PPNS="] = p13_localidx
            else:
                tmp_string1["p_NPNS="] = p11_localidx
                tmp_string2["p_NPPS="] = p12_localidx
                tmp_string3["p_NPNS="] = p13_localidx

            for p2 in range(p1+1, len_p):
                p21_localidx = p_3Fermi_list[p2].level1.local_index
                p22_localidx = p_3Fermi_list[p2].level2.local_index
                p23_localidx = p_3Fermi_list[p2].level3.local_index
                p2_parity = p_3Fermi_list[p2].level1.parity
                if p2_parity == "+":
                    tmp_string1["p_PPNS="] = p21_localidx
                    tmp_string2["p_PPPS="] = p22_localidx
                    tmp_string3["p_PPNS="] = p23_localidx
                else:
                    tmp_string1["p_NPNS="] = p21_localidx
                    tmp_string2["p_NPPS="] = p22_localidx
                    tmp_string3["p_NPNS="] = p23_localidx

                replace_sh_command(KEY_NAME, count)
                replace_blocking_levels(tmp_string1, 1)
                replace_blocking_levels(tmp_string2, 2)
                replace_blocking_levels(tmp_string3, 3)
                count += 1

def run_sh_command():
    """1. 执行 "~/wscsm1/run.sh" 脚本
    2. 返回该脚本的进程ID
    """
    import subprocess
    process = subprocess.Popen(["~/wscsm1/run.sh"], shell=True)
    return process.pid


if __name__ == "__main__":
    KEY_NAME = "Ds267-HKpr1n2p"
    proton_num = 110
    neutron_num = 157
    level_range = 7
    out_file_path = "hk.out"

    replace_sh_command(KEY_NAME, 100)
    replace_blocking_levels(blocking_levels, 1)
    replace_blocking_levels(blocking_levels, 2)
    replace_blocking_levels(blocking_levels, 3)
    # 运行测试文件bat
    a = run_sh_command()
    print(f"已启动测试脚本，进程ID: {a}")
    # generate_run(proton_num, neutron_num, file_path, level_range, KEY_NAME)