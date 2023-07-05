import pytest
from comber import C, Id, Lit, Seq, Choice

def test_wrap():
    parser = C('foo')

    assert Id(Lit('foo')) == parser

def test_seq():
    parser = C + 'foo' + 'bar'

    assert Seq(Seq(C, Lit('foo')), Lit('bar')) == parser

def test_choice():
    parser = C('foo') | 'bar'

    assert Choice(Id(Lit('foo')), Lit('bar')) == parser
