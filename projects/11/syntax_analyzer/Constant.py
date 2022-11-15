keyword = {
    'class': 'class',
    'constructor': 'constructor',
    'function': 'function',
    'method': 'method',
    'field': 'field',
    'static': 'static',
    'var': 'var',
    'int': 'int',
    'char': 'char',
    'boolean': 'boolean',
    'void': 'void',
    'true': 'true',
    'false': 'false',
    'null': 'null',
    'this': 'this',
    'let': 'let',
    'do': 'do',
    'if': 'if',
    'else': 'else',
    'while': 'while',
    'return': 'return'
}

symbol = {
    '{': '{',
    '}': '}',
    '(': '(',
    ')': ')',
    '[': '[',
    ']': ']',
    '.': '.',
    ',': ',',
    ';': ';',
    '+': '+',
    '-': '-',
    '*': '*',
    '/': '/',
    '&': '&',
    '|': '|',
    '<': '<',
    '>': '>',
    '=': '=',
    '~': '~'
}

tokenType = {
    'keyword': 'keyword',
    'symbol': 'symbol',
    'intConst': 'integerConstant',
    'strConst': 'stringConstant',
    'identifier': 'identifier'
}

# Jack variable type
IDT_STATIC = 'static'
IDT_FIELD = 'field'
IDT_ARG = 'arg'
IDT_VAR = 'var'

# memory segment
CONST = 'constant'
ARG = 'argument'
LOCAL = 'local'
STATIC = 'static'
THIS = 'this'
THAT = 'that'
POINTER = 'pointer'
TEMP = 'temp'

# Arithmetic cmd
ADD = 'add'
SUB = 'sub'
NEG = 'neg'
EQ = 'eq'
GT = 'gt'
LT = 'lt'
AND = 'and'
OR = 'or'
NOT = 'not'
