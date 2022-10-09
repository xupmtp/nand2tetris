import sys
import os
import re


class JackAnalyzer:
    def __init__(self) -> None:
        pass


    def main(self):
        """主程式執行函數"""
        if len(sys.argv) is not 2:
            print('Please enter correct file name')
            return
        f_list, arg1, path = [], sys.argv[1], ''
        # 判斷目錄or檔案
        if arg1.endswith('.jack'):
            f_list = [arg1]
            path = './'
        else:
            f_list = list(filter(lambda f: f.endswith('.jack'), os.listdir(f'../{arg1}')))
            path = f'../{arg1}/'

        # 讀取每筆檔案
        for f_name in f_list:
            try:
                with open(path + f_name, 'r') as file:
                    print(file.readlines())
            except FileNotFoundError:
                print(f'file {path + f_name} was not found')


    # 刪除註解&空白行
    def _remove_empty_and_annotation(self, file):
        flag = True
        def f_filter(f):
            nonlocal flag
            se = re.search("(/\*\*|/{2})+", f)
            if se == None:
                return True
            gp = se.group()

            sp = f.split('//')
            return flag and len(sp[0].strip()) > 0
        

        def f_map(f):
            sp = f.split('//')
            return sp[0].strip()

        
        return list(map(f_map, filter(f_filter, file)))


if __name__ == '__main__':
    JackAnalyzer().main()