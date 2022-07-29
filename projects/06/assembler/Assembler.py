import sys
from Parser import *
from Code import *
from SymbolTable import *


class Assembler:
    def __init__(self, asm_f, hack_f) -> None:
        self.hack_f = hack_f
        self.parser = Parser([f.strip() for f in asm_f.readlines()])
        self.code = Code()
        self.symbol_table = Symbol_Table()


    def first_pass(self):
        pass


    def second_pass(self):
        pass



def main():
    if len(sys.argv) is not 2:
        print('Please enter correct file name')
        return
    file_name = sys.argv[1].split('.')[0]
    
    try:
        with open(f'./projects/06/assembler/{sys.argv[1]}', 'r') as in_file:
            with open(f'{file_name}.hack', 'w') as out_file:
                assembler = Assembler(in_file, out_file)
    except FileNotFoundError:
        print(f'file {sys.argv[1]} was not found')


if __name__ == '__main__':
    main()
