import sys
import os
import re
from Constant import *
from CompilationEngine import *


class JackAnalyzer:
    def __init__(self) -> None:
        self.complier = None


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
            f_name = f_name.replace('.jack', '')
            try:
                with open(f"{path + f_name}.jack", 'r') as r_file, open(f"{path + f_name}.xml", 'w') as w_file:
                    self.complier = CompilationEngine(self._file_filter(r_file.readlines()), w_file)
                    self.complier.CompileClass()
            except FileNotFoundError:
                print(f'file {path + f_name} was not found')


    # 刪除註解&空白行 換行符轉空格
    def _file_filter(self, file):
        res = []
        flag = False
        for f in file:
            f = f.strip()
            if flag or not f:
                if '*/' in f:
                    flag = False
                continue

            se = re.search("(/\*|/{2})+", f)
            if se == None:
                res.append(f)
                continue

            gp = se.group()
            if gp == '//' and not f.startswith('//'):
                res.append(f.split('//')[0].strip())
            elif gp == '/*':
                if '*/' in f:
                    f = re.sub('/\*.*\*/', '', f)
                    if len(f) > 0:
                        res.append(f)
                else:
                    flag = True        
                
        return ' '.join(res)
        

if __name__ == '__main__':
    JackAnalyzer().main()