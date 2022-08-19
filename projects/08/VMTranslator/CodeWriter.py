from Constant import *


class Code_Writer:
    """解析命令轉換成assembly code"""
    def __init__(self, out_name) -> None:
        self.f_name = out_name
        self.con = Constant()
        # 區分bool label
        self.b_count = 1
        # 區分return label
        self.r_count = 1
        # 區分label commands
        self.curr_func_name = []
        try:
            self.out_file = open(f'./{out_name}.asm', 'w')
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
        self.write_to_file(res)
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

            return push_list
    

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

            return pop_list


        # 判斷是push pr pop
        if cmd == self.con.C_PUSH:
            self.write_to_file(_push(segment_dist[segment], index))
        elif cmd == self.con.C_POP:
            self.write_to_file(_pop(segment_dist[segment], index))
        else:
            print('push/pop cmd type error')


    def set_file_name(self, f_name: str) -> None:
        self.f_name = f_name


    def write_init(self) -> None:
        self.write_call('Sys.init', '0')


    def write_label(self, label: str) -> None:
        """create a new label"""
        self.out_file.write(f'({self._get_curr_fn(label)})')


    def write_goto(self, label: str) -> None:
        """jump to label"""
        self.write_to_file([f'@{self._get_curr_fn(label)}', '0;JMP'])


    def write_if(self, label: str) -> None:
        """if stack pop() != 0 : jump to label"""
        self.write_to_file(['@SP', 'M=M-1', 'A=M', 'D=M', f'@{self._get_curr_fn(label)}', 'D;JNE'])


    def write_function(self, fn_name: str, num_vars: str) -> None:
        # for label命名時紀錄當前function name
        self.curr_func_name.append(fn_name)
        assembly = [f'({fn_name})']
        if int(num_vars) > 0:
            assembly += ['@LCL', 'A=M', 'M=0'] + sum([['A=A+1', 'M=0'] for i in range(int(num_vars) - 1)], [])
        self.write_to_file(assembly)


    def write_call(self, fn_name: str, num_args: int) -> None:
        # save "return LCL ARG THIS THAT" address to stack
        res = [f'@{self.f_name}$ret.{self.r_count}', 'D=A', '@SP', 'A=M', 'M=D']
        res += ['@LCL', 'D=A', '@SP', 'AM=M+1', 'M=D']
        res += ['@ARG', 'D=A', '@SP', 'AM=M+1', 'M=D']
        res += ['@THIS', 'D=A', '@SP', 'AM=M+1', 'M=D']
        res += ['@THAT', 'D=A', '@SP', 'AM=M+1', 'M=D', '@SP', 'M=M+1']
        # ARG = SP-5-num_args
        res += ['@5', 'D=A', f'@{num_args}', 'D=D+A', '@SP', 'D=M-D', '@ARG', 'M=D']
        # LCL = SP
        res += ['@SP', 'D=M', '@LCL', 'M=D']
        # go to function label and create return label
        res += [f'@{fn_name}', '0;JMP', f'({self.f_name}$ret.{self.r_count})']

        self.write_to_file(res)
        self.r_count += 1


    def write_return(self) -> None:
        # for label命名時紀錄當前function name
        self.curr_func_name.pop()
        # 設變數endFrame=LCL
        res = ['@LCL', 'D=M', '@endFrame', 'M=D']
        # 設變數retAddr=return address *(LCL-5)
        res += ['@5', 'A=D-A', 'D=M', '@retAddr', 'M=D']
        # SP pop(return value) and push to ARG 0
        res += ['@SP', 'AM=M-1', 'D=M', '@ARG', 'A=M', 'M=D']
        # SP = ARG+1
        res += ['D=A+1', '@SP', 'M=D']
        # 回復 "THAT THIS ARG LCL"儲存address到上一層函數的值
        res += ['@endFrame', 'AM=M-1', 'D=M', '@THAT', 'M=D']
        res += ['@endFrame', 'AM=M-1', 'D=M', '@THIS', 'M=D']
        res += ['@endFrame', 'AM=M-1', 'D=M', '@ARG', 'M=D']
        res += ['@endFrame', 'AM=M-1', 'D=M', '@LCL', 'M=D']
        # jump to return label address
        res += ['@retAddr', 'A=D', '0;JMP']

        self.write_to_file(res)


    def close(self) -> None:
        self.out_file.close()


    def _get_curr_fn(self, label):
        # 若label在function內定義 需命名為"f_name:label"，便於區分不同function中相同名稱的label
        if len(self.curr_func_name) > 0:
            return f'{self.curr_func_name[-1]}:{label}'
        return label


    def write_to_file(self, assembly_list: list) -> None:
        self.out_file.write('\n'.join(assembly_list))
