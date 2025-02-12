import pytest
from comber import C, Repeat, Lit, ParseError, inf

def test_create():
    parser = Repeat(Lit('foo'), 0, 1, None)
    assert Lit('foo') == parser.subparser
    assert 0 == parser.minimum
    assert 1 == parser.maximum

def test_repeat_repr():
    assert str(Repeat(Lit('foo'), 0, 1, ',')) == \
        'Repeat(Lit(foo), 0, 1, Lit(,))'

def test_expect():
    parser = Repeat(Lit('foo'), 0, 1, None)
    assert ['foo'] == parser.expectCore()

def test_parse_exact():
    parser = Repeat(Lit('foo'), 2, None, None)
    state = parser('foofoo')
    assert state.text == ''
    assert state.tree == ['foo', 'foo']

    with pytest.raises(ParseError):
        parser('foo')

def test_parse_minimum_separator():
    parser = Repeat(Lit('foo'), 2, None, ',')
    state = parser('foo, foo')
    assert state.text == ''
    assert state.tree == ['foo', ',', 'foo']

    with pytest.raises(ParseError):
        parser('foo')

def test_parse_optional():
    parser = Repeat(Lit('foo'), 0, 1, None)
    state = parser('foo')
    assert state.text == ''
    assert state.tree == ['foo']
    state = parser('bar')
    assert state.text == 'bar'
    assert state.tree == []

def test_parse_with_max():
    parser = Repeat(Lit('foo'), 1, 2, None)
    state = parser('foo')
    assert state.text == ''
    assert state.tree == ['foo']
    state = parser('foobar')
    assert state.text == 'bar'
    assert state.tree == ['foo']
    state = parser('foofoo')
    assert state.text == ''
    assert state.tree == ['foo', 'foo']
    state = parser('foofoofoo')
    assert state.text == 'foo'
    assert state.tree == ['foo', 'foo']

    with pytest.raises(ParseError):
        parser('baz')

    with pytest.raises(ParseError):
        parser('')

def test_parse_inf():
    parser = Repeat(Lit('foo'), 0, inf, None)
    state = parser('foo')
    assert state.text == ''
    assert state.tree == ['foo']
    state = parser('foofoo')
    assert state.text == ''
    assert state.tree == ['foo', 'foo']
    state = parser('foofoofoo')
    assert state.text == ''
    assert state.tree == ['foo', 'foo', 'foo']
    state = parser('foofoobarfoo')
    assert state.text == 'barfoo'
    assert state.tree == ['foo', 'foo']

def test_parse_bracketed():
    parser = C + '[' + Lit('foo')[0, inf, None] + ']'

    state = parser('[ foo ]')
    assert state.text == ''
    assert state.tree == ['[', 'foo', ']']

def test_parse_bracketed_seperated():
    parser = C + '[' + Lit('foo')[0, inf, ','] + ']'

    state = parser('[ ]')
    assert state.text == ''
    assert state.tree == ['[', ']']

    state = parser('[ foo ]')
    assert state.text == ''
    assert state.tree == ['[', 'foo', ']']

    state = parser('[ foo, foo ]')
    assert state.text == ''
    assert state.tree == ['[', 'foo', ',', 'foo', ']']
