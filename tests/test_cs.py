import pytest
from comber import cs, ParseError

def test_create():
    cs('fo')
    cs(['foo', 'bar'])

def test_expect():
    assert set(['f', 'o']) == set(cs('foo').expectCore())

def test_cs_repr():
    assert str(cs('f')) == "cs(('f',))"

def test_parse():
    parser = cs(' \n')
    parser.whitespace = None

    state = parser(' foo')
    assert state.text == 'foo'
    assert state.tree == [' ']

    with pytest.raises(ParseError):
        parser('foo')

