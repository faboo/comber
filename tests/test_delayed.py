import pytest
from comber import delayed, ParseError, Lit

def test_create():
    parser = delayed()
    parser.fill('foo')

def test_expect():
    parser = delayed()
    parser.fill(Lit('foo'))
    assert parser.expect() == Lit('foo').expect()

def test_parse():
    parser = delayed()
    parser.fill(Lit('foo'))

    state = parser.parse('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    with pytest.raises(ParseError):
        parser.parse('bar')

