class Code:
    dest = ['', 'M', 'D', 'MD', 'A', 'AM', 'AD', 'AMD']
    jump = ['', 'JGT', 'JEQ', 'JGE', 'JLT', 'JNE', 'JLE', 'JMP']
    comp = {
        '0': '101010', '1': '111111', '-1': '111010',
        'D': '001100', 'A': '110000', '!D': '001101', 
        '!A': '110001', '-D': '001111', '-A': '110011',
        'D+1': '011111', 'A+1': '110111', 'D-1': '01110',
        'A-1': '110010', 'D+A': '000010', 'D-A': '010011',
        'A-D': '000111', 'D&A': '000000', 'D|A': '010101'
    }

    def __init__(self) -> None:
        pass


    def dest(self, mnemonic: str) -> str:
        bit = self.dest.find(mnemonic.strip())
        if bit == -1:
            print('convert dest error')
            return '000'
        return bin(bit)[2:].rjust(3, '0')
    

    def jump(self, mnemonic: str) -> str:
        bit = self.jump.find(mnemonic.strip())
        if bit == -1:
            print('convert jump error')
            return '000'
        return bin(bit)[2:].rjust(3, '0')
    

    def comp(self, mnemonic: str) -> str:
        # 第一位,決定M or A
        a = '0'
        # 替換M位成A位
        if 'M' in mnemonic:
            mnemonic = mnemonic.replace('M', 'A')
            a = '1'
        if mnemonic not in self.comp:
            print('convert comp error')
            return '0000000'
        return a + self.comp[mnemonic]


