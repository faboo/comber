"""
Base parser definitions.
"""
import logging
from typing import List, Optional, Callable, Any
from abc import abstractmethod


class Expect:
    """ Internal state of expect calculation """
    def __init__(self) -> None:
        self._recurseStack:list[list] = [[]]

    def pushParser(self, parser:Any) -> None:
        """
        Push the current parser.
        """
        self._recurseStack[-1].append(parser)

    def popParser(self) -> None:
        """
        Pop the last parser.
        """
        self._recurseStack[-1].pop()

    def shiftParser(self) -> None:
        """
        Create a new parser stack because we're looking for the element in a sequence
        """
        self._recurseStack.append([])

    def unshiftParser(self) -> None:
        """
        Toss out the current parser stack.
        """
        self._recurseStack.pop()

    def inRecursion(self, parser:Any) -> bool:
        """
        See if we're already trying to parse a given parser.
        """
        logging.info('RECURSE? %s <- %s == %s', parser, self._recurseStack[-1], parser in self._recurseStack[-1])
        return parser in self._recurseStack[-1]


class State:
    """
    Internal parse state.
    """
    def __init__(self, text:str, whitespace:Optional[str]) -> None:
        self.text = text
        self.line = 1
        self.char = 1
        self._tree:list = [[]]
        self._recurseStack:list = [[]]
        self._whitespace = whitespace

        self.eatWhite()

    @property
    def eof(self) -> bool:
        """
        True if we have run out of characters to read
        """
        return not self.text

    @property
    def tree(self) -> list:
        """
        The current parse tree
        """
        return self._tree[0]

    def eatWhite(self) -> None:
        """
        Consume the leading whitespace, if whitespace was defined.
        """
        if self._whitespace:
            text = self.text.lstrip(self._whitespace)
            lines = self.text[0:len(text)].split('\n')
            self.text = text
            self.line += len(lines) - 1
            self.char = len(lines[-1]) + 1

    def consume(self, length:int) -> None:
        """
        Consume a number of characters in the stream.
        """
        text = self.text[0:length]
        lines = text.split('\n')

        self.line += len(lines) - 1
        self.text = self.text[length:]

        self.char = len(lines[-1]) + 1

        self._tree[-1].append(text)

        self.eatWhite()
        logging.info('text: <%s>', self.text)

    def pushLeaf(self, value:Any) -> None:
        """
        Push a value onto the current stack branch.
        """
        self._tree[-1].append(value)

    def pushBranch(self) -> None:
        """
        Push a new stack branch.
        """
        self._tree.append([])

    def popBranch(self) -> list:
        """
        Pop a stack branch off the tree stack
        """
        return self._tree.pop()

    def pushState(self) -> 'State':
        """
        Extend this state.
        """
        state = State(self.text, self._whitespace)
        state.line = self.line
        state.char = self.char
        #pylint: disable=protected-access
        state._tree = list(self._tree)
        state._recurseStack = list(self._recurseStack)
        state.pushBranch()

        return state

    def popState(self) -> 'State':
        """
        Collapse an extended state.
        """
        popped = self.popBranch()
        self._tree[-1] += popped
        return self

    def pushParser(self, parser:Any) -> None:
        """
        Push the current parser.
        """
        self._recurseStack[-1].append(parser)

    def popParser(self) -> None:
        """
        Pop the last parser.
        """
        self._recurseStack[-1].pop()

    def shiftParser(self) -> None:
        """
        Create a new parser stack because we're looking for the element in a sequence
        """
        self._recurseStack.append([])

    def unshiftParser(self) -> None:
        """
        Toss out the current parser stack.
        """
        self._recurseStack.pop()

    def inRecursion(self, parser:Any) -> bool:
        """
        See if we're already trying to parse a given parser.
        """
        logging.info('RECURSE? %s <- %s == %s', parser, self._recurseStack[-1], parser in self._recurseStack[-1])
        return parser in self._recurseStack[-1]


class ParseError(Exception):
    """
    When a string cannot be parsed, this exception is thrown.
    """
    def __init__(self, state:State, expected:List[str]) -> None:
        super().__init__(
            str(state.line)+":"+str(state.char)+": "
            +"Unexpected text: "
            +state.text[0:10]
            +". Expected one of: "
            +", ".join(expected))
        self.line = state.line
        self.char = state.char
        self.text = state.text[0:10]
        self.expected = expected


class EndOfInputError(ParseError):
    """
    When we reach the end of input before completing a full parse.
    """

class ShiftShiftConflict(ParseError):
    """
    When we encounter a shift-shift conflict
    """

class ShiftReduceConflict(ParseError):
    """
    When we encounter a shift-reduce conflict (e.g. we would "shift" into a recursive rule, but we ought to reduce
    instead)
    """


Intern = Callable[[List[Any]], Any]
"""
Type of internalizer functions.
"""


class Parser:
    """
    Base parser.
    """
    def __init__(self) -> None:
        self.name:Optional[str] = None
        """ Friendly name of this sub-parser """
        self.intern:Optional[Intern] = None
        """ Internalizer function; if not provided, the result will be the parsed string """

    def parse(self, text:str, whitespace:Optional[str]=' \t\n') -> State:
        """
        Parse a string.
        """
        logging.info('Parsing: %s', self)
        return self.parseCore(State(text, whitespace))


    def parseCore(self, state:State, recurse=True) -> State:
        """
        Internal parse function, for calling by subparsers.
        """
        if state.inRecursion(self):
            raise ShiftShiftConflict(state, self.expectCore())
        if self.intern:
            state.pushBranch()

        if not recurse:
            state.pushParser(self)
        try:
            newState = self.recognize(state)
        finally:
            if not recurse:
                state.popParser()

        if newState is None:
            if state.eof:
                raise EndOfInputError(state, self.expectCore())
            else:
                raise ParseError(state, self.expectCore())

        #if newState != state:
            #logging.info('Popping for new state: %s <> %s', newState, state)
            #newState.popParser()

        logging.info('recurse after: %s', state._recurseStack) #pylint: disable=protected-access

        if self.intern is not None:
            value = self.intern(newState.popBranch())
            newState.pushLeaf(value)

        return newState


    def expectCore(self, state:Expect|None = None) -> List[str]:
        """
        If this parser has a name, then a list containing only its name, otherwise the value returned by expect
        """
        state = state or Expect()
        if state.inRecursion(self):
            expecting = []
        else:
            state.pushParser(self)
            expecting = [self.name] if self.name else self.expect(state)
            state.popParser()
        return expecting

    def __repr__(self) -> str:
        """
        A string representation of the combinator
        """
        if self.name:
            return f"@{self.name}"
        return self.repr()


    @abstractmethod
    def expect(self, state:Expect) -> List[str]:
        """
        Strings representing what's expected by this parser.
        """


    @abstractmethod
    def recognize(self, state:State) -> Optional[State]:
        """
        Core parse function of a parser.
        """

    @abstractmethod
    def repr(self) -> str:
        """
        The specific combinator string represenation.
        """
