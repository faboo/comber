import pytest
from comber import C, rs, defer, inf

# This grammar is (nearly) the grammar of Restsh

string = rs(r'"(\\"|[^"])*"')@('string')
integer = rs(r'[+-]?[0-9]+')@('integer')
floating = rs(r'[+-]?[0-9]+\.[0-9]+')@('float')
symbol = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')@('symbol')
operator = rs(r'[-+*/|&^$@?~=<>]+')@('operator')

expression = defer()
constant = (string | floating | integer)@'constant'
boolean = C+ '!' + expression
variable = symbol
objectRef = (expression + '.' + symbol)@'reference'
array = C+ '[' + expression[0, inf, ','] + ']'
closure = C+ '\\' + symbol[0, inf, ','] + '.' + expression
dictObject = C+ '{' + (symbol + ':' + expression)[0, inf, ','] + '}'
call = expression + '(' + (symbol + ':' + expression)[0, inf, ','] + ')'
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
    call |
    opcall |
    subscript |
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

