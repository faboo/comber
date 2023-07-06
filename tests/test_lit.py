import pytest
from comber import Lit, ParseError

def test_create():
    Lit('foo')

def test_expect():
    assert ['foo'] == Lit('foo').expect()

def test_parse():
    parser = Lit('foo')

    state = parser.parse('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    state = parser.parse('foobar')
    assert state.text == 'bar'
    assert state.tree == ['foo']

    with pytest.raises(ParseError):
        parser.parse('bar')
