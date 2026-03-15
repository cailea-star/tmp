from level_select import match_neutron_levels, match_proton_levels



if __name__ == "__main__":
    proton_num = 110
    neutron_num = 157

    level_range = 7
    file_path = "hk-z110-110-n158-158-Ds267-prolate.out"
    match_neutron_levels(proton_num, neutron_num, file_path, level_range, is_manual_selection=False)
    match_proton_levels(proton_num, neutron_num, file_path, level_range, is_manual_selection=False)

    