from Constant import *


class Code_Writer:
    """解析命令轉換成assembly code"""
    def __init__(self, f_name) -> None:
        self.f_name = f_name
        self.con = Constant()
        self.b_count = 0
        try:
            self.out_file = open(f'./{f_name}.asm', 'w')
        except:
            print('open out file fail')


    def write_arithmetic(self, cmd) -> None:
        """邏輯&運算命令處理"""
        def bool_list(goto):
            # 判斷bool值跳往哪
            res = ['D=M-D', f'@BOOL_{self.b_count}_TRUE', goto]
            # bool false
            res += ['D=0', f'@BOOL_{self.b_count}_END', '0;JMP']
            # bool true
            res += [f'(BOOL_{self.b_count}_TRUE)', 'D=-1']
            # end and set to stack
            res += [f'(BOOL_{self.b_count}_END)', '@SP', 'A=M', 'M=D']
            return res

        # 邏輯/運算命令dist
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
        # pop y
        res = ['@SP', 'M=M-1', 'A=M', 'D=M']
        # 如果需要2個值運算時，pop x
        if not self.con.NEG == cmd and not self.con.NOT == cmd:
            res += ['@SP', 'M=M-1', 'A=M']
        # 邏輯/運算命令
        res += arith_dist[cmd]
        # stack++
        res += ['@SP', 'M=M+1']
        self.out_file.write('\n'.join(res))
        self.out_file.write('\n')
        self.b_count += 1


    def write_push_pop(self, cmd, segment, index) -> None:
        """處理push/pop命令，分2個子函數處理"""
        # segment轉assembly code
        segment_dist = {
            self.con.LOCAL: '@LCL',
            self.con.ARGUMENT: '@ARG',
            self.con.THAT: '@THAT',
            self.con.THIS: '@THIS',
            self.con.CONSTATNT: f'@{index}',
            self.con.STATIC: f'@{self.f_name}.{index}',
            self.con.TEMP: '@R5',
            # pointer指令是 push/pop @THIS/@THAT的值，而不是一般將@THIS/@THAT作為索引操作其他地址
            self.con.POINTER: '@THIS' if int(index) == 0 else '@THAT'
        }


        def _push(addr, i):
            push_list = []
            # 1. 取得segment address儲存的值
            if segment == self.con.CONSTATNT:
                push_list = [addr, 'D=A']
            elif segment in ',static,pointer':
                push_list = [addr, 'D=M']
            else:
                tmp_data = 'A=A+D' if segment == self.con.TEMP else 'A=M+D'
                push_list = [f'@{i}', 'D=A', addr, tmp_data, 'D=M']

            # push值到stack and stack++
            push_list += ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']

            return '\n'.join(push_list)
    

        def _pop(addr, i):
            pop_list = []
            # 正常pop不會有CONSTATNT，防止意外命令
            if self.con.CONSTATNT == segment:
                return ''
            # static和pointer的index段用於address處理，故不需加入@i
            elif self.con.STATIC == segment or self.con.POINTER == segment:
                pop_list = ['@SP', 'M=M-1', 'A=M', 'D=M', addr, 'M=D']
            else:
                tmp_data = 'D=A+D' if segment == self.con.TEMP else 'D=M+D'
                # segment address = segmentPointer + i
                pop_list = [f'@{i}', 'D=A', addr, tmp_data]
                # pop stack and insert to segment address
                pop_list += ['@SP', 'M=M-1', 'A=M', 'D=D+M', 'A=D-M', 'M=D-A']

            return '\n'.join(pop_list)


        # 判斷是push pr pop
        if cmd == self.con.C_PUSH:
            self.out_file.write(_push(segment_dist[segment], index))
        elif cmd == self.con.C_POP:
            self.out_file.write(_pop(segment_dist[segment], index))
        else:
            print('push/pop cmd type error')
        self.out_file.write('\n')


    def set_file_name(f_name: str) -> None:
        pass


    def write_init() -> None:
        pass


    def write_label(label: str) -> None:
        """create a new label"""
        return f'({label})'


    def write_goto(label: str) -> None:
        """jump to label"""
        return '\n'.join([f'@{label}', '0;JMP'])


    def write_if(label: str) -> None:
        """if stack pop() == true : jump to label"""
        '\n'.join(['@SP', 'M=M-1', 'A=M', 'D=M', f'@{label}', 'D;JLT'])


    def write_function(fn_name: str, num_vars: int) -> None:
        pass


    def write_call(fn_name: str, num_args: int) -> None:
        pass


    def write_return() -> None:
        pass


    def close(self) -> None:
        self.out_file.close()
