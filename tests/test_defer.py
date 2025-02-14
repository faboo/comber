import pytest
from comber import defer, ParseError, Lit

def test_defer_create():
    parser = defer()
    parser.fill('foo')

def test_defer_unfilled():
    parser = defer()

    with pytest.raises(Exception):
        parser('foo')

    parser = defer()@'bar'

    with pytest.raises(Exception):
        parser('foo')

def test_defer_repr():
    parser = defer()

    assert str(parser) == 'defer(None)'

    parser.fill('foo')

    assert str(parser) == 'defer(Lit(foo))'
    

def test_defer_expect():
    parser = defer()
    parser.fill(Lit('foo'))
    assert parser.expectCore() == Lit('foo').expectCore()

def test_defer_parse():
    parser = defer()
    parser.fill(Lit('foo'))

    state = parser('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    with pytest.raises(ParseError):
        parser('bar')

def test_defer_recurse():
    single = defer()
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

