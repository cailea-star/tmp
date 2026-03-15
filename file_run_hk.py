from level_select import n_Fermi_ThreeLevelList, p_Fermi_ThreeLevelList

blocking_levels = [
    "n_NPNS=0",
    "n_PPPS=0",
    "n_PPNS=0",
    "p_NPPS=0",
    "p_NPNS=0",
    "p_PPPS=0",
    "p_PPNS=0"
]

if __name__ == "__main__":
    proton_num = 110
    neutron_num = 157

    level_range = 7
    file_path = "hk-z110-110-n158-158-Ds267-prolate.out"
    n_3Fermi_list = n_Fermi_ThreeLevelList(proton_num, neutron_num, file_path, level_range, is_manual_selection=False)
    p_3Fermi_list = p_Fermi_ThreeLevelList(proton_num, neutron_num, file_path, level_range, is_manual_selection=False)

    len_n = len(n_3Fermi_list)
    len_p = len(p_3Fermi_list)

    for p1 in range(len_p):
        for p2 in range(p1+1, len_p):
            for n1 in range(len_n):
                pass