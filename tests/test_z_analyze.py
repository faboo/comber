import pytest
from comber import defer, ParseError, Lit
from comber.combinator import Choice

def test_analyze_choice():
    single = defer()
    double = single + 'bar'
    single.fill(double | 'foo')
    grammar = single | 'baz'

    assert isinstance(grammar.subparsers[0], defer)
    grammar.analyze()
    assert isinstance(grammar.subparsers[0], Choice)


def test_analyze_repeat():
    single = defer()
    double = single + 'bar'
    single.fill(double | 'foo')
    grammar = single*','

    assert isinstance(grammar.subparser, defer)
    grammar.analyze()
    assert isinstance(grammar.subparser, Choice)


def test_analyze_deep():
    single = defer()
    double = single + 'bar'
    single.fill(double | 'foo' | single*',')
    grammar = single | 'baz'

    assert isinstance(grammar.subparsers[0], defer)
    grammar.analyze()
    assert isinstance(grammar.subparsers[0], Choice)
