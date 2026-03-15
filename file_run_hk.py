from level_select import n_Fermi_ThreeLevelList, p_Fermi_ThreeLevelList

KEY_WORDs = ["if [ $ind -eq 1 ]; then", 
             "if [ $ind -eq 2 ]; then", 
             "if [ $ind -eq 3 ]; then"]


blocking_levels = {
    "n_NPNS=":0,
    "n_PPPS=":0,
    "n_PPNS=":0,
    "p_NPPS=":0,
    "p_NPNS=":0,
    "p_PPPS=":0,
    "p_PPNS=":0
}


def replace_blocking_levels(blocking_levels, index, file_path="run.hk"):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        KEY_LINEs = []
        for i, line in enumerate(lines):
            if line.strip() in KEY_WORDs:
                KEY_LINEs.append(i)
        readed = [False, False, False]
        for i, line in enumerate(lines):
            if i >= KEY_LINEs[0]:
                readed[0] = True
            if i >= KEY_LINEs[1]:
                readed[1] = True
            if i >= KEY_LINEs[2]:
                readed[2] = True
            
            if index == 1:
                if readed[0] and (not readed[1]):
                    