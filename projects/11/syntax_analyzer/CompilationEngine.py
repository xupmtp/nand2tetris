from JackTokenizer import *
from TokenizerExcept import *
from SymbolTable import *
from VMWriter import *


class CompilationEngine:
    """ 
    每隻function註解為該語法結構
    'xxx' 表示 xxx是keyword或symbol
    x? 表示 x 出現 0 次或 1 次
    x* 表示 x 出現 1 次或 多次

    一般函數結尾時停留在最後已處理的token
    部分因結尾出現次數不定所以會往前一步,註記如下
    CompileExpression()
    compileIf()
    """

    def __init__(self, in_stream, out_stream) -> None:
        self.tokenizer = JackTokenizer(in_stream)
        self.table = SymbolTable()
        self.out = out_stream
        self.writer = VMWriter(out_stream)

    def CompileClass(self) -> None:
        """ 'class' className '{' classVarDec* subroutineDec* '}' """

        # 只有CompileClass() 開始時須取得當前token, 其他呼叫時便已是該Compiler的token
        self.tokenizer.next()
        if not self.tokenizer.checkKeyword(keyword['class']):
            raise TokenizerExcept('class keyword not found')

        self.out.write('<class>\n')
        tab_size = 1
        self.writeTerminalsXML(tab_size)

        # class name
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('class name not found')

        # '{'
        if self._tokenParse('symbol', tab_size, '{'):
            raise TokenizerExcept('class symbol \"{\" not found')

        while self.tokenizer.next() and self.tokenizer.checkTokenType('keyword'):
            k = self.tokenizer.keyWord()
            if k in ['static', 'field']:
                self.CompileClassVarDec(tab_size)
            elif k in ['constructor', 'function', 'method']:
                self.CompileSubroutine(tab_size)

        # while解析失敗才到這(已call next), 必定是 '}'
        if self.tokenizer.checkTokenType('symbol'):
            self.writeTerminalsXML(tab_size)
        else:
            raise TokenizerExcept('class symbol "}" not found')

        self.out.write('</class>\n')

    def CompileClassVarDec(self, tab_size) -> None:
        """ ('static' | 'field' ) type varName (',' varName)* ';' """
        self._processVarName(tab_size, 'classVarDec')

    def CompileSubroutine(self, tab_size) -> None:
        """ ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody """
        self.out.write(self._getTabStr(tab_size) + '<subroutineDec>\n')
        tab_size += 1
        # 'constructor' | 'function' | 'method'
        self.writeTerminalsXML(tab_size)

        # ('void' | type)
        if self.tokenizer.next() and self.tokenizer.isType():
            self.writeTerminalsXML(tab_size)
        else:
            raise TokenizerExcept('Subroutine type not found')

        # subroutineName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('Subroutine subroutineName not found')

        # '('
        if self._tokenParse('symbol', tab_size, '('):
            raise TokenizerExcept('Subroutine "(" not found')

        # parameterList
        self.compileParameterList(tab_size)

        # 不管compileParameterList()有沒有值, 下個token必為 ')'
        if self._tokenParse('symbol', tab_size, ')'):
            raise TokenizerExcept('Subroutine ")" not found')

        self.tokenizer.next()
        if self.tokenizer.checkSymbol('{'):
            self.ComplieSubroutineBody(tab_size)
        else:
            raise TokenizerExcept('Subroutine "{" not found')

        self.out.write(self._getTabStr(tab_size - 1) + '</subroutineDec>\n')

    def ComplieSubroutineBody(self, tab_size):
        """ '{' varDec* statements '}' """
        self.out.write(self._getTabStr(tab_size) + '<subroutineBody>\n')
        tab_size += 1
        self.writeTerminalsXML(tab_size)

        # varDec*
        while self.tokenizer.checkNext() == keyword['var']:
            self.tokenizer.next()
            self.compileVarDec(tab_size)

        # statements
        if self.tokenizer.checkNext() in ['let', 'do', 'if', 'while', 'return']:
            self.compileStatements(tab_size)

        # '}'
        if self._tokenParse('symbol', tab_size, '}'):
            raise TokenizerExcept('Subroutine "}" not found')

        self.out.write(self._getTabStr(tab_size - 1) + '</subroutineBody>\n')

    def compileParameterList(self, tab_size) -> None:
        """ ((type varName) (',' type varName)*)? """
        self.out.write(self._getTabStr(tab_size) + '<parameterList>\n')

        if self.tokenizer.checkNext() == symbol[')']:
            self.out.write(self._getTabStr(tab_size) + '</parameterList>\n')
            return

        tab_size += 1
        self.tokenizer.next()
        # type
        if self.tokenizer.isType() or self.tokenizer.checkTokenType('identifier'):
            self.writeTerminalsXML(tab_size)
        else:
            raise TokenizerExcept('ParameterList type not found')

        # varName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('ParameterList varName not found')

        # (',' varName)* 最後會前進到 ')'停止
        while self.tokenizer.checkNext() == symbol[',']:
            self.tokenizer.next()
            self.writeTerminalsXML(tab_size)
            # type
            if self.tokenizer.next() and (self.tokenizer.isType() or self.tokenizer.checkTokenType('identifier')):
                self.writeTerminalsXML(tab_size)
            else:
                raise TokenizerExcept('ParameterList type not found')
            # varName
            if self._tokenParse('identifier', tab_size):
                raise TokenizerExcept('ParameterList varName not found')

        self.out.write(self._getTabStr(tab_size - 1) + '</parameterList>\n')

    def compileVarDec(self, tab_size) -> None:
        """  'var' type varName (',' varName)* ';' """
        self._processVarName(tab_size, 'varDec')

    def compileStatements(self, tab_size) -> None:
        """ ( letStatement | ifStatement | whileStatement | doStatement | returnStatement )* """
        self.out.write(self._getTabStr(tab_size) + '<statements>\n')
        tab_size += 1

        # Statements可能為空 所以用checkNext
        while self.tokenizer.checkNext() in ['let', 'do', 'if', 'while', 'return']:
            # 第一次進來已有token
            self.tokenizer.next()
            if self.tokenizer.checkKeyword('let'):
                self.compileLet(tab_size)
            elif self.tokenizer.checkKeyword('if'):
                self.compileIf(tab_size)
            elif self.tokenizer.checkKeyword('while'):
                self.compileWhile(tab_size)
            elif self.tokenizer.checkKeyword('do'):
                self.compileDo(tab_size)
            elif self.tokenizer.checkKeyword('return'):
                self.compileReturn(tab_size)
            else:
                break

        self.out.write(self._getTabStr(tab_size - 1) + '</statements>\n')

    def compileDo(self, tab_size) -> None:
        """ 'do' subroutineCall ';' """
        self.out.write(self._getTabStr(tab_size) + '<doStatement>\n')
        tab_size += 1
        self.writeTerminalsXML(tab_size)
        self.tokenizer.next()
        if self.tokenizer.checkTokenType('identifier'):
            self._ComplieSubroutineCall(tab_size)
        else:
            raise TokenizerExcept('compileDo subroutineCall not found')

        if self._tokenParse('symbol', tab_size, ';'):
            raise TokenizerExcept('compileDo ";" not found')

        self.out.write(self._getTabStr(tab_size - 1) + '</doStatement>\n')

    def compileLet(self, tab_size) -> None:
        """ 'let' varName ('[' expression ']')? '=' expression ';' """
        self.out.write(self._getTabStr(tab_size) + '<letStatement>\n')
        tab_size += 1
        self.writeTerminalsXML(tab_size)

        # varName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('compileLet varName not found')

        self.tokenizer.next()
        # ('[' expression ']')?
        if self.tokenizer.checkSymbol('['):
            self.writeTerminalsXML(tab_size)
            self.tokenizer.next()
            self.CompileExpression(tab_size)
            if self._tokenParse('symbol', tab_size, ']'):
                raise TokenizerExcept('compileLet "]" not found')
            else:
                self.tokenizer.next()

        # '='
        if self.tokenizer.checkSymbol('='):
            self.writeTerminalsXML(tab_size)
        else:
            raise TokenizerExcept('compileLet "=" not found')

        # expression
        self.tokenizer.next()
        self.CompileExpression(tab_size)

        # ';'
        if self._tokenParse('symbol', tab_size, ';'):
            raise TokenizerExcept('compileLet ";" not found')

        self.out.write(self._getTabStr(tab_size - 1) + '</letStatement>\n')

    def compileWhile(self, tab_size) -> None:
        """ 'while' '(' expression ')' '{' statements '}' """
        self.out.write(self._getTabStr(tab_size) + '<whileStatement>\n')
        tab_size += 1
        self.writeTerminalsXML(tab_size)
        # '('
        if self._tokenParse('symbol', tab_size, '('):
            raise TokenizerExcept('compileWhile "(" not found')

        # expression
        self.tokenizer.next()
        self.CompileExpression(tab_size)

        # ')'
        if self._tokenParse('symbol', tab_size, ')'):
            raise TokenizerExcept('compileWhile ")" not found')

        # '{'
        if self._tokenParse('symbol', tab_size, '{'):
            raise TokenizerExcept('compileWhile "{" not found')

        # statements
        self.compileStatements(tab_size)

        # '}'
        if self._tokenParse('symbol', tab_size, '}'):
            raise TokenizerExcept('compileWhile "}" not found')

        self.out.write(self._getTabStr(tab_size - 1) + '</whileStatement>\n')

    def compileReturn(self, tab_size) -> None:
        """ 'return' expression? ';’ """
        self.out.write(self._getTabStr(tab_size) + '<returnStatement>\n')
        tab_size += 1
        self.writeTerminalsXML(tab_size)

        # expression
        self.tokenizer.next()
        if not self.tokenizer.checkSymbol(';'):
            self.CompileExpression(tab_size)
            self.tokenizer.next()

        # ';'
        if self.tokenizer.checkSymbol(';'):
            self.writeTerminalsXML(tab_size)
        else:
            raise TokenizerExcept('compileReturn ";" not found')

        self.out.write(self._getTabStr(tab_size - 1) + '</returnStatement>\n')

    def compileIf(self, tab_size) -> None:
        """ 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )? """
        self.out.write(self._getTabStr(tab_size) + '<ifStatement>\n')
        tab_size += 1
        self.writeTerminalsXML(tab_size)

        if self._tokenParse('symbol', tab_size, '('):
            raise TokenizerExcept('compileIf "(" not found')

        # expression
        self.tokenizer.next()
        self.CompileExpression(tab_size)

        # ')'
        if self._tokenParse('symbol', tab_size, ')'):
            raise TokenizerExcept('compileReturn ")" not found')

        # '{'
        if self._tokenParse('symbol', tab_size, '{'):
            raise TokenizerExcept('compileIf if "{" not found')

        # statements
        self.compileStatements(tab_size)

        # '}'
        if self._tokenParse('symbol', tab_size, '}'):
            raise TokenizerExcept('compileIf if "{" not found')

        # ( 'else' '{' statements '}' )?
        if self.tokenizer.checkNext() == keyword['else']:
            if self._tokenParse('keyword', tab_size):
                raise TokenizerExcept('compileIf else not found')

            # '{'
            if self._tokenParse('symbol', tab_size, '{'):
                raise TokenizerExcept('compileIf else "{" not found')

            # statements
            self.compileStatements(tab_size)

            # '}'
            if self._tokenParse('symbol', tab_size, '}'):
                raise TokenizerExcept('compileIf else "}" not found')

        self.out.write(self._getTabStr(tab_size - 1) + '</ifStatement>\n')

    def CompileExpression(self, tab_size) -> None:
        """ term (op term)* """
        self.out.write(self._getTabStr(tab_size) + '<expression>\n')
        tab_size += 1
        self.CompileTerm(tab_size)

        # (op term)*
        while self.tokenizer.isOp(self.tokenizer.checkNext()):
            # op
            if self._tokenParse('symbol', tab_size, self.tokenizer.checkNext()):
                raise TokenizerExcept('CompileExpression op not found')

            # term
            self.tokenizer.next()
            self.CompileTerm(tab_size)

        self.out.write(self._getTabStr(tab_size - 1) + '</expression>\n')

    def CompileTerm(self, tab_size) -> None:
        """ integerConstant | stringConstant | keywordConstant 
        | varName | varName '[' expression ']' | subroutineCall 
        | '(' expression ')' | unaryOp(~,-) term """

        def processSymbol():
            if self.tokenizer.checkSymbol('('):
                self.writeTerminalsXML(tab_size)
                self.tokenizer.next()
                self.CompileExpression(tab_size)
                if self._tokenParse('symbol', tab_size, ')'):
                    raise TokenizerExcept('CompileTerm ) not found')
            elif self.tokenizer.symbol() in [symbol['~'], symbol['-']]:
                self.writeTerminalsXML(tab_size)
                self.tokenizer.next()
                self.CompileTerm(tab_size)
            else:
                raise TokenizerExcept('CompileTerm processSymbol error')

        def processIdentifier():
            # 三種模式開頭都是identifier, 要再往前一步(LL(1))才知道如何處理
            next_token = self.tokenizer.checkNext()
            # varName '[' expression ']'
            if next_token == symbol['[']:
                self.writeTerminalsXML(tab_size)
                if self._tokenParse('symbol', tab_size, '['):
                    raise TokenizerExcept('CompileTerm [ not found')
                self.tokenizer.next()
                self.CompileExpression(tab_size)
                if self._tokenParse('symbol', tab_size, ']'):
                    raise TokenizerExcept('CoimpileTerm ] not found')
            # subroutineCall
            elif next_token in [symbol['('], symbol['.']]:
                self._ComplieSubroutineCall(tab_size)
            # varName
            else:
                self.writeTerminalsXML(tab_size)

        self.out.write(self._getTabStr(tab_size) + '<term>\n')
        tab_size += 1
        const = [tokenType['keyword'], tokenType['intConst'], tokenType['strConst']]
        # integerConstant, stringConstant, keywordConstant 
        if self.tokenizer.tokenType() in const:
            self.writeTerminalsXML(tab_size)
        elif self.tokenizer.checkTokenType('symbol'):
            processSymbol()
        elif self.tokenizer.checkTokenType('identifier'):
            processIdentifier()
        else:
            raise TokenizerExcept('CompileTerm type error')

        self.out.write(self._getTabStr(tab_size - 1) + '</term>\n')

    def CompileExpressionList(self, tab_size) -> None:
        """ (expression (',' expression)* )? """
        self.out.write(self._getTabStr(tab_size) + '<expressionList>\n')
        if self.tokenizer.checkNext() == symbol[')']:
            self.out.write(self._getTabStr(tab_size) + '</expressionList>\n')
            return

        tab_size += 1
        # expression
        self.tokenizer.next()
        self.CompileExpression(tab_size)

        # (',' expression)*
        while self.tokenizer.checkNext() == symbol[',']:
            if self._tokenParse('symbol', tab_size, symbol[',']):
                raise TokenizerExcept('CompileExpressionList , not found')

            # expression
            self.tokenizer.next()
            self.CompileExpression(tab_size)

        self.out.write(self._getTabStr(tab_size - 1) + '</expressionList>\n')

    def _ComplieSubroutineCall(self, tab_size) -> None:
        """(subroutineName '(' expressionList ')' ) | ( ( className | varName) '.' subroutineName '(' expressionList ')' )
            非規定子結構, 前後不須用<xxx></xxx>包覆"""

        def process_expressionList():
            self.writeTerminalsXML(tab_size)
            # ExpressionList可能為0, 故進入後再next()
            self.CompileExpressionList(tab_size)
            # ')'
            if self._tokenParse('symbol', tab_size, symbol[')']):
                raise TokenizerExcept('SubroutineCall ) not found')

        # 沒有到下一層tab_size不須+1
        self.writeTerminalsXML(tab_size)

        # '('
        self.tokenizer.next()
        if self.tokenizer.checkSymbol('('):
            process_expressionList()
        elif self.tokenizer.checkSymbol('.'):
            self.writeTerminalsXML(tab_size)
            # subroutineName
            if self._tokenParse('identifier', tab_size):
                raise TokenizerExcept('SubroutineCall subroutineName not found')
            self.tokenizer.next()
            process_expressionList()
        else:
            raise TokenizerExcept('SubroutineCall (|. not found')

    def writeTerminalsXML(self, tab_size) -> None:
        self.out.write(self._getTabStr(tab_size))
        if self.tokenizer.tokenType() == tokenType['keyword']:
            self.out.write(f'<keyword> {self.tokenizer.keyWord()} </keyword>')
        elif self.tokenizer.tokenType() == tokenType['symbol']:
            self.out.write(f'<symbol> {self.tokenizer.symbol()} </symbol>')
        elif self.tokenizer.tokenType() == tokenType['intConst']:
            self.out.write(f'<integerConstant> {self.tokenizer.intVal()} </integerConstant>')
        elif self.tokenizer.tokenType() == tokenType['strConst']:
            self.out.write(f'<stringConstant> {self.tokenizer.stringVal()} </stringConstant>')
        elif self.tokenizer.tokenType() == tokenType['identifier']:
            self.out.write(f'<identifier> {self.tokenizer.identifier()} </identifier>')
        else:
            print('getTerminalsXML error')
        self.out.write('\n')

    def _getTabStr(self, tab_size) -> str:
        return '  ' * tab_size

    # 拉出處理token程式return True表示失敗，需丟except
    def _tokenParse(self, type, tab_size, checkVal='') -> bool:
        self.tokenizer.next()
        if (type == 'keyword' and self.tokenizer.checkTokenType(type)
                or type == 'symbol' and self.tokenizer.checkSymbol(symbol[checkVal])
                or type == 'identifier' and self.tokenizer.checkTokenType(type)):
            self.writeTerminalsXML(tab_size)
            return False
        return True

    def _processVarName(self, tab_size, tagName):
        self.out.write(f'{self._getTabStr(tab_size)}<{tagName}>\n')
        tab_size += 1
        self.writeTerminalsXML(tab_size)

        # type
        if (self.tokenizer.next() and (self.tokenizer.isType() or self.tokenizer.checkTokenType('identifier'))):
            self.writeTerminalsXML(tab_size)
        else:
            raise TokenizerExcept(f'{tagName} type not found')

        # varName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept(f'{tagName} varName not found')

        # (',' varName)*
        while self.tokenizer.next() and self.tokenizer.checkSymbol(symbol[',']):
            self.writeTerminalsXML(tab_size)
            if self._tokenParse('identifier', tab_size):
                raise TokenizerExcept(f'{tagName} varName not found')

        # ';' self.tokenizer.next()必定會跑所以就算面條件不成立也會前移到此token
        if self.tokenizer.checkSymbol(symbol[';']):
            self.writeTerminalsXML(tab_size)
        else:
            raise TokenizerExcept(f'{tagName} symbol ";" not found')

        self.out.write(f'{self._getTabStr(tab_size - 1)}</{tagName}>\n')
