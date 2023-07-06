import pytest
from comber import C, Id, Lit, Seq, Choice, Repeat, inf

def test_wrap():
    parser = C('foo')

    assert Id(Lit('foo')) == parser

def test_seq():
    parser = C + 'foo' + 'bar'

    assert Seq(Seq(C, Lit('foo')), Lit('bar')) == parser

def test_choice():
    parser = C('foo') | 'bar'

    assert Choice(Id(Lit('foo')), Lit('bar')) == parser

    parser = C('foo') | 'bar' | 'baz'

    assert Choice(Choice(Id(Lit('foo')), Lit('bar')), Lit('baz')) == parser

def test_name():
    parser = (C('foo') | 'bar')@'baz'
    assert parser.name == 'baz'
    assert parser.expectCore() == ['baz']

def test_intern():
    class Eval:
        def __init__(self, args):
            self.args = args
    parser = (C + 'foo' + 'bar')@('baz', Eval)
    assert parser.name == 'baz'
    assert parser.intern == Eval
    state = parser.parse('foobar')
    value = state.tree[0]
    assert value.args == ['foo', 'bar']

def test_optional():
    parser = ~Lit('foo')
    assert Repeat(Lit('foo'), 0, 1) == parser

def test_repeat():
    parser = Lit('foo')[1]
    assert Repeat(Lit('foo'), 1, None) == parser

    parser = Lit('foo')[1, 3]
    assert Repeat(Lit('foo'), 1, 3) == parser

    parser = Lit('foo')[1, inf]
    assert Repeat(Lit('foo'), 1, inf) == parser
