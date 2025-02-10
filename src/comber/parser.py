"""
Base parser definitions.
"""
from typing import cast, Optional, Callable, Any
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
        return not parser.recurse and parser in self._recurseStack[-1]


class State:
    """
    Internal parse state.
    """
    def __init__(self,
            text:str,
            whitespace:str|None,

            line:int = 1,
            char:int = 1,
            tree:list[list]|None = None,
            recurseStack:list[set[int]]|None = None,
            ) -> None:
        self.text = text
        self.line = line
        self.char = char
        self.eof = False
        self._tree:list[list] = tree if tree is not None else [[]]
        self._recurseStack:list[set[int]] = recurseStack if recurseStack is not None else [set()]
        self._whitespace = whitespace

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
            eaten = self.text[0:len(text)]
            lines = eaten.count('\n')
            self.text = text
            self.line += lines
            self.char = \
                len(eaten) - (eaten.rfind('\n') + 1) \
                if lines \
                else len(eaten)
            self.eof = not self.text

    def consume(self, length:int) -> None:
        """
        Consume a number of characters in the stream.
        """
        eaten = text = self.text[0:length]
        self.text = self.text[length:]

        if self._whitespace:
            stripped = self.text.lstrip(self._whitespace)
            eaten = text + self.text[0:len(stripped)]
            self.text = stripped

        lines = eaten.count('\n')

        self.line += lines
        self.char = \
            length - (eaten.rfind('\n') + 1) \
            if lines \
            else length

        self._tree[-1].append(text)
        self.eof = not self.text

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
        stack = list(self._recurseStack)
        stack[-1] = set(stack[-1])
        state = State(
            self.text,
            self._whitespace,
            self.line,
            self.char,
            list(self._tree),
            stack
            )
        state.pushBranch()

        return state

    def popState(self) -> 'State':
        """
        Collapse an extended state.
        """
        popped = self.popBranch()
        self._tree[-1] += popped
        return self

    def pushParser(self, parser:'Parser') -> None:
        """
        Push the current parser.
        """
        self._recurseStack[-1].add(id(parser))

    def popParser(self, parser:'Parser') -> None:
        """
        Pop the last parser.
        """
        self._recurseStack[-1].remove(id(parser))

    def shiftParser(self) -> None:
        """
        Create a new parser stack because we're looking for the element in a sequence
        """
        self._recurseStack.append(set())

    def unshiftParser(self) -> None:
        """
        Toss out the current parser stack.
        """
        self._recurseStack.pop()

    def inRecursion(self, parser:Any) -> bool:
        """
        See if we're already trying to parse a given parser.
        """
        return not parser.recurse and id(parser) in self._recurseStack[-1]


class ParseError(Exception):
    """
    When a string cannot be parsed, this exception is thrown.
    """
    def __init__(self, state:State, parser:'Parser') -> None:
        super().__init__('Unexpected text')
        self.line = state.line
        self.char = state.char
        self.text = state.text
        self.parser = parser

    @property
    def message(self) -> str:
        return str(self.line)+":"+str(self.char)+": " \
            +"Unexpected text: " \
            +self.text[0:10] \
            +". Expected one of: " \
            +", ".join(list(set(self.parser.expectCore())))

    def __str__(self) -> str:
        return self.message


class EndOfInputError(ParseError):
    """
    When we reach the end of input before completing a full parse.
    """

class ShiftShiftConflict(ParseError):
    """
    When we encounter a shift-shift conflict
    """


Intern = Callable[[list[Any]], Any]
"""
Type of internalizer functions.
"""


class Parser:
    """
    Base parser.
    """

    recurse = False
    """ If True, the parser class is allowed to recurse without any checks. """
    compound = False
    """ If True, the parser class is a compound class, and so may fail partway through. """

    def __init__(self) -> None:
        self.name:Optional[str] = None
        """ Friendly name of this sub-parser """
        self.intern:Optional[Intern] = None
        """ Internalizer function; if not provided, the result will be the parsed string """
        self.whitespace:str|None = ' \t\n'
        """ Default whitespace """

    def __call__(self, text:str, whitespace:str|None=None) -> State:
        """
        Parse a string.
        """
        state = State(text, whitespace if whitespace is not None else self.whitespace)
        state.eatWhite()
        return self.parseCore(state)


    def parseCore(self, state:State) -> State:
        """
        Internal parse function, for calling by subparsers.
        """
        if self.intern:
            state.pushBranch()

        if not self.recurse:
            state.pushParser(self)

        try:
            newState = self.recognize(state)
        except ParseError:
            if not self.recurse:
                state.popParser(self)
            raise

        if newState is None:
            if state.eof:
                raise EndOfInputError(state, self)
            else:
                raise ParseError(state, self)

        if not self.recurse:
            newState.popParser(self)

        if self.intern is not None:
            value = self.intern(newState.popBranch())
            newState.pushLeaf(value)

        return newState


    def expectCore(self, state:Expect|None = None) -> list[str]:
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


    def analyze(self) -> None:
        """
        Analyze the grammar to improve performance.
        """


    @abstractmethod
    def expect(self, state:Expect) -> list[str]:
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
