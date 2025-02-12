import pytest
from comber import delayed, ParseError, Lit

def test_delayed_create():
    parser = delayed()
    parser.fill('foo')

def test_delayed_unfilled():
    parser = delayed()

    with pytest.raises(Exception):
        parser('foo')

    parser = delayed()@'bar'

    with pytest.raises(Exception):
        parser('foo')

def test_delayed_repr():
    parser = delayed()

    assert str(parser) == 'delayed(None)'

    parser.fill('foo')

    assert str(parser) == 'delayed(Lit(foo))'
    

def test_delayed_expect():
    parser = delayed()
    parser.fill(Lit('foo'))
    assert parser.expectCore() == Lit('foo').expectCore()

def test_delayed_parse():
    parser = delayed()
    parser.fill(Lit('foo'))

    state = parser('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    with pytest.raises(ParseError):
        parser('bar')

def test_delayed_recurse():
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

