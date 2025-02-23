import sys
import cProfile
from comber import C, rs, defer, inf

string = rs(r'"(\\"|[^"])*"')@('string')
integer = rs(r'[+-]?[0-9]+')@('integer')
floating = rs(r'[+-]?[0-9]+\.[0-9]+')@('float')
symbol = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')@('symbol')
operator = rs(r'[-+*/|&^$@?~=<>]+')@('operator')

expression = defer()@('expression')
constant = (string | floating | integer)@'constant'
boolean = C+ '!' + expression
variable = symbol
objectRef = (expression + '.' + symbol)@'reference'
array = (C+ '[' + expression*',' + ']')@'array'
closure = (C+ '\\' + symbol*',' + '.' + expression)@'closure'
dictObject = (C+ '{' + (symbol + ':' + expression)*',' + '}')@'dict'
call = expression + '(' + (symbol + ':' + expression)*',' + ')'
opcall = expression + operator + expression
tryex = C+ 'try' + expression
subscript = expression + '[' + expression + ']'
group = C+ '(' + expression + ')'
ifthen = C+ 'if' + expression + 'then' + expression
define = (C+ 'let' + variable)@'let'
lvalue = define | objectRef | variable
rvalue = expression

describe = (C+ 'help' + ~expression)@'help'
ext = (C+ 'exit')@'exit'
imprt = (C+ 'import' + symbol)@'import'
assignment = (lvalue + '=' + rvalue)@('assignment')
block = expression[1, inf, ';']

expression.fill(
    # No start symbol
#    block |
    opcall |
    subscript |
    call |
    objectRef |

    # Start symbol
    dictObject |
    closure |
    array |
    constant |
    boolean |
    tryex |
    ifthen |
    group |
    variable)

grammar = describe | ext | imprt | assignment | define | expression


def parseArray():
    if '--analyze' in sys.argv:
        grammar.analyze()
    for _ in range(0, 20):
        grammar('[]')
        grammar('["foo", true, -3 + 2, 3.14, false, 17.43]')

parseArray()
