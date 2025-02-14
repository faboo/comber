from restsh import grammar, integer, string, constant, expression, assignment, objectRef

def _test_expect():
    assert grammar.expectCore() == ['help', 'exit', 'import', 'assignment', 'let', 'expression']


def test_parse_import():
    state = grammar('import foo')
    assert state.text == ''
    assert state.tree == ['import', 'foo']

def test_parse_assignment():
    state = grammar('foo = bar')
    assert state.text == ''
    assert state.tree == ['foo', '=', 'bar']

def test_parse_let():
    state = grammar('let foo')
    assert state.text == ''
    assert state.tree == ['let', 'foo']

def test_parse_number():
    state = integer('12')
    assert state.text == ''
    assert state.tree == ['12']

    state = constant('12')
    assert state.text == ''
    assert state.tree == ['12']

    state = grammar('12')
    assert state.text == ''
    assert state.tree == ['12']

def test_parse_let_assignment():
    state = assignment('let foo = 12')
    assert state.text == ''
    assert state.tree == ['let', 'foo', '=', '12']

    state = grammar('let foo = 12')
    assert state.text == ''
    assert state.tree == ['let', 'foo', '=', '12']

def test_parse_string():
    state = string('"foo"')
    assert state.text == ''
    assert state.tree == ['"foo"']

    state = constant('"foo"')
    assert state.text == ''
    assert state.tree == ['"foo"']

    state = grammar('"foo"')
    assert state.text == ''
    assert state.tree == ['"foo"']

def test_parse_array():
    state = expression('[ ]')
    assert state.text == ''
    assert state.tree == ['[', ']']

    state = expression('[ 3 ]')
    assert state.text == ''
    assert state.tree == ['[', '3', ']']

    state = grammar('["foo", true, -3, 3.14, false, 17.43]')
    assert state.text == ''
    assert state.tree == ['[', '"foo"', ',', 'true', ',', '-3', ',', '3.14', ',', 'false', ',', '17.43', ']']

def test_parse_objectRef():
    state = objectRef('funcs.foo')
    assert state.text == ''
    assert state.tree == ['funcs', '.', 'foo']

    state = expression('funcs.foo')
    assert state.text == ''
    assert state.tree == ['funcs', '.', 'foo']

    state = grammar('funcs.foo')
    assert state.text == ''
    assert state.tree == ['funcs', '.', 'foo']

def test_parse_call():
    state = grammar('funcs.foo(arg: "baz")')
    assert state.text == ''
    assert state.tree == ['funcs', '.', 'foo', '(', 'arg', ':', '"baz"', ')']

def test_parse_op_call():
    state = grammar('1 + 2')
    assert state.text == ''
    assert state.tree == ['1', '+', '2']

def test_parse_group():
    state = grammar('(1 + 2)')
    assert state.text == ''
    assert state.tree == ['(', '1', '+', '2', ')']

    state = grammar('("foo")')
    assert state.text == ''
    assert state.tree == ['(', '"foo"', ')']
