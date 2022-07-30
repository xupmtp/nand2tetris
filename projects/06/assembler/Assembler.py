import sys
from Parser import *
from Code import *
from SymbolTable import *


class Assembler:
    """Assembler，讀取asm file，輸出二進位hack file"""
    def __init__(self, asm_f, out_file) -> None:
        """初始化各module"""
        self.out_file = out_file
        self.file_list = asm_f.readlines()
        self.code = Code()
        self.symbol_table = Symbol_Table()
        


    def first_pass(self):
        """process L_commend"""
        parser = Parser(self.file_list)
        cur_line = 0
        while parser.has_more_commands():
            parser.advance()
            if parser.command_type() == parser.L_CMD:
                self.symbol_table.add_entry(parser.symbol(), cur_line)
            else:
                cur_line += 1


    def second_pass(self):
        """process A_commend and C_commend other pass"""
        # Parser只供遍歷一次，所以重新遍歷要建立新物件
        parser = Parser(self.file_list)
        while parser.has_more_commands():
            parser.advance()
            if parser.command_type() == parser.A_CMD:
                self.out_file.write(self.get_A_CMD_binary(parser.symbol()) + '\n')
            elif parser.command_type() == parser.C_CMD:
                self.out_file.write(self.get_C_CMD_binary(parser) + '\n')
            else:
                continue


    def get_A_CMD_binary(self, symbol: str) -> str:
        """處理A指令回傳16-bits字串"""
        if symbol.isdigit():
            return self.code.decimal_to_binary(symbol)
        elif not self.symbol_table.contains(symbol):
            self.symbol_table.add_new_symbol(symbol)
        
        return self.code.decimal_to_binary(self.symbol_table.get_address(symbol))


    def get_C_CMD_binary(self, parser: Parser) -> str:
        """處理C指令回傳16-bits字串"""
        comp = self.code.comp(parser.comp())
        dest = self.code.dest(parser.dest())
        jump = self.code.jump(parser.jump())


        return f"111{comp}{dest}{jump}"


    def assembling_program(self):
        """assember主程式"""
        self.first_pass()
        self.second_pass()


def main():
    """程式預設執行函數，執行目錄為：{YOUR_PATH}/nand2tetris/"""
    if len(sys.argv) is not 2:
        print('Please enter correct file name')
        return
    fname = sys.argv[1].split('.')[0]
    path = f'./projects/06/{fname[0].lower() + fname[1:].replace("L", "")}'
    
    try:
        with open(f'{path}/{fname}.asm', 'r') as in_file:
            with open(f'{path}/{fname}.hack', 'w') as out_file:
                assembler = Assembler(in_file, out_file)
                assembler.assembling_program()
    except FileNotFoundError:
        print(f'file {sys.argv[1]} was not found')


if __name__ == '__main__':
    main()
