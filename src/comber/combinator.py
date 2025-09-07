"""
Combinator definitions.
"""
from typing import cast, Optional, Tuple, List, Union, Any
import weakref
from math import inf
from abc import ABC
from .parser import Parser, State, Expect, Emitter, ParseError

Parseable = Union['Combinator', str]

class Combinator(Parser, ABC):
    """
    Combinator definitions.
    """
    def __matmul__(self, arg:Union[str, Emitter, Tuple[str, Emitter]]) -> 'Combinator':
        if isinstance(arg, str):
            self.name = arg
        elif callable(arg):
            self.emit = arg
        elif isinstance(arg, tuple):
            self.name = arg[0]
            self.emit = arg[1]
        else:
            raise TypeError(
                'Expected name or name-emitter tuple, e.g. '\
                'combinator@"name", combinator@lambda x: int(x), or combinator@("name", lambda x: int(x)')

        return self

    def __add__(self, right:Parseable) -> Parseable:
        return Seq(self, right)

    def __or__(self, right:Parseable) -> Parseable:
        return Choice(self, right)

    def __getitem__(self, args:Union[int,Tuple[int,int|float],Tuple[int,int|float,Parseable]]) -> 'Combinator':
        minimum = args if isinstance(args, int) else args[0]
        maximum = None if isinstance(args, int) else args[1]
        separator = None if isinstance(args, int) or len(args) < 3 else cast(Tuple[int,int,Parseable], args)[2]
        return Repeat(self, minimum, maximum, separator)

    def __invert__(self) -> 'Combinator':
        return Repeat(self, 0, 1, None)

    def __pos__(self) -> 'Combinator':
        return Repeat(self, 0, inf, None)

    def __mul__(self, separator:Parseable) -> Parseable:
        return Repeat(self, 0, inf, separator)

    def simplify(self) -> 'Combinator':
        """ Return a simplified version of the combinator """
        return self

    def analyze(self) -> None:
        analyzed:set[Combinator] = set()
        parsers:list[Combinator] = [self]

        while parsers:
            parser = parsers.pop()

            if hasattr(parser, 'subparsers'):
                subparsers = tuple(sub.simplify() for sub in getattr(parser, 'subparsers'))
                setattr(parser, 'subparsers', subparsers)
                parsers.extend(list(sub for sub in subparsers if sub not in analyzed))
                analyzed.update(subparsers)

            elif hasattr(parser, 'subparser'):
                subparser = getattr(parser, 'subparser').simplify()
                setattr(parser, 'subparser', subparser)
                if parser not in analyzed:
                    parsers.append(subparser)
                    analyzed.add(subparser)


class Lit(Combinator):
    """
    A parser of an exact string
    """
    instances:weakref.WeakValueDictionary[str,'Lit'] = weakref.WeakValueDictionary()
    recurse = True # As an optimization - there's no way Lit can recurse, so don't check

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

# TODO: Make a multi-parser parent of Seq and Choice

class Seq(Combinator):
    """
    A sequence of parsers.
    """
    compound = True

    def __init__(self, left:Parseable, right:Parseable) -> None:
        super().__init__()
        self.subparsers:tuple[Combinator, ...]

# TODO: this doesn't flatten the rhs
        if isinstance(left, Seq) and not left.emit:
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

    def recognize(self, state:State) -> State|None:
        first = True
        for parser in self.subparsers:
            if not first:
                state.shiftParser()

            if parser.compound:
                try:
                    state = parser.parseCore(state)
                finally:
                    if not first:
                        state.unshiftParser()
            else:
                newState = parser.recognize(state)
                if not first:
                    state.unshiftParser()

                if newState is None:
                    return None

                state = newState

            first = False

        return state

    def __add__(self, right:Parseable) -> Parseable:
        subparsers = list(self.subparsers)
        subparsers.append(asCombinator(right))
        self.subparsers = tuple(subparsers)
        self._hash = hash(self.subparsers)
        return self

    def __hash__(self) -> int:
        return self._hash

    def repr(self) -> str:
        return f'Seq{self.subparsers}'


