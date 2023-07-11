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
    define = C+ 'let' + variable
    lvalue = define | objectRef | variable
    rvalue = expression
    describe = C+ 'help' + ~expression
    ext = C+ 'exit'
    imprt = C+ 'import' + symbol
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
    
    statement = describe | ext | imprt | assignment | define | expression
    
    return statement


def test_expect(grammar):
    assert grammar.expect() == ['help', 'exit', 'import', 'assignment', 'let', 'expression']


def test_parse(grammar):
    #state = grammar.parse('import foo')
    #assert state.text == ''
    #assert state.tree == ['import', 'foo']

    #state = grammar.parse('let foo')
    #assert state.text == ''
    #assert state.tree == ['let', 'foo']

    state = grammar.parse('12')
    assert state.text == ''
    assert state.tree == ['12']

    #state = grammar.parse('let foo = 12')
    #assert state.text == ''
    #assert state.tree == ['let', 'foo', '=', '12']

    #state = grammar.parse('["foo", true, -3, 3.14]')
    #assert state.text == ''
    #assert state.tree == ['[', '"foo"', ',', 'true', ',', '-3', ',', '3.14', ']']
    #
    #state = grammar.parse('funcs.foo(arg: "baz")')
    #assert state.text == ''
    #assert state.tree == ['funcs', '.', 'foo', '(', 'arg', ':', '"baz"', ')']

