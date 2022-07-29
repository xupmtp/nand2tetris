class Parser:
    def __init__(self, file):
        self.current_cmd = ''
        self.current_line = 0
        self.file = file
        self.cmd_type = {
            'not_commend': -1,
            'A_commend': 0,
            'C_commend': 1,
            'L_commend': 2
        }


    def has_more_commands(self) -> bool:
        return len(list) > self.current_line + 1


    def advance(self) -> None:
        self.current_line += 1
        self.current_cmd = self.file[self.current_line]


    def command_type(self) -> int:
        if '@' in self.current_cmd:
            return self.cmd_type['A_commend']
        elif '=' in self.current_cmd or ';' in self.current_cmd:
            return self.cmd_type['C_commend']
        elif '(' in self.current_cmd and ')' in self.current_cmd:
            return self.cmd_type['L_commend']
        else:
            return self.cmd_type['not_commend']


    def symbol(self) -> str:
        """呼叫此函數前須check command_type() = A or L commend"""
        return self.current_cmd.replace('@', '').replace('(', '').replace(')', '')

    
    def dest(self) -> str:
        """呼叫此函數前須check command_type() = C commend"""
        return self._handle_commend['dest']


    def comp(self) -> str:
        """呼叫此函數前須check command_type() = C commend"""
        return self._handle_commend['comp']


    def jump(self) -> str:
        """呼叫此函數前須check command_type() = C commend"""
        return self._handle_commend['jump']


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