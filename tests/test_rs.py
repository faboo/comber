import pytest
from comber import rs, ParseError

def test_create():
    rs('foo')
    rs('foo', True)
    assert rs('foo', True) != rs('foo', False)

def test_expect():
    assert ['/foo/'] == rs('foo').expectCore()

def test_rs_repr():
    assert str(rs('foo')) == 'rs(foo)'

def test_parse():
    parser = rs('[_a-z][a-z]*')

    state = parser('foo')
    assert state.text == ''
    assert state.tree == ['foo']
    state = parser('foo 123')
    assert state.text == '123'
    assert state.tree == ['foo']

    with pytest.raises(ParseError):
        parser('123')

def test_emit():
    def emitter(string):
        nonlocal called
        called = True
        return string
    called = False
    parser = rs('foo')@emitter
    
    parser('foo')
    assert called

    called = False
    parser = (rs('foo')@emitter)[0, 2]
    
    parser('foo')
    assert called
