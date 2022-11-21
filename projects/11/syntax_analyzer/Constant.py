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

vm_operation = {
    '+': 'add',
    'b-': 'sub',
    'u-': 'neg',
    '>': 'gt',
    '<': 'lt',
    '&': 'and',
    '|': 'or',
    '~': 'not',
    '=': 'eq',
    '*': 'call Math.multiply 2',
    '/': 'call Math.divide 2'
}

# Jack variable type
IDT_STATIC = 'static'
IDT_FIELD = 'field'
IDT_ARG = 'arg'
IDT_VAR = 'var'

# VM CODE segment
VM_CONST = 'constant'
VM_ARG = 'argument'
VM_LOCAL = 'local'
VM_STATIC = 'static'
VM_THIS = 'this'
VM_THAT = 'that'
VM_POINTER = 'pointer'
VM_TEMP = 'temp'
# VM Arithmetic
VM_ADD = 'add'
VM_SUB = 'sub'
VM_NEG = 'neg'
VM_GT = 'gt'
VM_LT = 'lt'
VM_AND = 'and'
VM_OR = 'or'
VM_NOT = 'not'
VM_EQ = 'eq'

