from comber import C, rs, cs, delayed

number = rs(r'[+-]?[0-9]+(\.[0-9]+)?')@('number')
variable = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')@('variable')
expression = delayed()@'multiplication'
expression.fill( (C+ '(' + expression+ ')') | (expression + cs('*/+-') + expression) | number | variable)

def test_math_number():
    state = number.parse('12')
    assert state.text == ''
    assert state.tree == ['12']

    state = expression.parse('12')
    assert state.text == ''
    assert state.tree == ['12']

def test_math_variable():
    state = variable.parse('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    state = expression.parse('foo')
    assert state.text == ''
    assert state.tree == ['foo']

def test_math_multiplication():
    #state = multiplication.parse('1 * 2')
    #assert state.text == ''
    #assert state.tree == ['1', '*', '2']

    state = expression.parse('1 * 2')
    assert state.text == ''
    assert state.tree == ['1', '*', '2']
