import sys
from Parser import *
from CodeWriter import *


class Main:
    def __init__(self) -> None:
        self.parser = None


    def translator(self) -> None:
        """主程式執行函數"""
        if len(sys.argv) is not 2:
            print('Please enter correct file name')
            return
        fname = sys.argv[1].split('.')[0]
        
        try:
            with open(f'./{fname}.vm', 'r') as in_file:
                self.parser = Parser(in_file.readlines())
                    
        except FileNotFoundError:
            print(f'file {sys.argv[1]} was not found')




if __name__ == '__main__':
    Main().translator()