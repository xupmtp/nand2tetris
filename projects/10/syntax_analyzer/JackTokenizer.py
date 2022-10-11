from curses.ascii import isdigit
from Constant import *
import re


class JackTokenizer:
    def __init__(self, input_stream) -> None:
        self.file = input_stream
        # 當前token
        self.token = None
        self.cur_idx = 0


    def hasMoreTokens(self) -> bool:
        return len(self.file) > self.cur_idx + 1


    def advance(self) -> None:
        i = self.cur_idx

        while self.file[i] == ' ':
            i += 1
        self.cur_idx = i
        
        # symbol
        if self.file[i] in symbol:
            self.token = self.file[i]
            self.cur_idx += 1
            return

        #string
        if self.file[i] == '"':
            i += 1
            while self.file[i] != '"':
                i += 1
            i += 1
        else:
            # keyword, int string Constant, identifier
            while self.file[i] != ' ' and self.file[i] not in symbol:
                i += 1
        # 最後一個字符正常是 '}' symbol 所以不必擔心index out
        self.token = self.file[self.cur_idx: i]
        self.cur_idx = i


    def tokenType(self) -> str:
        if self.token in keyword:
            return tokenType['keyword']
        elif self.token in symbol:
            return tokenType['symbol']
        elif self.token.isdigit():
            return tokenType['intConst']
        elif re.search('^".*"$', self.token) != None:
            return tokenType['strConst']
        else:
            return tokenType['identifier']


    def keyWord(self) -> str:
        return f"<keyword> {keyword[self.token]} </keyword>"


    def symbol(self) -> str:
        return f"<symbol> {symbol[self.token]} </symbol>"


    def identifier(self) -> str:
        return f"<identifier> {self.token} </idenetifier>"


    def intVal(self) -> int:
        return f"<integerConstant> {self.token} </integerConstant>"


    def stringVal(self) -> str:
        return f"<stringConstant> {self.token.replace('\"', '')} </stringConstant>"
    