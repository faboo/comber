import pytest
from comber import Lit, ParseError

def test_create():
    Lit('foo')

def test_expect():
    assert ['foo'] == Lit('foo').expect()

def test_parse():
    parser = Lit('foo')

    parser.parse('foo')
    parser.parse('foobar')

    with pytest.raises(ParseError):
        parser.parse('bar')
