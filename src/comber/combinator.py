"""
Combinator definitions.
"""
from typing import Optional, Tuple, List, Union, Any
from abc import ABC
from .parser import Parser, State, Intern

Parseable = Union['Combinator', str]

class Combinator(Parser, ABC):
    """
    Combinator definitions.
    """

    def __matmul__(self, arg:Union[str, Tuple[str, Intern]]) -> 'Combinator':
        if isinstance(arg, str):
            self.name = arg
        elif isinstance(arg, tuple):
            self.name = arg[0]
            self.intern = arg[1]
        else:
            raise TypeError(
                'Expected name or name-internalizer tuple, e.g. '\
                'combinator@"name" or combinator@("name, lambda x: int(x)"')

        return self

    def __add__(self, right:Parseable) -> Parseable:
        return Seq(self, right)

    def __or__(self, right:Parseable) -> Parseable:
        return Choice(self, right)


class Lit(Combinator):
    """
    A parser of an exact string
    """
    def __init__(self, string:str) -> None:
        super().__init__()
        self.string = string

    def expect(self) -> List[str]:
        return [self.string]

    def parseString(self, state:State) -> Optional[State]:
        if not state.text.startswith(self.string):
            return None

        return state.consume(len(self.string))

    def __eq__(self, right:Any) -> bool:
        return isinstance(right, Lit) and right.string == self.string

    def __hash__(self) -> int:
        return hash(self.string)

    def __repr__(self) -> str:
        return f'Lit({self.string})'


def asCombinator(arg:Parseable) -> Combinator:
    """
    Ensure a value is a Combinator
    """
    if isinstance(arg, Combinator):
        return arg
    else:
        return Lit(arg)


class Seq(Combinator):
    """
    A sequence of parsers.
    """
    def __init__(self, left:Parseable, right:Parseable) -> None:
        super().__init__()
        self.subparsers:List[Combinator] = left.subparsers \
            if isinstance(left, Seq) \
            else [asCombinator(left)]

        self.subparsers.append(asCombinator(right))

    def expect(self) -> List[str]:
        return self.subparsers[0].expect()

    def parseString(self, state:State) -> Optional[State]:
        for parser in self.subparsers:
            newState = parser.parseBase(state)
            if not newState:
                return None
            state = newState

        return state

    def __add__(self, right:Parseable) -> Parseable:
        self.subparsers.append(asCombinator(right))
        return self

    def __eq__(self, right:Any) -> bool:
        return isinstance(right, Seq) and right.subparsers == self.subparsers

    def __hash__(self) -> int:
        return hash(self.subparsers)

    def __repr__(self) -> str:
        return f'Seq({self.subparsers})'


class Choice(Combinator):
    """
    Parse as the first successful parse.
    """
    def __init__(self, left:Parseable, right:Parseable) -> None:
        super().__init__()
        self.subparsers:List[Combinator] = left.subparsers \
            if isinstance(left, Choice) \
            else [asCombinator(left)]

        self.subparsers.append(asCombinator(right))

    def expect(self) -> List[str]:
        return \
            [ string
              for subparser in self.subparsers
              for string in subparser.expect()
            ]

    def parseString(self, state:State) -> Optional[State]:
        for parser in self.subparsers:
            newState = parser.parseBase(state)

            if newState:
                return newState

        return None

    def __or__(self, right:Parseable) -> Parseable:
        self.subparsers.append(asCombinator(right))
        return self

    def __eq__(self, right:Any) -> bool:
        return isinstance(right, Choice) and right.subparsers == self.subparsers

    def __hash__(self) -> int:
        return hash(self.subparsers)

    def __repr__(self) -> str:
        return f'Choice({self.subparsers})'


class Id(Combinator):
    """
    Parse exactly the subparser.
    """
    def __init__(self, subparser:Parseable) -> None:
        super().__init__()
        self.subparser = asCombinator(subparser)


    def expect(self) -> List[str]:
        return self.subparser.expect()


    def parseString(self, state:State) -> Optional[State]:
        return self.subparser.parseBase(state)

    def __eq__(self, right:Any) -> bool:
        return isinstance(right, Id) and right.subparser == self.subparser

    def __hash__(self) -> int:
        return hash(self.subparser)

    def __repr__(self) -> str:
        return f'Id({self.subparser})'


class CClass(Combinator):
    """
    The combinator start's class. Don't instantiate.
    """
    def expect(self) -> List[str]:
        return []

    def parseString(self, state:State) -> Optional[State]:
        return state

    def __call__(self, *args:Parseable) -> Id:
        return Id(args[0])

    def __repr__(self) -> str:
        return 'C'


C = CClass()
