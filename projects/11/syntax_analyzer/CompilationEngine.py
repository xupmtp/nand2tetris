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
        self.className = ''
        self.if_idx = 0
        self.while_idx = 0

    def CompileClass(self) -> None:
        """ 'class' className '{' classVarDec* subroutineDec* '}' """

        # 只有CompileClass() 開始時須取得當前token, 其他呼叫時便已是該Compiler的token
        self.tokenizer.next()
        if not self.tokenizer.checkKeyword(keyword['class']):
            raise TokenizerExcept('class keyword not found')

        self.out.write('<class>\n')
        tab_size = 1
        # class name
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('class name not found')
        self.className = self.tokenizer.identifier()

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
        if not self.tokenizer.checkTokenType('symbol'):
            raise TokenizerExcept('class symbol "}" not found')

        self.out.write('</class>\n')

    def CompileClassVarDec(self, tab_size) -> None:
        """ ('static' | 'field' ) type varName (',' varName)* ';' """
        self._processVarName(tab_size)

    def CompileSubroutine(self, tab_size) -> None:
        """ ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody """
        self.out.write(self._getTabStr(tab_size) + '<subroutineDec>\n')
        tab_size += 1
        # 'constructor' | 'function' | 'method'
        tab_size += 1
        #  reset symbol table
        self.table.startSubroutine()
        # method 函數第一個多傳this
        if self.tokenizer.keyWord() is keyword['method']:
            p_len = 1
            # set this using arg 0
            is_method = True
        else:
            p_len = 0
            is_method = False
        if self.tokenizer.keyWord() is keyword['constructor']:
            # TODO check idx要怎麼傳
            self.writer.writeCall('Memory.alloc', 1)

        # ('void' | type)
        if not (self.tokenizer.next() and self.tokenizer.isType()):
            raise TokenizerExcept('Subroutine type not found')

        # subroutineName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('Subroutine subroutineName not found')
        f_name = self.tokenizer.identifier()

        # '('
        if self._tokenParse('symbol', tab_size, '('):
            raise TokenizerExcept('Subroutine "(" not found')

        # parameterList
        p_len += self.compileParameterList(tab_size)

        # 不管compileParameterList()有沒有值, 下個token必為 ')'
        if self._tokenParse('symbol', tab_size, ')'):
            raise TokenizerExcept('Subroutine ")" not found')

        self.writer.writeFunction(f"{self.className}.{f_name}", p_len)
        if is_method:
            self.writer.writePush(VM_ARG, 0)
            self.writer.writePop(VM_POINTER, 0)

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

    def compileParameterList(self, tab_size) -> int:
        """ ((type varName) (',' type varName)*)? """
        self.out.write(self._getTabStr(tab_size) + '<parameterList>\n')

        if self.tokenizer.checkNext() == symbol[')']:
            self.out.write(self._getTabStr(tab_size) + '</parameterList>\n')
            return 0

        tab_size += 1
        self.tokenizer.next()
        i_type = None
        # type
        if not self.tokenizer.isType() or self.tokenizer.checkTokenType('identifier'):
            raise TokenizerExcept('ParameterList type not found')
        i_type = self.tokenizer.token
        # varName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('ParameterList varName not found')
        self.table.define(self.tokenizer.identifier(), i_type, IDT_ARG)
        # 計算參數數量
        res = 1
        # (',' varName)* 最後會前進到 ')'停止
        while self.tokenizer.checkNext() == symbol[',']:
            res += 1
            self.tokenizer.next()
            # type
            if not self.tokenizer.next() and (self.tokenizer.isType() or self.tokenizer.checkTokenType('identifier')):
                raise TokenizerExcept('ParameterList type not found')
            i_type = self.tokenizer.token
            # varName
            if self._tokenParse('identifier', tab_size):
                raise TokenizerExcept('ParameterList varName not found')
            self.table.define(self.tokenizer.identifier(), i_type, IDT_ARG)

        self.out.write(self._getTabStr(tab_size - 1) + '</parameterList>\n')

    def compileVarDec(self, tab_size) -> None:
        """  'var' type varName (',' varName)* ';' """
        self._processVarName(tab_size)

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
        self.tokenizer.next()
        if self.tokenizer.checkTokenType('identifier'):
            self._ComplieSubroutineCall(tab_size)
        else:
            raise TokenizerExcept('compileDo subroutineCall not found')

        if self._tokenParse('symbol', tab_size, ';'):
            raise TokenizerExcept('compileDo ";" not found')
        # do return 後不做事
        self.writer.writePop(VM_TEMP, 0)

        self.out.write(self._getTabStr(tab_size - 1) + '</doStatement>\n')

    def compileLet(self, tab_size) -> None:
        """ 'let' varName ('[' expression ']')? '=' expression ';' """
        self.out.write(self._getTabStr(tab_size) + '<letStatement>\n')
        tab_size += 1

        # varName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('compileLet varName not found')

        _, kind, idx = self.table.paramOf(self.tokenizer.identifier())
        is_arr = False

        self.tokenizer.next()
        # ('[' expression ']')?
        if self.tokenizer.checkSymbol('['):
            is_arr = True
            self.tokenizer.next()
            self.CompileExpression(tab_size)
            if self._tokenParse('symbol', tab_size, ']'):
                raise TokenizerExcept('compileLet "]" not found')
            else:
                self.tokenizer.next()
            # varName
            self.writer.writePush(kind, idx)
            self.writer.writeArithmetic(VM_ADD)

        # '='
        if not self.tokenizer.checkSymbol('='):
            raise TokenizerExcept('compileLet "=" not found')

        # expression
        self.tokenizer.next()
        self.CompileExpression(tab_size)

        # ';'
        if self._tokenParse('symbol', tab_size, ';'):
            raise TokenizerExcept('compileLet ";" not found')
        # set '='後面 expression result的值給varName
        if is_arr:
            self.writer.writePop(VM_TEMP, 0)
            self.writer.writePop(VM_POINTER, 1)
            self.writer.writePush(VM_TEMP, 0)
            self.writer.writePop(VM_THAT, 0)
        else:
            self.writer.writePop(kind, idx)

        self.out.write(self._getTabStr(tab_size - 1) + '</letStatement>\n')

    def compileWhile(self, tab_size) -> None:
        """ 'while' '(' expression ')' '{' statements '}' """
        self.out.write(self._getTabStr(tab_size) + '<whileStatement>\n')
        tab_size += 1
        # '('
        if self._tokenParse('symbol', tab_size, '('):
            raise TokenizerExcept('compileWhile "(" not found')

        # 每次迴圈要從條件式重新執行
        self.writer.writeLabel(f"WHILE_EXP{self.while_idx}")
        # expression
        self.tokenizer.next()
        self.CompileExpression(tab_size)

        # ')'
        if self._tokenParse('symbol', tab_size, ')'):
            raise TokenizerExcept('compileWhile ")" not found')
        # 條件不成立(!true)時跳到END
        self.writer.writeArithmetic(VM_NOT)
        self.writer.writeIf(f"WHILE_END{self.while_idx}")

        # '{'
        if self._tokenParse('symbol', tab_size, '{'):
            raise TokenizerExcept('compileWhile "{" not found')

        # statements
        self.compileStatements(tab_size)

        # '}'
        if self._tokenParse('symbol', tab_size, '}'):
            raise TokenizerExcept('compileWhile "}" not found')
        # while 結束位置
        self.writer.writeLabel(f"WHILE_END{self.while_idx}")
        self.while_idx += 1

        self.out.write(self._getTabStr(tab_size - 1) + '</whileStatement>\n')

    def compileReturn(self, tab_size) -> None:
        """ 'return' expression? ';’ """
        self.out.write(self._getTabStr(tab_size) + '<returnStatement>\n')
        tab_size += 1

        # expression
        self.tokenizer.next()
        if not self.tokenizer.checkSymbol(';'):
            self.CompileExpression(tab_size)
            self.tokenizer.next()
        else:
            self.writer.writePush(VM_CONST, 0)

        # ';'
        if not self.tokenizer.checkSymbol(';'):
            raise TokenizerExcept('compileReturn ";" not found')
        self.writer.writeReturn()

        self.out.write(self._getTabStr(tab_size - 1) + '</returnStatement>\n')

    def compileIf(self, tab_size) -> None:
        """ 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )? """
        tab_size += 1

        if self._tokenParse('symbol', tab_size, '('):
            raise TokenizerExcept('compileIf "(" not found')

        # expression
        self.tokenizer.next()
        self.CompileExpression(tab_size)

        # ')'
        if self._tokenParse('symbol', tab_size, ')'):
            raise TokenizerExcept('compileReturn ")" not found')

        self.writer.writeIf(f"IF_TRUE{self.if_idx}")
        self.writer.writeGoto(f"IF_FALSE{self.if_idx}")
        self.writer.writeLabel(f"IF_TRUE{self.if_idx}")

        # '{'
        if self._tokenParse('symbol', tab_size, '{'):
            raise TokenizerExcept('compileIf if "{" not found')

        # statements
        self.compileStatements(tab_size)

        # '}'
        if self._tokenParse('symbol', tab_size, '}'):
            raise TokenizerExcept('compileIf if "{" not found')

        # ( 'else' '{' statements '}' )?
        self.writer.writeLabel(f"IF_FALSE{self.if_idx}")
        self.if_idx += 1
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
            op = self.tokenizer.symbol()
            # term
            self.tokenizer.next()
            self.CompileTerm(tab_size)
            self.writer.writeArithmetic(operation[op])

        self.out.write(self._getTabStr(tab_size - 1) + '</expression>\n')

    def CompileTerm(self, tab_size) -> None:
        """ integerConstant | stringConstant | keywordConstant 
        | varName | varName '[' expression ']' | subroutineCall 
        | '(' expression ')' | unaryOp(~,-) term """
        self.out.write(self._getTabStr(tab_size) + '<term>\n')
        tab_size += 1
        # integerConstant, stringConstant, keywordConstant
        if self.tokenizer.tokenType() == tokenType['keyword']:
            self.writer.writePush(self.table.kindOf(self.tokenizer.keyWord()), self.table.indexOf(self.tokenizer.keyWord()))
        elif self.tokenizer.tokenType() == tokenType['intConst']:
            self.writer.writePush(VM_CONST, self.tokenizer.intVal())
        elif self.tokenizer.tokenType() == tokenType['strConst']:
            self._termString(self.tokenizer.stringVal())
        elif self.tokenizer.checkTokenType('symbol'):
            self._termSymbol(tab_size)
        elif self.tokenizer.checkTokenType('identifier'):
            self._termIdentifier(tab_size)
        else:
            raise TokenizerExcept('CompileTerm type error')

        self.out.write(self._getTabStr(tab_size - 1) + '</term>\n')

    def CompileExpressionList(self, tab_size) -> int:
        """ (expression (',' expression)* )? """
        self.out.write(self._getTabStr(tab_size) + '<expressionList>\n')
        if self.tokenizer.checkNext() == symbol[')']:
            self.out.write(self._getTabStr(tab_size) + '</expressionList>\n')
            return 0

        tab_size += 1
        # expression
        self.tokenizer.next()
        self.CompileExpression(tab_size)
        res = 1

        # (',' expression)*
        while self.tokenizer.checkNext() == symbol[',']:
            if self._tokenParse('symbol', tab_size, symbol[',']):
                raise TokenizerExcept('CompileExpressionList , not found')

            # expression
            self.tokenizer.next()
            self.CompileExpression(tab_size)
            res += 1

        self.out.write(self._getTabStr(tab_size - 1) + '</expressionList>\n')
        return res

    def _ComplieSubroutineCall(self, tab_size) -> None:
        """(subroutineName '(' expressionList ')' ) | ( ( className | varName) '.' subroutineName '(' expressionList ')' )
            非規定子結構, 前後不須用<xxx></xxx>包覆"""
        def process_expressionList():
            # ExpressionList可能為0, 故進入後再next()
            res = self.CompileExpressionList(tab_size)
            # ')'
            if self._tokenParse('symbol', tab_size, symbol[')']):
                raise TokenizerExcept('SubroutineCall ) not found')
            return res

        # subroutineName | className | varName
        f_name = self.tokenizer.identifier()
        # '('
        self.tokenizer.next()
        if self.tokenizer.checkSymbol('('):
            f_len = 1 + process_expressionList()
            p_name = self.className
            self.writer.writePush(VM_POINTER, 0)
        elif self.tokenizer.checkSymbol('.'):
            f_len = 0
            # subroutineName
            if self._tokenParse('identifier', tab_size):
                raise TokenizerExcept('SubroutineCall subroutineName not found')
            p_name, f_name = f_name, self.tokenizer.identifier()
            # '('
            self.tokenizer.next()
            f_len += process_expressionList()
        else:
            raise TokenizerExcept('SubroutineCall (|. not found')
        self.writer.writeCall(f"{p_name}.{f_name}", f_len)

    def _getTabStr(self, tab_size) -> str:
        return '  ' * tab_size

    # 拉出處理token程式return True表示失敗，需丟except
    def _tokenParse(self, type, tab_size, checkVal='') -> bool:
        self.tokenizer.next()
        if (type == 'keyword' and self.tokenizer.checkTokenType(type)
                or type == 'symbol' and self.tokenizer.checkSymbol(symbol[checkVal])
                or type == 'identifier' and self.tokenizer.checkTokenType(type)):
            return False
        return True

    def _processVarName(self, tab_size):
        i_type, kind = None, self.tokenizer.keyWord()
        # type
        if self.tokenizer.next() and (self.tokenizer.isType() or self.tokenizer.checkTokenType('identifier')):
            i_type = self.tokenizer.identifier()
        else:
            raise TokenizerExcept(f'VarName type not found')

        # varName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept(f'VarName varName not found')
        self.table.define(self.tokenizer.identifier(), i_type, kind)

        # (',' varName)*
        while self.tokenizer.next() and self.tokenizer.checkSymbol(symbol[',']):
            if self._tokenParse('identifier', tab_size):
                raise TokenizerExcept(f'VarName varName not found')
            self.table.define(self.tokenizer.identifier(), i_type, kind)

        # ';' self.tokenizer.next()必定會跑所以就算面條件不成立也會前移到此token
        if not self.tokenizer.checkSymbol(symbol[';']):
            raise TokenizerExcept(f'VarName symbol ";" not found')

    def _termSymbol(self, tab_size):
        if self.tokenizer.checkSymbol('('):
            self.tokenizer.next()
            self.CompileExpression(tab_size)
            if self._tokenParse('symbol', tab_size, ')'):
                raise TokenizerExcept('CompileTerm ) not found')
        elif self.tokenizer.symbol() in [symbol['~'], symbol['-']]:
            op = ('u' if self.tokenizer.symbol() is symbol['-'] else '') + self.tokenizer.symbol()
            self.tokenizer.next()
            self.CompileTerm(tab_size)
            self.writer.writeArithmetic(operation(op))
        else:
            raise TokenizerExcept('CompileTerm processSymbol error')

    def _termIdentifier(self, tab_size):
        # 三種模式開頭都是identifier, 要再往前一步(LL(1))才知道如何處理
        next_token = self.tokenizer.checkNext()
        # varName '[' expression ']'
        if next_token == symbol['[']:
            var_name = self.tokenizer.identifier()
            if self._tokenParse('symbol', tab_size, '['):
                raise TokenizerExcept('CompileTerm [ not found')
            self.tokenizer.next()
            self.CompileExpression(tab_size)
            if self._tokenParse('symbol', tab_size, ']'):
                raise TokenizerExcept('CoimpileTerm ] not found')
            # 取得arr[i]的值
            _, kind, idx = self.table.paramOf(var_name)
            self.writer.writePush(kind, idx)
            self.writer.writeArithmetic(VM_ADD)
            self.writer.writePop(VM_POINTER, 1)
            self.writer.writePush(VM_THAT, 0)
        # subroutineCall
        elif next_token in [symbol['('], symbol['.']]:
            self._ComplieSubroutineCall(tab_size)
        # varName
        else:
            _, kind, idx = self.table.paramOf(self.tokenizer.identifier())
            self.writer.writePush(kind, idx)

    def _termString(self, string):
        self.writer.writePush(VM_CONST, len(string))
        self.writer.writeCall('String.new', 1)
        for c in string:
            self.writer.writePush(VM_CONST, ord(c))
            # 第一個參數是string.new完取得的內容
            self.writer.writeCall('String.appendChar', 2)

