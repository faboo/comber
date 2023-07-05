import pytest
from comber import Choice, Lit, ParseError

def test_create():
    parser = Choice(Lit('foo'), Lit('bar'))
    assert [Lit('foo'), Lit('bar')] == parser.subparsers
    parser = Choice('foo', 'bar')
    assert [Lit('foo'), Lit('bar')] == parser.subparsers
    parser = Choice(Choice('foo', 'bar'), 'baz')
    assert [Lit('foo'), Lit('bar'), Lit('baz')] == parser.subparsers

def test_expect():
    parser = Choice('foo', 'bar')
    assert ['foo', 'bar'] == parser.expect()

def test_parse():
    parser = Choice('foo', 'bar')
    parser.parse('foo')
    parser.parse('bar')

    with pytest.raises(ParseError):
        parser.parse('baz')

