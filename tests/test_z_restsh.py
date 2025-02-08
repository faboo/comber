import pytest
from comber import C, rs, delayed, inf

string = rs(r'"(\\"|[^"])*"')@('string')
integer = rs(r'[+-]?[0-9]+')@('integer')
floating = rs(r'[+-]?[0-9]+\.[0-9]+')@('float')
symbol = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')@('symbol')
operator = rs(r'[-+*/|&^$@?~=<>]+')@('operator')

expression = delayed() #@('expression')
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


def _test_expect():
    assert grammar.expectCore() == ['help', 'exit', 'import', 'assignment', 'let', 'expression']


def test_parse_import():
    state = grammar.parse('import foo')
    assert state.text == ''
    assert state.tree == ['import', 'foo']

def test_parse_assignment():
    state = grammar.parse('foo = bar')
    assert state.text == ''
    assert state.tree == ['foo', '=', 'bar']

def test_parse_let():
    state = grammar.parse('let foo')
    assert state.text == ''
    assert state.tree == ['let', 'foo']

def test_parse_number():
    state = integer.parse('12')
    assert state.text == ''
    assert state.tree == ['12']

    state = constant.parse('12')
    assert state.text == ''
    assert state.tree == ['12']

    state = grammar.parse('12')
    assert state.text == ''
    assert state.tree == ['12']

def test_parse_let_assignment():
    state = assignment.parse('let foo = 12')
    assert state.text == ''
    assert state.tree == ['let', 'foo', '=', '12']

    state = grammar.parse('let foo = 12')
    assert state.text == ''
    assert state.tree == ['let', 'foo', '=', '12']

def test_parse_string():
    state = string.parse('"foo"')
    assert state.text == ''
    assert state.tree == ['"foo"']

    state = constant.parse('"foo"')
    assert state.text == ''
    assert state.tree == ['"foo"']

    state = grammar.parse('"foo"')
    assert state.text == ''
    assert state.tree == ['"foo"']

def test_parse_array():
    state = expression.parse('[ ]')
    assert state.text == ''
    assert state.tree == ['[', ']']

    state = expression.parse('[ 3 ]')
    assert state.text == ''
    assert state.tree == ['[', '3', ']']

    state = grammar.parse('["foo", true, -3, 3.14, false, 17.43]')
    assert state.text == ''
    assert state.tree == ['[', '"foo"', ',', 'true', ',', '-3', ',', '3.14', ',', 'false', ',', '17.43', ']']

def test_parse_objectRef():
    state = objectRef.parse('funcs.foo')
    assert state.text == ''
    assert state.tree == ['funcs', '.', 'foo']

    state = expression.parse('funcs.foo')
    assert state.text == ''
    assert state.tree == ['funcs', '.', 'foo']

    state = grammar.parse('funcs.foo')
    assert state.text == ''
    assert state.tree == ['funcs', '.', 'foo']

def test_parse_call():
    state = grammar.parse('funcs.foo(arg: "baz")')
    assert state.text == ''
    assert state.tree == ['funcs', '.', 'foo', '(', 'arg', ':', '"baz"', ')']

