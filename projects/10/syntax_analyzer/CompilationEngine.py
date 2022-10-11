class CompilationEngine:
    """ 
    每隻function註解為該語法結構
    'xxx' 表示 xxx 是keyword或symbol
    x? 表示 x 出現 0 次或 1 次
    x* 表示 x 出現 1 次或 多次
    """
    def __init__(self, in_stream, out_stream) -> None:
        pass


    def CompileClass() -> None:
        """ 'class' className '{' classVarDec* subroutineDec* '}' """
        pass

    
    def CompileClassVarDec() -> None:
        """ ('static' | 'field' ) type varName (',' varName)* ';' """
        pass

    
    def CompileSubroutine() -> None:
        """ ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody """
        pass

    
    def compileParameterList() -> None:
        """ ((type varName) (',' type varName))? """
        pass

    
    def compileVarDec() -> None:
        """  'var' type varName (',' varName)* ';' """
        pass

    
    def compileStatements() -> None:
        """ letStatement | ifStatement | whileStatement | doStatement | returnStatement """
        pass

    
    def compileDo() -> None:
        """ 'do' subroutineCall ';' """
        pass

    
    def compileLet() -> None:
        """ 'let' varName ('[' expression ']')? '=' expression ';' """
        pass

    
    def compileWhile() -> None:
        """ 'while' '(' expression ')' '{' statements '}' """
        pass

    
    def compileReturn() -> None:
        """ 'return' expression? ';’ """
        pass

    
    def compileIf() -> None:
        """ 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )? """
        pass

    
    def CompileExpression() -> None:
        """ expression: term (op term)* """
        pass

    
    def CompileTerm() -> None:
        """ integerConstant | stringConstant | keywordConstant 
        | varName | varName '[' expression ']' | subroutineCall 
        | '(' expression ')' | 一元運算(unaryOp) term """
        pass

    
    def CompileExpressionList() -> None:
        """ (expression (',' expression)* )? """
        pass

    
