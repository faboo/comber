import pytest
from comber import Choice, Repeat, Lit, ParseError


def test_repr():
    grammar = Choice(Lit('foo'), Lit('bar'))

    assert repr(grammar) == 'Choice(Lit(foo), Lit(bar))'

    grammar = Choice(Lit('foo'), Lit('bar'))@'qux'

    assert repr(grammar) == '@qux'

def test_exception_message():
    grammar = Choice(Lit('foo'), Lit('bar'))

    try:
        grammar('qux')
    except ParseError as ex:
        assert str(ex) in \
            ('1:1: Unexpected text: qux. Expected one of: foo, bar'
            ,'1:1: Unexpected text: qux. Expected one of: bar, foo'
            )

def test_mid_parse_error():
    grammar = Choice(Repeat(Lit('foo'), 2, 5, ','), Lit('bar'))

    with pytest.raises(ParseError):
        grammar('foo')
