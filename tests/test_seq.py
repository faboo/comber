import pytest
from comber import Seq, Lit, ParseError

def test_create():
    parser = Seq(Lit('foo'), Lit('bar'))
    assert (Lit('foo'), Lit('bar')) == parser.subparsers
    parser = Seq('foo', 'bar')
    assert (Lit('foo'), Lit('bar')) == parser.subparsers
    parser = Seq(Seq('foo', 'bar'), 'baz')
    assert (Lit('foo'), Lit('bar'), Lit('baz')) == parser.subparsers

def test_expect():
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

