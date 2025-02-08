import pytest
from comber import C, Choice, Lit, ParseError

def test_choice_create():
    parser = Choice(Lit('foo'), Lit('bar'))
    assert (Lit('foo'), Lit('bar')) == parser.subparsers
    parser = Choice('foo', 'bar')
    assert (Lit('foo'), Lit('bar')) == parser.subparsers
    parser = Choice(Choice('foo', 'bar'), 'baz')
    assert (Lit('foo'), Lit('bar'), Lit('baz')) == parser.subparsers
    parser = Choice(C, Lit('bar'))
    assert (Lit('bar'), ) == parser.subparsers

def test_choice_repr():
    assert repr(Choice(Lit('foo'), Lit('bar'))) == 'Choice(Lit(foo), Lit(bar))'

def test_choice_expect():
    parser = Choice('foo', 'bar')
    assert ['foo', 'bar'] == parser.expectCore()

def test_choice_parse():
    parser = Choice('foo', 'bar')
    state = parser('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    state = parser('bar')
    assert state.text == ''
    assert state.tree == ['bar']

    with pytest.raises(ParseError):
        parser('baz')

def test_choice_parse_with_backtrack():
    parser = Choice(C+'bar'+'foo', C+'bar'+'foo'+'baz')
    state = parser('bar foo')
    assert state.text == ''
    assert state.tree == ['bar', 'foo']
