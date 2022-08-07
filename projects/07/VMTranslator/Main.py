import sys
from Parser import *
from CodeWriter import *
from Constant import *


class Main:
    def __init__(self) -> None:
        self.parser = None
        self.con = Constant()


    def translator(self) -> None:
        while self.parser.has_more_commands():
            self.parser.advance()
            type = self.parser.command_type()
            if type == self.con.C_ARITHMETIC:
                self.write.write_arithmetic(self.parser.current_cmd)
            elif type == self.con.C_PUSH or type == self.con.C_POP:
                self.write.write_push_pop(type, self.parser.args1(), self.parser.args2())
            else:
                print('pass pass')
        self.write.close()

    def main(self) -> None:
        """主程式執行函數"""
        if len(sys.argv) is not 2:
            print('Please enter correct file name')
            return
        fname = sys.argv[1].split('.')[0]
        
        try:
            with open(f'./{fname}.vm', 'r') as in_file:
                self.parser = Parser(in_file.readlines())
                self.write = Code_Writer(fname)
                self.translator()
                    
        except FileNotFoundError:
            print(f'file {sys.argv[1]} was not found')


if __name__ == '__main__':
    Main().main()