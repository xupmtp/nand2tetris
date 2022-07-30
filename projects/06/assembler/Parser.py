class Parser:
    """
    解析指令
    去除空白與註釋
    判斷指令為何種類型
    """
    def __init__(self, file):
        self.current_cmd = ''
        self.current_line = -1
        self.file = self._remove_empty_and_annotation(file)

        self.NOT_CMD = -1
        self.A_CMD = 0
        self.C_CMD = 1
        self.L_CMD = 2


    def has_more_commands(self) -> bool:
        self.current_line += 1
        return len(self.file) > self.current_line


    def advance(self) -> None:
        self.current_cmd = self.file[self.current_line]


    def command_type(self) -> int:
        if '@' in self.current_cmd:
            return self.A_CMD
        elif '=' in self.current_cmd or ';' in self.current_cmd:
            return self.C_CMD
        elif '(' in self.current_cmd and ')' in self.current_cmd:
            return self.L_CMD
        else:
            return self.NOT_CMD


    def symbol(self) -> str:
        """呼叫此函數前須check command_type() = A or L commend"""
        return self.current_cmd.replace('@', '').replace('(', '').replace(')', '')

    
    def dest(self) -> str:
        """呼叫此函數前須check command_type() = C commend"""
        return self._handle_commend()['dest']


    def comp(self) -> str:
        """呼叫此函數前須check command_type() = C commend"""
        return self._handle_commend()['comp']


    def jump(self) -> str:
        """呼叫此函數前須check command_type() = C commend"""
        return self._handle_commend()['jump']


    def _handle_commend(self) -> dict:
        """處理字串 dest=comp;jump"""
        res = {}
        get_dest = self.current_cmd.split('=')
        get_comp = []
        if len(get_dest) == 1:
            res['dest'] = ''
            get_comp = get_dest[0].split(';')
        else:
            res['dest'] = get_dest[0].strip()
            get_comp = get_dest[1].split(';')
        
        res['comp'] = get_comp[0].replace(' ', '')

        if len(get_comp) == 1:
            res['jump'] = ''
        else:
            res['jump'] = get_comp[1].strip()
        
        return res
    

    def _remove_empty_and_annotation(self, file):
        def f_filter(f):
            sp = f.split('//')
            return len(sp[0].strip()) > 0
        

        def f_map(f):
            sp = f.split('//')
            return sp[0].strip()

        
        return list(map(f_map, filter(f_filter, file)))
        