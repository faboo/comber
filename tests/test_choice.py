import pytest
from comber import C, Choice, Lit, ParseError

def test_create():
    parser = Choice(Lit('foo'), Lit('bar'))
    assert (Lit('foo'), Lit('bar')) == parser.subparsers
    parser = Choice('foo', 'bar')
    assert (Lit('foo'), Lit('bar')) == parser.subparsers
    parser = Choice(Choice('foo', 'bar'), 'baz')
    assert (Lit('foo'), Lit('bar'), Lit('baz')) == parser.subparsers

def test_expect():
    parser = Choice('foo', 'bar')
    assert ['foo', 'bar'] == parser.expectCore()

def test_parse():
    parser = Choice('foo', 'bar')
    state = parser.parse('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    state = parser.parse('bar')
    assert state.text == ''
    assert state.tree == ['bar']

    with pytest.raises(ParseError):
        parser.parse('baz')

def test_parse_with_backtrack():
    parser = Choice(C+'bar'+'foo', C+'bar'+'foo'+'baz')
    state = parser.parse('bar foo')
    assert state.text == ''
    assert state.tree == ['bar', 'foo']
