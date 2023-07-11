import pytest
from comber import cs, ParseError

def test_create():
    cs('fo')
    cs(['foo', 'bar'])

def test_expect():
    assert set(['f', 'o']) == set(cs('foo').expect())

def test_parse():
    parser = cs(' \n')

    state = parser.parse(' foo', whitespace=None)
    assert state.text == 'foo'
    assert state.tree == [' ']

    with pytest.raises(ParseError):
        parser.parse('foo')

