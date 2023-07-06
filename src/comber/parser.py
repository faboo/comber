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
        self._tree:list = [[]]

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

    def consume(self, length:int) -> None:
        """
        Consume a number of characters in the stream.
        """
        text = self.text[0:length]
        lines = text.split('\n')

        self.line += len(lines) - 1
        self.text = self.text[length:]

        if len(lines):
            self.char = len(lines[-1]) + 1
        else:
            self.char += len(lines[0])

        self._tree[-1].append(text)

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
        state = State(self.text)
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

    def parse(self, text:str) -> Any:
        """
        Parse a string.
        """
        return self.parseCore(State(text))


    def parseCore(self, state:State) -> State:
        """
        Internal parse function, for call on subparsers.
        """
        if self.intern:
            state.pushBranch()

        newState = self.recognize(state)

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

