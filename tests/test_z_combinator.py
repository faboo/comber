import pytest
from comber import C, Id, Lit, Seq, Choice, Repeat, inf, EndOfInputError

def test_wrap():
    parser = C('foo')

    assert Id(Lit('foo')) == parser


def test_eof():
    parser = C('foo')

    with pytest.raises(EndOfInputError):
        parser.parse('')


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

    parser = (C('foo') | 'bar')@('baz')
    assert parser.name == 'baz'
    assert parser.expectCore() == ['baz']

    with pytest.raises(TypeError):
        C('foo')@12

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
    assert Repeat(Lit('foo'), 0, 1, None) == parser

def test_repeat():
    parser = Lit('foo')[1]
    assert Repeat(Lit('foo'), 1, None, None) == parser

    parser = Lit('foo')[1, 3]
    assert Repeat(Lit('foo'), 1, 3, None) == parser

    parser = Lit('foo')[1, inf]
    assert Repeat(Lit('foo'), 1, inf, None) == parser

def test_space_eating():
    parser = C+ 'foo' + 'bar'
    state = parser.parse('foo bar')
    assert state.text == ''
    assert state.tree == ['foo', 'bar']
