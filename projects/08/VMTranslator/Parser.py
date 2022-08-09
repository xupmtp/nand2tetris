from Constant import *


class Parser:
    current_cmd = ''
    current_line = -1
    constant = Constant()
    cmd_type = {
        'error': constant.C_ERROR,
        'arithmetic': constant.C_ARITHMETIC,
        'push': constant.C_PUSH,
        'pop': constant.C_POP,
        'label': constant.C_LABEL,
        'goto': constant.C_GOTO,
        'if-goto': constant.C_IF,
        'return': constant.C_RETURN,
        'function': constant.C_FUNCTION,
        'call': constant.C_CALL
    }
    
    def __init__(self, in_file) -> None:
        self.file = self._remove_empty_and_annotation(in_file)


    def has_more_commands(self) -> bool:
        self.current_line += 1
        return len(self.file) > self.current_line


    def advance(self) -> None:
        self.current_cmd = self.file[self.current_line]


    def command_type(self) -> int:
        cmd_list = self.current_cmd.split()
        cmd0 = cmd_list[0].lower()
        if len(cmd_list) == 1 and cmd0 not in self.cmd_type:
            return self.constant.C_ARITHMETIC
        elif cmd0 in self.cmd_type:
            return self.cmd_type[cmd0]
        else:
            return self.constant.C_ERROR


    def args1(self) -> str:
        """命令為C_RETURN時不該調用此函數"""
        cmd_list = self.current_cmd.split()
        if len(cmd_list) == 1 and self.command_type() == self.constant.C_ARITHMETIC:
            return cmd_list[0]
        else:
            return cmd_list[1]


    def args2(self) -> str:
        """只有當command為PUSH, POP, FUNCTION, CALL時才應調用"""
        cmd_list = self.current_cmd.split()
        if len(cmd_list) > 2:
            return cmd_list[2]
        print('get args2 error', cmd_list)
        return ''


    def _remove_empty_and_annotation(self, file):
        def f_filter(f):
            sp = f.split('//')
            return len(sp[0].strip()) > 0
        

        def f_map(f):
            sp = f.split('//')
            return sp[0].strip()

        
        return list(map(f_map, filter(f_filter, file)))
 