class Choice(Combinator):
    """
    Parse as the first successful parse.
    """
    recurse = True
    compound = True

    def __init__(self, left:Parseable, right:Parseable) -> None:
        super().__init__()
        self.subparsers:tuple[Combinator, ...]

        if isinstance(left, Choice) and not left.emit:
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

    def recognize(self, state:State) -> State|None:
        bestState:State|None = None
        
        for parser in self.subparsers:
            if not state.inRecursion(parser):
                trialState:State|None

                if parser.compound:
                    trialState = state.pushState()

                    try:
                        trialState = parser.parseCore(trialState)
                    except ParseError:
                        continue
                else:
                    trialState = parser.recognize(state)

                if trialState is not None:
                    if state != trialState:
                        state = trialState.popState()
                    bestState = state
                    break
        return bestState

    def __or__(self, right:Parseable) -> Parseable:
        subparsers = list(self.subparsers)
        subparsers.append(asCombinator(right))
        self.subparsers = tuple(subparsers)
        self._hash = hash(self.subparsers)
        return self

    def __hash__(self) -> int:
        return self._hash

    def repr(self) -> str:
        return f'Choice{self.subparsers}'


class Repeat(Combinator):
    """
    Repeat a combinator.
    """
    compound = True

    def __init__(self,
            subparser:Combinator,
            minimum:int,
            maximum:Optional[int|float],
            separator:Optional[Parseable]
            ) -> None:
        super().__init__()
        self.subparser = subparser
        self.minimum = minimum
        self.maximum = maximum
        self.separator = None if separator is None else asCombinator(separator)
        self._hash = hash(hash(self.subparser)+hash(self.minimum)+hash(self.maximum))

        self._sepParse = None if self.separator is None \
            else self.sepParse if self.separator.compound \
            else self.sepRecognize
        self._subParse = self.subParse if self.subparser.compound else self.subRecognize

    def expect(self, state:Expect) -> List[str]:
        return self.subparser.expectCore(state)

    def sepParse(self, state:State) -> State|None:
        """ Parse seperator with parseCore """
        try:
            return cast(Combinator, self.separator).parseCore(state)
        except ParseError:
            return None

    def sepRecognize(self, state:State) -> State|None:
        """ Parse separator with recognize """
        return cast(Combinator, self.separator).recognize(state)

    def subParse(self, state:State) -> State|None:
        """ Parse subparser with parseCore """
        try:
            return self.subparser.parseCore(state)
        except ParseError:
            return None

    def subRecognize(self, state:State) -> State|None:
        """ Parse subparser with recognize """
        return self.subparser.recognize(state)

    def recognizeOne(self, state:State, parsed:int) -> State|None:
        """ Recognize a seperator + subparser set """
        if parsed > 0 and self._sepParse:
            newState = self._sepParse(state)

            if newState is None:
                return None
            state = newState

        return self._subParse(state)

    def recognize(self, state:State) -> State|None:
        parsed = 0

        while parsed < self.minimum:
            newState = self.recognizeOne(state, parsed)

            if newState is None:
                return None

            state = newState
            parsed += 1

        if self.maximum is not None:
            while parsed < self.maximum:
                mustPop = self.subparser.compound or self.separator and self.separator.compound
                if mustPop:
                    trialState = state.pushState()
                else:
                    trialState = state

                newState = self.recognizeOne(trialState, parsed)

                if newState is None:
                    break

                state = newState

                if mustPop:
                    state = state.popState()

                parsed += 1

        return state

    def __hash__(self) -> int:
        return self._hash

    def repr(self) -> str:
        return f'Repeat({self.subparser}, {self.minimum}, {self.maximum}, {self.separator})'


class Id(Combinator):
    """
    Parse exactly the subparser.
    """
    compound = True

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

    #pylint: disable=signature-differs
    def __call__(self, arg:Parseable) -> Id:#type:ignore
        return Id(arg)

    def repr(self) -> str:
        return 'C'


C = CClass()
