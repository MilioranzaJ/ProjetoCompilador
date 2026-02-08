import ply.lex as lex

reserved = {
    'function': 'FUNCTION',
    'if':       'IF',
    'else':     'ELSE',
    'while':    'WHILE',
    'echo':     'ECHO',
    'floatval': 'FLOATVAL',
    'readline': 'READLINE',
    'PHP_EOL':  'PHP_EOL',
}

tokens = [
    'PHP_OPEN',
    'PHP_CLOSE',
    'VAR',          
    'NUMERO_REAL',  
    'STRING',
    'IDENT',        

    'SOMA', 'SUB', 'MULT', 'DIV',
    'ATRIB',
    
    'IGUAL', 'DIFERENTE', 
    'MAIOR', 'MENOR', 
    'MAIOR_IGUAL', 'MENOR_IGUAL',

    'PV',          
    'VIRG',        
    'PONTO',       
    'ABRE_P', 'FECHA_P',  
    'ABRE_C', 'FECHA_C',  
    
] + list(reserved.values())

t_SOMA        = r'\+'
t_SUB         = r'-'
t_MULT        = r'\*'
t_DIV         = r'/'
t_ATRIB       = r'='
t_PV          = r';'
t_VIRG        = r','
t_PONTO       = r'\.'
t_ABRE_P      = r'\('
t_FECHA_P     = r'\)'
t_ABRE_C      = r'\{'
t_FECHA_C     = r'\}'
t_PHP_OPEN    = r'<\?php'
t_PHP_CLOSE   = r'\?>'

t_MAIOR_IGUAL = r'>='
t_MENOR_IGUAL = r'<='
t_IGUAL       = r'=='
t_DIFERENTE   = r'!='
t_MAIOR       = r'>'
t_MENOR       = r'<'

def t_FLOATVAL_READLINE(t):
    r'floatval\s*\(\s*readline\s*\(\s*\)\s*\)'
    t.type = 'FLOATVAL'
    t.value = 'floatval(readline());'
    return t

def t_VAR(t):
    r'\$[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NUMERO_REAL(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t
def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENT') 
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    return t

def t_COMENTARIO_LINHA(t):
    r'//.*'
    pass

def t_COMENTARIO_BLOCO(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()