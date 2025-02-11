import pytest
from comber import C, Id, Lit, Seq, Choice, Repeat, inf, EndOfInputError

def test_wrap():
    parser = C('foo')

    assert Id(Lit('foo')) == parser


def test_eof():
    parser = C('foo')

    with pytest.raises(EndOfInputError):
        parser('')


def test_seq():
    parser = C + 'foo' + 'bar'

    assert parser.subparsers == (Lit('foo'), Lit('bar'))
    #assert Seq(Seq(C, Lit('foo')), Lit('bar')) == parser

def test_choice():
    parser = C('foo') | 'bar'

    assert parser.subparsers == (Id(Lit('foo')), Lit('bar'))

    parser = C('foo') | 'bar' | 'baz'

    assert parser.subparsers == (Id(Lit('foo')), Lit('bar'), Lit('baz'))

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
    state = parser('foobar')
    value = state.tree[0]
    assert value.args == ['foo', 'bar']

def test_optional():
    parser = ~Lit('foo')
    repeated = Repeat(Lit('foo'), 0, 1, None)
    assert repeated.subparser == parser.subparser
    assert repeated.minimum == parser.minimum
    assert repeated.maximum == parser.maximum 
    assert repeated.separator == parser.separator

def test_zero_or_more():
    parser = +Lit('foo')
    repeated = Repeat(Lit('foo'), 0, inf, None)
    assert repeated.subparser == parser.subparser
    assert repeated.minimum == parser.minimum
    assert repeated.maximum == parser.maximum 
    assert repeated.separator == parser.separator

def test_zero_or_more():
    parser = Lit('foo')*','
    repeated = Repeat(Lit('foo'), 0, inf, ',')
    assert repeated.subparser == parser.subparser
    assert repeated.minimum == parser.minimum
    assert repeated.maximum == parser.maximum 
    assert repeated.separator == parser.separator

def test_repeat():
    parser = Lit('foo')[1]
    repeated = Repeat(Lit('foo'), 1, None, None)
    assert repeated.subparser == parser.subparser
    assert repeated.minimum == parser.minimum
    assert repeated.maximum == parser.maximum 

    parser = Lit('foo')[1, 3]
    repeated = Repeat(Lit('foo'), 1, 3, None)
    assert repeated.subparser == parser.subparser
    assert repeated.minimum == parser.minimum
    assert repeated.maximum == parser.maximum 

    parser = Lit('foo')[1, inf]
    repeated = Repeat(Lit('foo'), 1, inf, None)
    assert repeated.subparser == parser.subparser
    assert repeated.minimum == parser.minimum
    assert repeated.maximum == parser.maximum 

def test_space_eating():
    parser = C+ 'foo' + 'bar'
    state = parser('foo bar')
    assert state.text == ''
    assert state.tree == ['foo', 'bar']
