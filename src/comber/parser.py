"""
Base parser definitions.
"""
from typing import List, Optional, Callable, Any
from abc import abstractmethod


class State:
    """
    Internal parse state.
    """
    def __init__(self, text:str) -> None:
        self.text = text
        self.line = 1
        self.char = 1
        self.strings:List[str] =  []

    def consume(self, length:int) -> 'State':
        """
        Consume a number of characters in the stream.
        """
        state = State(self.text[length:])
        lines = self.text[0:length].split('\n')
        state.line += len(lines) - 1

        if len(lines):
            state.char = len(lines[-1]) + 1
        else:
            state.char += len(lines[0])

        return state


class ParseError(Exception):
    """
    When a string cannot be parsed, this exception is thrown.
    """
    def __init__(self, state:State, expected:List[str]) -> None:
        super().__init__("Unexpected text: "+state.text[0:10])
        self.line = state.line
        self.char = state.char
        self.text = state.text[0:10]
        self.expected = expected


Intern = Callable[[str], Any]
"""
Type of internalizer functions.
"""


class Parser:
    """
    Base parser.
    """
    def __init__(self) -> None:
        self.name:Optional[str] = None
        """ Name given the result of this parser """
        self.intern:Optional[Intern] = None
        """ Internalizer function; if not provided, the result will be the parsed string """

    def parse(self, text:str) -> Any:
        """
        Parse a string.
        """
        state = State(text)
        result = self.parseBase(state)

        if not result:
            raise ParseError(state, self.expect())

        return result


    def parseBase(self, state:State) -> Optional[State]:
        """
        Internal parse function, for call on subparsers.
        """
        newState = self.parseString(state)

        if newState is None:
            return None

        return newState


    @abstractmethod
    def expect(self) -> List[str]:
        """
        Strings representing what's expected by this parser.
        """


    @abstractmethod
    def parseString(self, state:State) -> Optional[State]:
        """
        Core parse function of a parser.
        """

