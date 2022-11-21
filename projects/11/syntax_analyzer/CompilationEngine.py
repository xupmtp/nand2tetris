from JackTokenizer import *
from TokenizerExcept import *
from SymbolTable import *
from VMWriter import *


class CompilationEngine:
    """
    處理所有語法, 呼叫對應的函數解析token

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
        self.writer = VMWriter(out_stream)
        self.className = ''
        self.cod_idx = 0
        self.if_idx = 0

    def CompileClass(self) -> None:
        """ 'class' className '{' classVarDec* subroutineDec* '}' """

        # 只有CompileClass() 開始時須取得當前token, 其他呼叫時便已是該Compiler的token
        self.tokenizer.next()
        if not self.tokenizer.checkKeyword(keyword['class']):
            raise TokenizerExcept('class keyword not found')

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

    def CompileClassVarDec(self, tab_size) -> None:
        """ ('static' | 'field' ) type varName (',' varName)* ';' """
        self._processVarName(tab_size)

    def CompileSubroutine(self, tab_size) -> None:
        """ ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody """
        # 'constructor' | 'function' | 'method'
        tab_size += 1
        #  reset symbol table
        self.table.startSubroutine()
        # ('constructor' | 'function' | 'method')
        f_key = self.tokenizer.keyWord()
        # method第一參數必須為this
        if f_key == keyword['method']:
            self.table.define('this', self.className, IDT_ARG)

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
        self.compileParameterList(tab_size)

        # 不管compileParameterList()有沒有值, 下個token必為 ')'
        if self._tokenParse('symbol', tab_size, ')'):
            raise TokenizerExcept('Subroutine ")" not found')

        self.tokenizer.next()
        if self.tokenizer.checkSymbol('{'):
            self.ComplieSubroutineBody(f_name, f_key, tab_size)
        else:
            raise TokenizerExcept('Subroutine "{" not found')

    def ComplieSubroutineBody(self, f_name, f_keyword, tab_size):
        """ '{' varDec* statements '}' """
        tab_size += 1

        # varDec*
        while self.tokenizer.checkNext() == keyword['var']:
            self.tokenizer.next()
            self.compileVarDec(tab_size)

        # 在"function name args"中宣告的args數量只看參數列表, 不加上this
        self.writer.writeFunction(f"{self.className}.{f_name}", self.table.index[IDT_VAR])
        if f_keyword == keyword['method']:
            # method函數開頭要先push 呼叫class的this到第一個參數
            self.writer.writePush(VM_ARG, 0)
            # this設給當前函數的this
            self.writer.writePop(VM_POINTER, 0)
        elif f_keyword == keyword['constructor']:
            # constructor函數開頭要先分配空間給此class, 大小根據field變數數量決定
            self.writer.writePush(VM_CONST, self.table.varCount(IDT_FIELD))
            self.writer.writeCall("Memory.alloc", 1)
            # 取得的空間開頭會設給class的this
            self.writer.writePop(VM_POINTER, 0)

        # statements
        if self.tokenizer.checkNext() in ['let', 'do', 'if', 'while', 'return']:
            self.compileStatements(tab_size)

        # '}'
        if self._tokenParse('symbol', tab_size, '}'):
            raise TokenizerExcept('Subroutine "}" not found')

    def compileParameterList(self, tab_size) -> None:
        """ ((type varName) (',' type varName)*)? """
        if self.tokenizer.checkNext() == symbol[')']:
            return

        tab_size += 1
        self.tokenizer.next()
        # type
        if not self.tokenizer.isType():
            raise TokenizerExcept('ParameterList type not found')
        i_type = self.tokenizer.token
        # varName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('ParameterList varName not found')
        self.table.define(self.tokenizer.identifier(), i_type, IDT_ARG)
        # (',' varName)* 最後會前進到 ')'停止
        while self.tokenizer.checkNext() == symbol[',']:
            self.tokenizer.next()
            # type
            if not self.tokenizer.next() and (self.tokenizer.isType() or self.tokenizer.checkTokenType('identifier')):
                raise TokenizerExcept('ParameterList type not found')
            i_type = self.tokenizer.token
            # varName
            if self._tokenParse('identifier', tab_size):
                raise TokenizerExcept('ParameterList varName not found')
            self.table.define(self.tokenizer.identifier(), i_type, IDT_ARG)

    def compileVarDec(self, tab_size) -> None:
        """  'var' type varName (',' varName)* ';' """
        self._processVarName(tab_size)

    def compileStatements(self, tab_size) -> None:
        """ ( letStatement | ifStatement | whileStatement | doStatement | returnStatement )* """
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

    def compileDo(self, tab_size) -> None:
        """ 'do' subroutineCall ';' """
        tab_size += 1
        self.tokenizer.next()
        if self.tokenizer.checkTokenType('identifier'):
            self._ComplieSubroutineCall(tab_size)
        else:
            raise TokenizerExcept('compileDo subroutineCall not found')

        if self._tokenParse('symbol', tab_size, ';'):
            raise TokenizerExcept('compileDo ";" not found')
        # 不管return甚麼都丟棄到temp 0
        self.writer.writePop(VM_TEMP, 0)

    def compileLet(self, tab_size) -> None:
        """ 'let' varName ('[' expression ']')? '=' expression ';' """
        tab_size += 1
        # varName
        if self._tokenParse('identifier', tab_size):
            raise TokenizerExcept('compileLet varName not found')

        _, kind, idx = self.table.paramOf(self.tokenizer.identifier())
        is_arr = False

        self.tokenizer.next()
        # ('[' expression ']')?
        # 如果是arr物件要賦值, 先將arr pointer push到stack中
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
            # 如果是陣列賦值, 先將expression結果pop到temp 0, 再跳到arr pointer位置, 最後將temp 0 push到arr[i]內
            self.writer.writePop(VM_TEMP, 0)
            self.writer.writePop(VM_POINTER, 1)
            self.writer.writePush(VM_TEMP, 0)
            self.writer.writePop(VM_THAT, 0)
        else:
            # 其他狀況直接pop expression結果到變數位置
            self.writer.writePop(kind, idx)

    def compileWhile(self, tab_size) -> None:
        """ 'while' '(' expression ')' '{' statements '}' """
        tab_size += 1
        # idx變數儲存cod_idx, 確保在statements中cod_idx被改變的情形
        idx = self.cod_idx
        self.cod_idx += 1
        # '('
        if self._tokenParse('symbol', tab_size, '('):
            raise TokenizerExcept('compileWhile "(" not found')

        # 每次迴圈要從條件式重新執行
        self.writer.writeLabel(f"WHILE_EXP{idx}")
        # expression
        self.tokenizer.next()
        self.CompileExpression(tab_size)

        # ')'
        if self._tokenParse('symbol', tab_size, ')'):
            raise TokenizerExcept('compileWhile ")" not found')
        # 條件不成立(!true)時跳到END
        self.writer.writeArithmetic(VM_NOT)
        self.writer.writeIf(f"WHILE_END{idx}")

        # '{'
        if self._tokenParse('symbol', tab_size, '{'):
            raise TokenizerExcept('compileWhile "{" not found')

        # statements
        self.compileStatements(tab_size)

        # '}'
        if self._tokenParse('symbol', tab_size, '}'):
            raise TokenizerExcept('compileWhile "}" not found')
        self.writer.writeGoto(f"WHILE_EXP{idx}")
        # while 結束位置
        self.writer.writeLabel(f"WHILE_END{idx}")

    def compileReturn(self, tab_size) -> None:
        """ 'return' expression? ';’ """
        tab_size += 1

        # expression
        self.tokenizer.next()
        if not self.tokenizer.checkSymbol(';'):
            self.CompileExpression(tab_size)
            self.tokenizer.next()
        else:
            # 如果沒有return內容須push 0到stack中做為return值
            self.writer.writePush(VM_CONST, 0)

        # ';'
        if not self.tokenizer.checkSymbol(';'):
            raise TokenizerExcept('compileReturn ";" not found')
        self.writer.writeReturn()

    def compileIf(self, tab_size) -> None:
        """ 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )? """
        tab_size += 1
        # idx變數儲存cod_idx, 確保在statements中cod_idx被改變的情形
        idx = self.if_idx
        self.if_idx += 1

        if self._tokenParse('symbol', tab_size, '('):
            raise TokenizerExcept('compileIf "(" not found')

        # expression
        self.tokenizer.next()
        # 先計算完表達式在決定流程
        self.CompileExpression(tab_size)

        # ')'
        if self._tokenParse('symbol', tab_size, ')'):
            raise TokenizerExcept('compileReturn ")" not found')

        # TRUE:往下走, FALSE:跳到FALSE標籤
        self.writer.writeIf(f"IF_TRUE{idx}")
        self.writer.writeGoto(f"IF_FALSE{idx}")
        self.writer.writeLabel(f"IF_TRUE{idx}")

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
            # 如果有else區塊, FALSE標籤變成else開始標籤,新增END標籤在if-else結尾處
            self.writer.writeGoto(f"IF_END{idx}")
            self.writer.writeLabel(f"IF_FALSE{idx}")
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
            self.writer.writeLabel(f"IF_END{idx}")
        else:
            self.writer.writeLabel(f"IF_FALSE{idx}")

    def CompileExpression(self, tab_size) -> None:
        """ term (op term)* """
        tab_size += 1
        self.CompileTerm(tab_size)

        # (op term)*
        while self.tokenizer.isOp(self.tokenizer.checkNext()):
            # op
            if self._tokenParse('symbol', tab_size, self.tokenizer.checkNext()):
                raise TokenizerExcept('CompileExpression op not found')
            # 加入'b'辨別是二元運算子
            op = ('b' if self.tokenizer.symbol() is '-' else '') + self.tokenizer.symbol()
            # term
            self.tokenizer.next()
            self.CompileTerm(tab_size)
            self.writer.writeArithmetic(vm_operation[op])

    def CompileTerm(self, tab_size) -> None:
        """ integerConstant | stringConstant | keywordConstant 
        | varName | varName '[' expression ']' | subroutineCall 
        | '(' expression ')' | unaryOp(~,-) term """
        tab_size += 1
        # integerConstant, stringConstant, keywordConstant
        if self.tokenizer.tokenType() == tokenType['keyword']:
            self._termKeywordConst(self.tokenizer.keyWord())
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

    def CompileExpressionList(self, tab_size) -> int:
        """ (expression (',' expression)* )? """
        if self.tokenizer.checkNext() == symbol[')']:
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
        f_len = 0
        f_type, f_kind, f_idx = self.table.paramOf(f_name)
        # 如果是varName, 要多傳該變數指向的this(由symbol table取得)
        if f_type is not None:
            f_name = f_type
            self.writer.writePush(f_kind, f_idx)
            f_len = 1

        # '('
        self.tokenizer.next()
        if self.tokenizer.checkSymbol('('):
            # 表示直接以subroutineName()呼叫, 多傳入this作為第一個參數
            f_len += 1 + process_expressionList()
            p_name = self.className
            self.writer.writePush(VM_POINTER, 0)
        elif self.tokenizer.checkSymbol('.'):
            # className.subroutineName, 呼叫的class名稱由symbol table取得
            if self._tokenParse('identifier', tab_size):
                raise TokenizerExcept('SubroutineCall subroutineName not found')
            p_name, f_name = f_name, self.tokenizer.identifier()
            # '('
            self.tokenizer.next()
            f_len += process_expressionList()
        else:
            raise TokenizerExcept('SubroutineCall (|. not found')
        self.writer.writeCall(f"{p_name}.{f_name}", f_len)

    # 拉出處理token程式return True表示失敗，需丟except
    def _tokenParse(self, type, tab_size, checkVal='') -> bool:
        self.tokenizer.next()
        if (type == 'keyword' and self.tokenizer.checkTokenType(type)
                or type == 'symbol' and self.tokenizer.checkSymbol(symbol[checkVal])
                or type == 'identifier' and self.tokenizer.checkTokenType(type)):
            return False
        return True

    def _processVarName(self, tab_size):
        """定義變數到symbol table"""
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
        """解析符號"""
        if self.tokenizer.checkSymbol('('):
            self.tokenizer.next()
            self.CompileExpression(tab_size)
            if self._tokenParse('symbol', tab_size, ')'):
                raise TokenizerExcept('CompileTerm ) not found')
        elif self.tokenizer.symbol() in [symbol['~'], symbol['-']]:
            """特殊的一元運算符處理"""
            op = ('u' if self.tokenizer.symbol() is symbol['-'] else '') + self.tokenizer.symbol()
            self.tokenizer.next()
            self.CompileTerm(tab_size)
            self.writer.writeArithmetic(vm_operation[op])
        else:
            raise TokenizerExcept('CompileTerm processSymbol error')

    def _termIdentifier(self, tab_size):
        """解析標識浮token"""
        # 三種模式開頭都是identifier, 要再往前一步(LL(1))才知道如何處理
        next_token = self.tokenizer.checkNext()
        """varName '[' expression ']'
        取得陣列值的步驟為
        1. 解析expression
        2. push arr pointer, expression結果
        3. add
        4. pop到that
        5. 取值(that 0)
        """
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
        """解析字串"""
        self.writer.writePush(VM_CONST, len(string))
        self.writer.writeCall('String.new', 1)
        for c in string:
            self.writer.writePush(VM_CONST, ord(c))
            # 第一個參數是string.new完取得的內容
            self.writer.writeCall('String.appendChar', 2)

    def _termKeywordConst(self, key):
        """解析關鍵字常數 (true, false, null, this)"""
        if key is keyword['true']:
            self.writer.writePush(VM_CONST, 1)
            self.writer.writeArithmetic(VM_NEG)
        elif key in 'false,null':
            self.writer.writePush(VM_CONST, 0)
        elif key is 'this':
            self.writer.writePush(VM_POINTER, 0)
        else:
            print('compiler termKeywordConst error')
