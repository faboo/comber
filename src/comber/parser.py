"""
Base parser definitions.
"""
import logging
from typing import List, Optional, Callable, Any
from abc import abstractmethod




class State:
    """
    Internal parse state.
    """
    def __init__(self, text:str, whitespace:Optional[str]) -> None:
        self.text = text
        self.line = 1
        self.char = 1
        self._tree:list = [[]]
        self._recurseStack = set()
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
            if lines:
                self.char = len(lines[-1]) + 1
            else:
                self.char += len(lines[0])

    def consume(self, length:int) -> None:
        """
        Consume a number of characters in the stream.
        """
        text = self.text[0:length]
        lines = text.split('\n')

        self.line += len(lines) - 1
        self.text = self.text[length:]

        if lines:
            self.char = len(lines[-1]) + 1
        else:
            self.char += len(lines[0])

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
        state.pushBranch()

        return state

    def popState(self) -> 'State':
        """
        Collapse an extended state.
        """
        popped = self.popBranch()
        self._tree[-1] += popped
        return self


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
        return self.parseCore(State(text, whitespace))


    def parseCore(self, state:State) -> State:
        """
        Internal parse function, for call on subparsers.
        """
        if self.inStack(state):
            ShiftShiftError(state, self.expectCore())
        if self.intern:
            state.pushBranch()

        logging.info('parseCore %s (%s)', self.__class__.__name__, self.name)
        logging.info('tree depth: %s', len(state._tree))
        newState = self.recognize(state)
        logging.info('    newState: %s', newState)

        if newState is None:
            if state.eof:
                raise EndOfInputError(state, self.expectCore())
            else:
                raise ParseError(state, self.expectCore())

        if self.intern is not None:
            value = self.intern(newState.popBranch())
            newState.pushLeaf(value)

        return newState


    def expectCore(self) -> List[str]:
        """
        If this parser has a name, then a list containing only its name, otherwise the value returned by expect
        """
        return [self.name] if self.name else self.expect()


    @abstractmethod
    def expect(self) -> List[str]:
        """
        Strings representing what's expected by this parser.
        """


    @abstractmethod
    def recognize(self, state:State) -> Optional[State]:
        """
        Core parse function of a parser.
        """

