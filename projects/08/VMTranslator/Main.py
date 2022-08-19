import sys
import os
from Parser import *
from CodeWriter import *
from Constant import *


class Main:
    """接續project 7 VMTranslator"""
    def __init__(self) -> None:
        self.parser = None
        self.con = Constant()


    def translator(self) -> None:
        """迭代文件，判斷命令並執行相應函數"""
        cmd_fn = {
            self.con.C_ERROR: lambda _: print('command type error'),
            self.con.C_ARITHMETIC: self.write.write_arithmetic,
            self.con.C_PUSH: self.write.write_push_pop,
            self.con.C_POP: self.write.write_push_pop,
            self.con.C_LABEL: self.write.write_label,
            self.con.C_GOTO: self.write.write_goto,
            self.con.C_IF: self.write.write_if,
            self.con.C_RETURN: self.write.write_return,
            self.con.C_FUNCTION: self.write.write_function,
            self.con.C_CALL: self.write.write_call,
        }

        while self.parser.has_more_commands():
            self.parser.advance()
            type = self.parser.command_type()
            if type == self.con.C_ARITHMETIC:
                self.write.write_arithmetic(self.parser.current_cmd)
            elif type == self.con.C_PUSH or type == self.con.C_POP:
                self.write.write_push_pop(type, self.parser.args1(), self.parser.args2())
            elif type == self.con.C_LABEL:
                self.write.write_label(self.parser.args1())
            elif type == self.con.C_GOTO:
                self.write.write_goto(self.parser.args1())
            elif type == self.con.C_IF:
                self.write.write_if(self.parser.args1())
            elif type == self.con.C_RETURN:
                self.write.write_return()
            elif type == self.con.C_FUNCTION:
                self.write.write_function(self.parser.args1(), self.parser.args2())
            elif type == self.con.C_CALL:
                self.write.write_call(self.parser.args1(), self.parser.args2())
            else:
                print(f'commands type {type} not found')
                continue
            self.write.out_file.write('\n')

    def main(self) -> None:
        """主程式執行函數"""
        if len(sys.argv) is not 2:
            print('Please enter correct file name')
            return
        f_list, arg1, path = [], sys.argv[1], ''

        if arg1.endswith('.vm'):
            f_list = [arg1]
            path = './'
            self.write = Code_Writer(arg1.replace('.vm', ''))
        else:
            f_list = list(filter(lambda f: f.endswith('.vm'), os.listdir(f'../{arg1}')))
            path = f'../{arg1}/'
            self.write = Code_Writer(arg1.split('/')[1])
            self.write.write_init()
        
        for fname in f_list:
            try:
                with open(path + fname, 'r') as in_file:
                    self.parser = Parser(in_file.readlines())
                    self.write.set_file_name(fname.replace('.vm', ''))
                    self.translator()
            except FileNotFoundError:
                print(f'file {path + fname} was not found')
        self.write.close()


if __name__ == '__main__':
    Main().main()