from Constant import *


class Code_Writer:
    def __init__(self, f_name) -> None:
        self.f_name = f_name
        self.con = Constant()
        self.b_count = 0
        try:
            self.out_file = open(f'./{f_name}.asm', 'w')
        except:
            print('open out file fail')


    def write_arithmetic(self, cmd) -> None:
        def bool_list(goto):
            res = ['D=M-D']
            res.append(f'@BOOL_{self.b_count}_TRUE')
            res.append(goto)
            # bool false
            res.append('D=0')
            res.append(f'@BOOL_{self.b_count}_END')
            res.append('0;JMP')
            res.append(f'(BOOL_{self.b_count}_TRUE)')
            res.append('D=-1')
            res.append(f'(BOOL_{self.b_count}_END)')
            res.append('@SP')
            res.append('M=D')
            return res


        arith_dist = {
            self.con.ADD: ['M=M+D'],
            self.con.SUB: ['M=M-D'],
            self.con.NEG: ['M=-M'],
            self.con.EQ: bool_list('D;JEQ'),
            self.con.GT: bool_list('D;JGT'),
            self.con.LT: bool_list('D;JLT'),
            self.con.AND: ['M=M&D'],
            self.con.OR: ['M=M|D'],
            self.con.NOT: ['M=!M']
        }
        res = ['@SP', 'M=M-1', 'A=M', 'D=M']
        if not self.con.SUB == cmd and not self.con.NOT == cmd:
            res += ['@SP', 'M=M-1', 'A=M']
        res += arith_dist[cmd]
        res += ['@SP', 'M=M+1']
        self.out_file.write('\n'.join(res))
        self.out_file.write('\n')
        self.b_count += 1


    def write_push_pop(self, cmd, segment, index) -> None:
        segment_dist = {
            self.con.LOCAL: '@LCL',
            self.con.ARGUMENT: '@ARG',
            self.con.THAT: '@THAT',
            self.con.THIS: '@THIS',
            self.con.CONSTATNT: f'@{index}',
            self.con.STATIC: f'{self.f_name}.{index}',
            self.con.TEMP: '@R5',
            self.con.POINTER: '@THIS' if index == 0 else '@THAT'
        }


        def _push(addr, i):
            # get segment address位移數字
            push_list = [f'@{i}', 'D=A'] if segment not in 'constant,static' else []
            push_list.append(addr)
            if segment == self.con.TEMP:
                push_list.append('A=A+D')
            elif segment not in 'constant,static':
                push_list.append('A=M+D')
            push_list.append(f'D={"A" if segment == self.con.CONSTATNT else "M"}')
            push_list.append('@SP')
            push_list.append('A=M')
            push_list.append('M=D')
            push_list.append('@SP')
            push_list.append('M=M+1')

            return '\n'.join(push_list)
    

        def _pop(addr, i):
            pop_list = []
            tmp_data = 'D=A+D' if segment == self.con.TEMP else 'D=M+D'
            if self.con.CONSTATNT == segment:
                return ''
            elif self.con.STATIC == segment:
                pop_list = ['@SP', 'M=M-1', 'A=M', 'D=M', addr, 'M=D']
            else:
                # get segment address
                pop_list = [f'@{i}', 'D=A', addr, tmp_data]
                # pop stack and insert to segment address
                pop_list += ['@SP', 'M=M-1', 'A=M', 'D=D+M', 'A=D-M', 'M=D-A']

            return '\n'.join(pop_list)


        i = 0 if self.con.POINTER == segment else index
        if cmd == self.con.C_PUSH:
            self.out_file.write(_push(segment_dist[segment], i))
        elif cmd == self.con.C_POP:
            self.out_file.write(_pop(segment_dist[segment], i))
        else:
            print('push/pop cmd type error')
        self.out_file.write('\n')


    def close(self) -> None:
        self.out_file.write('\n'.join(['(END)', '@END', '0;JMP']))
        self.out_file.close()
