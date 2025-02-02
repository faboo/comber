"""
Additional non-core parsers.
"""
import logging
from typing import Iterable, List, Optional, Any
import re
from .parser import State, Expect
from .combinator import Combinator, asCombinator

#pylint: disable=invalid-name
class cs(Combinator):
    """
    Parse one of a list of strings, or one of a character in a string.
    """
    def __init__(self, string:Iterable) -> None:
        super().__init__()
        self.string = set(string)

    def expect(self, state:Expect) -> List[str]:
        return list(self.string)

    def recognize(self, state:State) -> Optional[State]:
        for string in self.string:
            if state.text.startswith(string):
                state.consume(len(string))
                return state

        return None

    def __eq__(self, right:Any) -> bool:
        return isinstance(right, cs) and right.string == self.string

    def __hash__(self) -> int:
        return hash(self.string)

    def repr(self) -> str:
        return f'cs({self.string})'


#pylint: disable=invalid-name
class rs(Combinator):
    """
    Parse using a regular expression
    """
    def __init__(self, regex:str, caseInsensitive=False) -> None:
        super().__init__()
        self.raw = regex
        self.regex = re.compile(
            self.raw,
            re.IGNORECASE if caseInsensitive else 0)

    def expect(self, state:Expect) -> List[str]:
        return [self.raw]

    def recognize(self, state:State) -> Optional[State]:
        matched = self.regex.match(state.text)
        if matched:
            state.consume(len(matched.group(0)))
            return state

        return None

    def __eq__(self, right:Any) -> bool:
        return isinstance(right, rs) and right.raw == self.raw and right.regex.flags == self.regex.flags

    def __hash__(self) -> int:
        return hash(self.raw)

    def repr(self) -> str:
        return f'rs({self.raw})'


#pylint: disable=invalid-name
class delayed(Combinator):
    """
    A placeholder parser that can be filled in later with another parser.
    Useful for recusive definitions.
    """
    def __init__(self) -> None:
        super().__init__()
        self._subparser:Optional[Combinator] = None

    @property
    def subparser(self) -> Combinator:
        """
        The parser this delayed parser is the stand-in for.
        """
        if self._subparser is None:
            message = 'Unfulfilled delay parser'
            if self.name:
                message += f' ({self.name})'
            #pylint: disable=broad-exception-raised
            raise Exception(message)

        return self._subparser

    def fill(self, subparser:Combinator) -> None:
        """
        Fill in the parser for this delayed parser.
        """
        self._subparser = asCombinator(subparser)

    def expect(self, state:Expect) -> List[str]:
        return self.subparser.expect(state)

    def recognize(self, state:State) -> Optional[State]:
        logging.info('Delayed parse')
        return self.subparser.parseCore(state)

    def __eq__(self, right:Any) -> bool:
        return isinstance(right, delayed) and right._subparser == self._subparser

    def __hash__(self) -> int:
        return hash(self._subparser)

    def repr(self) -> str:
        return f'delayed({self._subparser})'

