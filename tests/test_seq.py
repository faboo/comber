import pytest
from comber import Seq, Lit, ParseError

def test_seq_create():
    parser = Seq(Lit('foo'), Lit('bar'))
    assert (Lit('foo'), Lit('bar')) == parser.subparsers
    parser = Seq('foo', 'bar')
    assert (Lit('foo'), Lit('bar')) == parser.subparsers
    parser = Seq(Seq('foo', 'bar'), 'baz')
    assert (Lit('foo'), Lit('bar'), Lit('baz')) == parser.subparsers

def test_seq_repr():
    assert repr(Seq('foo', 'bar')) == 'Seq(Lit(foo), Lit(bar))'

def test_seq_expect():
    parser = Seq('foo', 'bar')
    assert ['foo'] == parser.expectCore()

def test_parse_seq_success():
    parser = Seq('foo', 'bar')
    state = parser('foobar')
    assert state.text == ''
    assert state.tree == ['foo', 'bar']

def test_parse_seq_partial_success():
    parser = Seq('foo', 'bar')

    with pytest.raises(ParseError):
        parser('foo')

def test_parse_seq_dont_skip():
    parser = Seq('foo', 'bar')

    with pytest.raises(ParseError):
        parser('bar')

def test_parse_seq_emit():
    parser = Seq(Lit('1')@(int), Lit('2')@(int))

    assert parser('1 2').tree == [1, 2]
