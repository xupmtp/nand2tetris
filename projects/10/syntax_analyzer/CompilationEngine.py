from JackTokenizer import *


class CompilationEngine:
    """ 
    每隻function註解為該語法結構
    'xxx' 表示 xxx是keyword或symbol
    x? 表示 x 出現 0 次或 1 次
    x* 表示 x 出現 1 次或 多次
    """
    def __init__(self, in_stream, out_stream) -> None:
        self.tokenizer = JackTokenizer(in_stream)
        self.out = out_stream

    
    def CompileClass(self) -> None:
        """ 'class' className '{' classVarDec* subroutineDec* '}' """
        self.out.write('<class>\n')
        self.writeTerminalsXML()

        # class name
        if self.next() and self.tokenizer.tokenType() == tokenType['identifier']:
            self.writeTerminalsXML()
        else:
            print('class name not found')

        if self.next() and self.tokenizer.tokenType() == tokenType['symbol']:
            self.writeTerminalsXML()
        else:
            print('class symbol \"{\" not found')

        if self.next() and self.tokenizer.tokenType() == tokenType['keyword']:
            k = self.tokenizer.keyWord()
            if k in ['static', 'field']:
                self.CompileClassVarDec()
            elif k in ['constructor', 'function', 'method']:
                self.CompileSubroutine()
            else:
                print('class body type error')

        if self.next() and self.tokenizer.tokenType() == tokenType['symbol']:
            self.writeTerminalsXML()
        else:
            print('class symbol "}" not found')

        self.out.write('</class>')

    
    def CompileClassVarDec(self) -> None:
        """ ('static' | 'field' ) type varName (',' varName)* ';' """
        pass

    
    def CompileSubroutine(self) -> None:
        """ ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody """
        pass

    
    def compileParameterList(self) -> None:
        """ ((type varName) (',' type varName))? """
        pass

    
    def compileVarDec(self) -> None:
        """  'var' type varName (',' varName)* ';' """
        pass

    
    def compileStatements(self) -> None:
        """ letStatement | ifStatement | whileStatement | doStatement | returnStatement """
        pass

    
    def compileDo(self) -> None:
        """ 'do' subroutineCall ';' """
        pass

    
    def compileLet(self) -> None:
        """ 'let' varName ('[' expression ']')? '=' expression ';' """
        pass

    
    def compileWhile(self) -> None:
        """ 'while' '(' expression ')' '{' statements '}' """
        pass

    
    def compileReturn(self) -> None:
        """ 'return' expression? ';’ """
        pass

    
    def compileIf(self) -> None:
        """ 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )? """
        pass

    
    def CompileExpression(self) -> None:
        """ term (op term)* """
        pass

    
    def CompileTerm(self) -> None:
        """ integerConstant | stringConstant | keywordConstant 
        | varName | varName '[' expression ']' | subroutineCall 
        | '(' expression ')' | 一元運算(unaryOp) term """
        pass

    
    def CompileExpressionList(self) -> None:
        """ (expression (',' expression)* )? """
        pass


    def next(self) -> bool:
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            return True
        return False


    def writeTerminalsXML(self) -> str:
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

