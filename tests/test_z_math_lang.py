from comber import C, rs, cs, defer

number = rs(r'[+-]?[0-9]+(\.[0-9]+)?')@('number')
variable = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')@('variable')
expression = defer()@'multiplication'
expression.fill( (C+ '(' + expression+ ')') | (expression + cs('*/+-') + expression) | number | variable)

def test_math_number():
    state = number('12')
    assert state.text == ''
    assert state.tree == ['12']

    state = expression('12')
    assert state.text == ''
    assert state.tree == ['12']

def test_math_variable():
    state = variable('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    state = expression('foo')
    assert state.text == ''
    assert state.tree == ['foo']

def test_math_multiplication():
    state = expression('1 * 2')
    assert state.text == ''
    assert state.tree == ['1', '*', '2']
