import pytest
from comber import Repeat, Lit, ParseError, inf

def test_create():
    parser = Repeat(Lit('foo'), 0, 1)
    assert Lit('foo') == parser.subparser
    assert 0 == parser.minimum
    assert 1 == parser.maximum

def test_expect():
    parser = Repeat(Lit('foo'), 0, 1)
    assert ['foo'] == parser.expect()

def test_parse_exact():
    parser = Repeat(Lit('foo'), 2, None)
    state = parser.parse('foofoo')
    assert state.text == ''
    assert state.tree == ['foo', 'foo']

    with pytest.raises(ParseError):
        parser.parse('foo')

def test_parse_optional():
    parser = Repeat(Lit('foo'), 0, 1)
    state = parser.parse('foo')
    assert state.text == ''
    assert state.tree == ['foo']
    state = parser.parse('bar')
    assert state.text == 'bar'
    assert state.tree == []

def test_parse_with_max():
    parser = Repeat(Lit('foo'), 1, 2)
    state = parser.parse('foo')
    assert state.text == ''
    assert state.tree == ['foo']
    state = parser.parse('foobar')
    assert state.text == 'bar'
    assert state.tree == ['foo']
    state = parser.parse('foofoo')
    assert state.text == ''
    assert state.tree == ['foo', 'foo']
    state = parser.parse('foofoofoo')
    assert state.text == 'foo'
    assert state.tree == ['foo', 'foo']

    with pytest.raises(ParseError):
        parser.parse('baz')

    with pytest.raises(ParseError):
        parser.parse('')

def test_parse_inf():
    parser = Repeat(Lit('foo'), 0, inf)
    state = parser.parse('foo')
    assert state.text == ''
    assert state.tree == ['foo']
    state = parser.parse('foofoo')
    assert state.text == ''
    assert state.tree == ['foo', 'foo']
    state = parser.parse('foofoofoo')
    assert state.text == ''
    assert state.tree == ['foo', 'foo', 'foo']
    state = parser.parse('foofoobarfoo')
    assert state.text == 'barfoo'
    assert state.tree == ['foo', 'foo']
