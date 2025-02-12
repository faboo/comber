import pytest
from comber import delayed, ParseError, Lit
from comber.combinator import Choice

def test_analyze_choice():
    single = delayed()
    double = single + 'bar'
    single.fill(double | 'foo')
    grammar = single | 'baz'

    assert isinstance(grammar.subparsers[0], delayed)
    grammar.analyze()
    assert isinstance(grammar.subparsers[0], Choice)


def test_analyze_repeat():
    single = delayed()
    double = single + 'bar'
    single.fill(double | 'foo')
    grammar = single*','

    assert isinstance(grammar.subparser, delayed)
    grammar.analyze()
    assert isinstance(grammar.subparser, Choice)


def test_analyze_deep():
    single = delayed()
    double = single + 'bar'
    single.fill(double | 'foo' | single*',')
    grammar = single | 'baz'

    assert isinstance(grammar.subparsers[0], delayed)
    grammar.analyze()
    assert isinstance(grammar.subparsers[0], Choice)
