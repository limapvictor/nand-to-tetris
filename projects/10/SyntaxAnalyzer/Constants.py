SYMBOLS = [
    '{', '}', '[', ']', '(', ')', 
    ';', '.', ',',
    '+', '-', '*', '/', '&', '|', 
    '=', '~', '<', '>'     
]

K_CLASS = 'class'
K_CONSTRUCTOR = 'constructor'
K_FUNCTION = 'function'
K_METHOD = 'method'
K_FIELD = 'field'
K_STATIC = 'static'
K_VAR = 'var'
K_INT = 'int'
K_CHAR = 'char'
K_BOOLEAN = 'boolean'
K_VOID = 'void'
K_TRUE = 'true'
K_FALSE = 'false'
K_NULL = 'null'
K_THIS = 'this'
K_LET = 'let'
K_DO = 'do'
K_IF = 'if'
K_ELSE = 'else'
K_WHILE = 'while'
K_RETURN = 'return'

KEYWORDS = [
    K_CLASS ,   K_CONSTRUCTOR , K_FUNCTION , K_METHOD ,    K_FIELD ,   K_STATIC ,    K_VAR , K_INT , K_CHAR ,  K_BOOLEAN ,
    K_VOID ,  K_TRUE ,  K_FALSE ,   K_NULL ,  K_THIS ,  K_LET , K_DO ,K_IF ,K_ELSE ,  K_WHILE ,   K_RETURN 
 ]

T_KEYWORD = 0
T_SYMBOL = 1
T_IDENTIFIER = 2
T_INTEGER_CONSTANT = 3
T_STRING_CONSTANT = 4