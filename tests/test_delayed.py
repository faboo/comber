import pytest
from comber import delayed, ParseError, Lit

def test_create_delayed():
    parser = delayed()
    parser.fill('foo')

def test_expect_delayed():
    parser = delayed()
    parser.fill(Lit('foo'))
    assert parser.expectCore() == Lit('foo').expectCore()

def test_parse_delayed():
    parser = delayed()
    parser.fill(Lit('foo'))

    state = parser('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    with pytest.raises(ParseError):
        parser('bar')

def test_recurse_delayed():
    single = delayed()
    double = single + 'bar'
    single.fill(double | 'foo')

    state = single('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    state = single('foobar')
    assert state.text == ''
    assert state.tree == ['foo', 'bar']

    with pytest.raises(ParseError):
        single('bar')

