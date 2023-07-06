from typing import Iterable, List, Optional, Any
import re
from .parser import State
from .combinator import Combinator

class cs(Combinator):
    """
    Parse one of a list of strings, or one of a character in a string.
    """
    def __init__(self, string:Iterable) -> None:
        super().__init__()
        self.string = set(string)

    def expect(self) -> List[str]:
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

    def __repr__(self) -> str:
        return f'cs({self.string})'


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

    def expect(self) -> List[str]:
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

    def __repr__(self) -> str:
        return f'rs({self.raw})'
