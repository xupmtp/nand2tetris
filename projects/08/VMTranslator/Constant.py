class Constant:
    """常數module"""

    """command_type"""
    C_ERROR = -1
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_RETURN = 6
    C_FUNCTION = 7
    C_CALL = 8

    """command segment"""
    LOCAL = 'local'
    ARGUMENT = 'argument'
    THIS = 'this'
    THAT = 'that'
    CONSTATNT = 'constant'
    TEMP = 'temp'
    STATIC = 'static'
    POINTER = 'pointer'

    """airthmetic command segment"""
    # return integer
    ADD = 'add'
    SUB = 'sub'
    NEG = 'neg'
    # return true/false
    EQ = 'eq'
    GT = 'gt'
    LT = 'lt'
    AND = 'and'
    OR = 'or'
    NOT = 'not'
    