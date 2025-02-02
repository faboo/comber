import pytest
from comber import C, rs, delayed, inf

@pytest.fixture
def grammar():
    string = rs(r'"(\\"|[^"])*"')@('string')
    integer = rs(r'[+-]?[0-9]+')@('integer')
    floating = rs(r'[+-]?[0-9]+\.[0-9]+')@('float')
    symbol = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')@('symbol')
    operator = rs(r'[-+*/|&^$@?~=<>]+')@('operator')

    expression = delayed()@('expression')
    constant = string | floating | integer
    boolean = C+ '!' + expression
    variable = symbol
    objectRef = expression + '.' + symbol
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
    lvalue = objectRef | variable | define
    rvalue = expression
    describe = (C+ 'help' + ~expression)@'help'
    ext = (C+ 'exit')@'exit'
    imprt = (C+ 'import' + symbol)@'import'
    assignment = (lvalue + '=' + rvalue)@('assignment')
    block = expression[1, inf, ';']

    expression.fill(
        # No start symbol
        block |
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
    
    statement = assignment | define
    
    return statement


def _test_expect(grammar):
    assert grammar.expectCore() == ['help', 'exit', 'import', 'assignment', 'let', 'expression']


def _test_parse_import(grammar):
    state = grammar.parse('import foo')
    assert state.text == ''
    assert state.tree == ['import', 'foo']

def test_parse_assignment(grammar):
    state = grammar.parse('foo = bar')
    assert state.text == ''
    assert state.tree == ['foo', '=', 'bar']

def test_parse_let(grammar):
    state = grammar.parse('let foo')
    assert state.text == ''
    assert state.tree == ['let', 'foo']

def test_parse_let_assignment(grammar):
    state = grammar.parse('let foo = 12')
    assert state.text == ''
    assert state.tree == ['let', 'foo', '=', '12']

def test_parse_number(grammar):
    state = grammar.parse('12')
    assert state.text == ''
    assert state.tree == ['12']

def test_parse_array(grammar):
    state = grammar.parse('["foo", true, -3, 3.14]')
    assert state.text == ''
    assert state.tree == ['[', '"foo"', ',', 'true', ',', '-3', ',', '3.14', ']']

def test_parse_call(grammar):
    state = grammar.parse('funcs.foo(arg: "baz")')
    assert state.text == ''
    assert state.tree == ['funcs', '.', 'foo', '(', 'arg', ':', '"baz"', ')']

