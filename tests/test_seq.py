import pytest
from comber import Seq, Lit, ParseError

def test_create():
    parser = Seq(Lit('foo'), Lit('bar'))
    assert [Lit('foo'), Lit('bar')] == parser.subparsers
    parser = Seq('foo', 'bar')
    assert [Lit('foo'), Lit('bar')] == parser.subparsers
    parser = Seq(Seq('foo', 'bar'), 'baz')
    assert [Lit('foo'), Lit('bar'), Lit('baz')] == parser.subparsers

def test_expect():
    parser = Seq('foo', 'bar')
    assert ['foo'] == parser.expect()

def test_parse():
    parser = Seq('foo', 'bar')
    state = parser.parse('foobar')
    assert state.text == ''
    assert state.tree == ['foo', 'bar']

    with pytest.raises(ParseError):
        parser.parse('foo')

    with pytest.raises(ParseError):
        parser.parse('bar')

