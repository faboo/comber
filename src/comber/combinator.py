"""
Combinator definitions.
"""
from typing import cast, Optional, Tuple, List, Union, Any
import weakref
from abc import ABC
from .parser import Parser, State, Expect, Intern, ParseError

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

    def __getitem__(self, args:Union[int,Tuple[int,int],Tuple[int,int,Parseable]]) -> 'Combinator':
        minimum = args if isinstance(args, int) else args[0]
        maximum = None if isinstance(args, int) else args[1]
        separator = None if isinstance(args, int) or len(args) < 3 else cast(Tuple[int,int,Parseable], args)[2]
        return Repeat(self, minimum, maximum, separator)

    def __invert__(self) -> 'Combinator':
        return Repeat(self, 0, 1, None)


class Lit(Combinator):
    """
    A parser of an exact string
    """
    instances:weakref.WeakValueDictionary[str,'Lit'] = weakref.WeakValueDictionary()

    def __new__(cls, string:str) -> 'Lit':
        if string not in cls.instances:
            instance = super().__new__(cls)
            cls.__init__(instance, string)
            cls.instances[string] = instance
        else:
            instance = cls.instances[string]

        return instance

    def __init__(self, string:str) -> None:
        super().__init__()
        self.string = string
        self._hash = hash(string)

    def expect(self, state:Expect) -> List[str]:
        return [self.string]

    def recognize(self, state:State) -> Optional[State]:
        if not state.text.startswith(self.string):
            return None

        state.consume(len(self.string))
        return state

    #def __eq__(self, right:Any) -> bool:
    #    return isinstance(right, Lit) and right.string == self.string

    def __hash__(self) -> int:
        return self._hash

    def repr(self) -> str:
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
        self.subparsers:tuple[Combinator, ...]

        if isinstance(left, Seq):
            subparsers = list(left.subparsers)
            subparsers.append(asCombinator(right))
            self.subparsers = tuple(subparsers)
        else:
            if left is not C:
                self.subparsers = (asCombinator(left), asCombinator(right))
            else:
                self.subparsers = (asCombinator(right), )

        self._hash:int = hash(self.subparsers)

    def expect(self, state:Expect) -> List[str]:
        return self.subparsers[0].expectCore(state)

    def recognize(self, state:State) -> Optional[State]:
        first = True
        for parser in self.subparsers:
            try:
                if not first:
                    state.shiftParser()
                state = parser.parseCore(state)
            finally:
                if not first:
                    state.unshiftParser()

            first = False

        return state

    def __add__(self, right:Parseable) -> Parseable:
        subparsers = list(self.subparsers)
        subparsers.append(asCombinator(right))
        self.subparsers = tuple(subparsers)
        self._hash = hash(self.subparsers)
        return self

    #def __eq__(self, right:Any) -> bool:
    #    return isinstance(right, Seq) and right.subparsers == self.subparsers

    def __hash__(self) -> int:
        return self._hash

    def repr(self) -> str:
        return f'Seq({self.subparsers})'


class Choice(Combinator):
    """
    Parse as the first successful parse.
    """
    recurse = True
    def __init__(self, left:Parseable, right:Parseable) -> None:
        super().__init__()
        self.subparsers:tuple[Combinator, ...]

        if isinstance(left, Choice):
            subparsers = list(left.subparsers)
            subparsers.append(asCombinator(right))
            self.subparsers = tuple(subparsers)
        else:
            if left is not C:
                self.subparsers = (asCombinator(left), asCombinator(right))
            else:
                self.subparsers = (asCombinator(right), )

        self._hash:int = hash(self.subparsers)

    def expect(self, state:Expect) -> List[str]:
        return \
            [ string
              for subparser in self.subparsers
              for string in subparser.expectCore(state)
            ]

    def recognize(self, state:State) -> Optional[State]:
        lastParser = None
        bestMatch = None

        for parser in self.subparsers:
            try:
                trialState = state.pushState()
                trialState = parser.parseCore(trialState, False)
                if bestMatch is None or len(trialState.text) < len(bestMatch.text):
                    bestMatch = trialState
                    lastParser = parser
                    break
            except ParseError as ex:
                continue

        if bestMatch:
            state = bestMatch.popState()
            return state
        return None

    def __or__(self, right:Parseable) -> Parseable:
        subparsers = list(self.subparsers)
        subparsers.append(asCombinator(right))
        self.subparsers = tuple(subparsers)
        self._hash = hash(self.subparsers)
        return self

    #def __eq__(self, right:Any) -> bool:
    #    return isinstance(right, Choice) and right.subparsers == self.subparsers

    def __hash__(self) -> int:
        return self._hash

    def repr(self) -> str:
        return f'Choice({self.subparsers})'


class Repeat(Combinator):
    """
    Repeat a combinator.
    """
    def __init__(self, subparser:Combinator, minimum:int, maximum:Optional[int], separator:Optional[Parseable]) -> None:
        super().__init__()
        self.subparser = subparser
        self.minimum = minimum
        self.maximum = maximum
        self.separator = None if separator is None else asCombinator(separator)

    def expect(self, state:Expect) -> List[str]:
        return self.subparser.expectCore(state)

    def recognize(self, state:State) -> Optional[State]:
        parsed = 0

        while parsed < self.minimum:
            if parsed > 0 and self.separator:
                state = self.separator.parseCore(state)
            state = self.subparser.parseCore(state)
            parsed += 1

        if parsed < self.minimum:
            return None

        if self.maximum is not None:
            while parsed < self.maximum:
                try:
                    trialState = state.pushState()

                    if parsed > 0 and self.separator:
                        trialState = self.separator.parseCore(trialState)

                    trialState = self.subparser.parseCore(trialState)
                    state = trialState.popState()
                    parsed += 1
                except ParseError:
                    break

        return state

    def __eq__(self, right:Any) -> bool:
        return isinstance(right, Repeat) \
            and right.subparser == self.subparser \
            and right.minimum == self.minimum \
            and right.maximum == self.maximum

    def __hash__(self) -> int:
        return hash(hash(self.subparser)+hash(self.minimum)+hash(self.maximum))

    def repr(self) -> str:
        return f'Repeat({self.subparser}, {self.minimum}, {self.maximum})'


class Id(Combinator):
    """
    Parse exactly the subparser.
    """
    def __init__(self, subparser:Parseable) -> None:
        super().__init__()
        self.subparser = asCombinator(subparser)


    def expect(self, state:Expect) -> List[str]:
        return self.subparser.expectCore(state)


    def recognize(self, state:State) -> Optional[State]:
        return self.subparser.parseCore(state)

    def __eq__(self, right:Any) -> bool:
        return isinstance(right, Id) and right.subparser == self.subparser

    def __hash__(self) -> int:
        return hash(self.subparser)

    def repr(self) -> str:
        return f'Id({self.subparser})'


class CClass(Combinator):
    """
    The combinator start's class. Don't instantiate.
    """
    def expect(self, state:Expect) -> List[str]:
        return []

    def recognize(self, state:State) -> Optional[State]:
        return state

    def __call__(self, arg:Parseable) -> Id:
        return Id(arg)

    def repr(self) -> str:
        return 'C'


C = CClass()
