import pytest
from comber import rs, ParseError

def test_create():
    rs('foo')
    rs('foo', True)
    assert rs('foo', True) != rs('foo', False)

def test_expect():
    assert ['foo'] == rs('foo').expectCore()

def test_parse():
    parser = rs('[_a-z][a-z]*')

    state = parser.parse('foo')
    assert state.text == ''
    assert state.tree == ['foo']
    state = parser.parse('foo 123')
    assert state.text == '123'
    assert state.tree == ['foo']

    with pytest.raises(ParseError):
        parser.parse('123')


