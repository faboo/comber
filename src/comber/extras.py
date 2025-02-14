"""
Additional non-core parsers.
"""
from typing import Iterable, List, Optional
import re
from .parser import State, Expect
from .combinator import Combinator, asCombinator

#pylint: disable=invalid-name
class cs(Combinator):
    """
    Parse one of a list of strings, or one of a character in a string.
    """
    recurse = True # As an optimization - there's no way cs can recurse, so don't check

    def __init__(self, string:Iterable) -> None:
        super().__init__()
        self.string = tuple(set(string))

    def expect(self, state:Expect) -> List[str]:
        return list(self.string)

    def recognize(self, state:State) -> Optional[State]:
        for string in self.string:
            if state.text.startswith(string):
                state.consume(len(string))
                return state

        return None

    def __hash__(self) -> int:
        return hash(self.string)

    def repr(self) -> str:
        return f'cs({self.string})'


#pylint: disable=invalid-name
class rs(Combinator):
    """
    Parse using a regular expression
    """
    recurse = True # As an optimization - there's no way rs can recurse, so don't check

    def __init__(self, regex:str, caseInsensitive=False) -> None:
        super().__init__()
        self.raw = regex
        self.regex = re.compile(
            self.raw,
            re.IGNORECASE if caseInsensitive else 0)

    def expect(self, state:Expect) -> List[str]:
        return [f'/{self.raw}/']

    def recognize(self, state:State) -> Optional[State]:
        matched = self.regex.match(state.text)
        if matched:
            state.consume(len(matched[0]))
            return state

        return None

    def __hash__(self) -> int:
        return hash(self.raw)

    def repr(self) -> str:
        return f'rs({self.raw})'


#pylint: disable=invalid-name
class defer(Combinator):
    """
    A placeholder parser that can be filled in later with another parser.
    Useful for recusive definitions.
    """
    recurse = False
    compound = True

    def __init__(self) -> None:
        super().__init__()
        self._coreparser:Optional[Combinator] = None

    @property
    def coreparser(self) -> Combinator:
        """
        The parser this defer parser is the stand-in for.
        """
        if self._coreparser is None:
            message = 'Unfulfilled defer parser'
            if self.name:
                message += f' ({self.name})'
            #pylint: disable=broad-exception-raised
            raise Exception(message)

        return self._coreparser

    def fill(self, coreparser:Combinator) -> None:
        """
        Fill in the parser for this deferred parser.
        """
        self._coreparser = asCombinator(coreparser)

    def expect(self, state:Expect) -> List[str]:
        return self.coreparser.expect(state)

    def recognize(self, state:State) -> Optional[State]:
        raise NotImplementedError('Deferred parsers have no recogizer')

    def parseCore(self, state:State) -> State:
        return self.coreparser.parseCore(state)

    def simplify(self) -> Combinator:
        return self.coreparser

    def __hash__(self) -> int:
        # Where we care about this, we care about literal identity
        return hash(id(self))

    def repr(self) -> str:
        return f'defer({self._coreparser})'

