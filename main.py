import os
import sys
import subprocess
import xlrd
import xlwt
from xlwt import *
from xlrd import *
from xlutils.copy import copy
import pandas as pd
import re
# 方法终端输入 SynDT.py
approach = sys.argv[1]
# 文件路径
PDDLFolder =sys.argv[2]
# 结果文件
resultFile =sys.argv[3]
# 游戏类型
gameType = sys.argv[4]
# 方法对应的方法
choice_way = sys.argv[5]

# approach = "SynDS.py"
# PDDLFolder=r'.\domain-new\1.Sub\1.1 Take-away\Take-away-5.pddl'
# resultFile = r".\r.xls"
# gameType = 'normal'  #normal misere
# choice_way = 'Minds2' #InfoGain, Gini

if choice_way == "ID3":
    algorithm_way_type = sys.argv[6]

# For example
# the first method: python main.py Enum.py "domain\1.Sub\1.3 S, D-MarkGame" "result.xls" "normal" "in"

# the second method: python main.py SynDT.py "domain\1.Sub\1.3 S, D-MarkGame" "result.xls" "normal" "ID3" "InfoGain"

# the third method: python main.py SynDT.py "domain\1.Sub\1.3 S, D-MarkGame" "result.xls" "normal" "Incre"

# the fourth method: python main.py SynDT.py "domain\1.Sub\1.3 S, D-MarkGame" "result.xls" "normal" "DT1"

# python main.py SynDS.py "domain_wy\1.Sub" "r.xls" "normal" "Minds2"


PDDLlist = os.listdir(PDDLFolder)
PDDLlist = sorted(PDDLlist,key=None)

def needJump(pddl) :
    name = pddl[:-5]
    # if xls not exist, create new one
    if not os.path.exists(resultFile):
        # also make sure to create a fresh worksheet
        wb = Workbook(encoding='utf-8')
        wb.add_sheet('Sheet 1')
        wb.save(resultFile)

    oldwb = xlrd.open_workbook(resultFile, encoding_override='utf-8')
    sheet1 = oldwb.sheet_by_index(0)
    row = sheet1.nrows - 1                           # 获取最后一行的行索引
    # print(row)
    if row == -1:
        print("不需要跳过")
        return False  #空表， 不需要跳过
    #是否这前已经判断过name了
    df = pd.read_excel(resultFile, header=None)
    if os.path.basename(name) in df.iloc[:,0].values:
        print("该测例之前判断过了")
        return True
    timeString = "" if len(sheet1.row_values(row)) <= 2 else sheet1.row_values(row)[2]
    if re.match(r'^-?\d+\.?\d*$', str(timeString)) and 0 < float(timeString) < 1200:
        print("上一个合成成功，不需要跳过")
        return False
    else:
        print("上一个合成失败")
        fail_game_name = sheet1.row_values(row)[0]
        #名称是否类似
        if  is_one_char_diff(fail_game_name, pddl[:-5]) and "Sub" not in pddl[:-5]:
            # 把名字保存，不执行它了，默认为失败  ##没有把名字写出来
            newwb = copy(oldwb)
            sheet1 = newwb.get_sheet(0)
            sheet1.write(row + 1, 0, pddl[:-5])
            sheet1.write(row + 1, 6, "J-C")
            newwb.save(resultFile)
            print("需要跳过")
            return True
        else:
            print("不需要跳过")
            return False

def is_one_char_diff(str1, str2):
    if len(str1) == len(str2) - 1:
        # str1 比 str2 少一个字符，判断是否只有一个字符不同
        for i in range(len(str1)):
            if str1[i] != str2[i]:
                return str1 == str2[:i] + str2[i+1:]  # 判断是否只有一个字符不同
        return True
    elif len(str2) == len(str1) - 1:
        # str1 比 str2 多一个字符，判断是否只有一个字符不同
        for i in range(len(str2)):
            if str2[i] != str1[i]:
                return str2 == str1[:i] + str1[i+1:]  # 判断是否只有一个字符不同
        return True
    elif len(str1) == len(str2):
        # str1 和 str2 长度相同，判断是否只有一个字符不同
        count_diff = 0  # 不同字符计数器
        for i in range(len(str1)):
            if str1[i] != str2[i]:
                count_diff += 1
                if count_diff > 1:
                    return False  # 不同字符超过一个，直接返回 False
        return count_diff == 1  # 不同字符只有一个，返回 True
    else:
        return False


def go(PDDLlist):
    for pddl in PDDLlist:
        print(pddl)
        try:
            if 'pddl' not in pddl:    #非pddl文件跳过
                continue
            print("测试用例：", pddl)
            if needJump(pddl) == False:
                if choice_way == "Incre" or choice_way == "ID3":
                    subprocess.call("python \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" "%(approach, pddl, resultFile, gameType, choice_way), timeout = 1200)
                else:
                    subprocess.call(("python \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" "%(approach, pddl, resultFile, gameType, choice_way)), timeout = 1200, shell=True)
        except subprocess.TimeoutExpired as e:
            #避免未知的错误导致一直卡着，子程序一直不结束
            print('Error: Subprocess execution timed out:', e)
            continue
        except subprocess.CalledProcessError as e:
            print("Error executing subprocess:", e)
            continue
        except Exception as e:
            print("其他异常: ", e)
            continue

for root, dirs, files in os.walk(PDDLFolder):
    # for file in files:
    #     yield os.path.join(root, file)
    go([os.path.join(root, file) for file in files if 'pddl' in file])
