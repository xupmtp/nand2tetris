from Constant import *
from TokenizerExcept import *
import re


class JackTokenizer:
    def __init__(self, input_stream) -> None:
        self.file = input_stream
        # 當前token
        self.token = None
        self.cur_idx = 0

    def next(self) -> bool:
        if self.hasMoreTokens():
            self.advance()
            return True
        elif self.token is not '}':
            raise TokenizerExcept('End of file is not "}"')

    def hasMoreTokens(self) -> bool:
        return len(self.file) > self.cur_idx + 1

    def advance(self) -> None:
        i, token = self.processAdvance()
        self.cur_idx = i
        self.token = token

    def checkNext(self) -> str:
        """只檢查不往前"""
        i, token = self.processAdvance()
        if self.hasMoreTokens():
            return token
        return ''

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
        return keyword[self.token]

    def symbol(self) -> str:
        if self.token == symbol['<']:
            return '&lt;'
        elif self.token == symbol['>']:
            return '&gt;'
        elif self.token == symbol['&']:
            return '&amp;'
        return symbol[self.token]

    def identifier(self) -> str:
        return self.token

    def intVal(self) -> int:
        return self.token

    def stringVal(self) -> str:
        return self.token.replace('"', '')

    # 只處理不實際前進
    def processAdvance(self) -> tuple:
        start = i = self.cur_idx

        while self.file[i] == ' ':
            start += 1
            i += 1

        # symbol
        if self.file[i] in symbol:
            return i + 1, self.file[i]

        # string
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
        return i, self.file[start: i]

    def isStatment(self) -> bool:
        return self.checkKeyword(['let', 'do', 'if', 'while', 'return'])

    def checkTokenType(self, type):
        return self.tokenType() == tokenType[type]

    def isType(self) -> bool:
        return self.checkKeyword(['int', 'char', 'boolean', 'void']) or self.checkTokenType('identifier')

    def isOp(self, token=None) -> bool:
        if token == None:
            return self.checkSymbol(['+', '-', '*', '/', '&', '|', '<', '>', '='])
        else:
            return token in ['+', '-', '*', '/', '&', '|', '<', '>', '=']

    def checkKeyword(self, words):
        return self.checkTokenType('keyword') and self.token in words

    def checkSymbol(self, symbols):
        return self.checkTokenType('symbol') and self.token in symbols
