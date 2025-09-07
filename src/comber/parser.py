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
            recurseStack:list[list[int]]|None = None,
            ) -> None:
        self.text = text
        """ Unparsed input """
        self.line = line
        """ Current line offset into the input text (starts at 1) """
        self.char = char
        """ Current character offset into the current line (starts at 1) """
        self.eof = False
        """ True if we have it the end of the text """
        self._tree:list[list] = tree if tree is not None else [[]]
        self._recurseStack:list[list[int]] = recurseStack if recurseStack is not None else [[]]
        self._whitespace = whitespace
        self._parent:State|None = None

    @property
    def tree(self) -> list:
        """
        The current parse tree
        """
        return self._tree[0]

    def advance(self, text:str) -> None:
        """ Advance current line and char based on a chunk of text """
        lines = text.count('\n')

        self.line += lines
        self.char = \
            len(text) - (text.rfind('\n') + 1) \
            if lines \
            else self.char + len(text)

    def eatWhite(self) -> None:
        """
        Consume the leading whitespace, if whitespace was defined.
        """
        if self._whitespace:
            text = self.text.lstrip(self._whitespace)
            eaten = self.text[0:len(self.text) - len(text)]
            self.text = text

            self.advance(eaten)
            self.eof = not self.text

    def consume(self, length:int) -> None:
        """
        Consume a number of characters in the stream.
        """
        eaten = text = self.text[0:length]
        self.text = self.text[length:]

        if self._whitespace:
            stripped = self.text.lstrip(self._whitespace)
            eaten = text + self.text[0:len(self.text) - len(stripped)]
            self.text = stripped

        self.advance(eaten)

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
        stack[-1] = list(stack[-1])
        tree = list(self._tree)
        tree.append([])
        state = State(
            self.text,
            self._whitespace,
            self.line,
            self.char,
            tree,
            stack
            )
        state._parent = self #pylint: disable=protected-access

        return state

    def popState(self) -> 'State':
        """
        Collapse an extended state.
        """
        state = cast(State, self._parent) #pylint: disable=protected-access

        state.text = self.text
        state.line = self.line
        state.char = self.char
        state.eof = self.eof
        state._tree[-1] += self._tree[-1] #pylint: disable=protected-access

        return state

    def pushParser(self, parser:'Parser') -> None:
        """
        Push the current parser.
        """
        self._recurseStack[-1].append(id(parser))

    #pylint: disable=unused-argument
    def popParser(self, parser:'Parser') -> None:
        """
        Pop the last parser.
        """
        self._recurseStack[-1].pop()

    def shiftParser(self) -> None:
        """
        Create a new recursion stack because we're looking for the element in a sequence
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
        return not parser.recurse and id(parser) in self._recurseStack[-1]


class ParseError(Exception):
    """
    When a string cannot be parsed, this exception is thrown.
    """
    def __init__(self, state:State, parser:'Parser') -> None:
        super().__init__('Unexpected text')
        self.line = state.line
        """ The input line the error occurred at. """
        self.char = state.char
        """ The character offset into the line the error occurred at. """
        self.text = state.text
        """ The unparsed input text. """
        self.parser = parser
        """ The parser that failed. """

    @property
    def expected(self) -> list[str]:
        """ The possible next tokens """
        return list(set(self.parser.expectCore()))

    @property
    def message(self) -> str:
        """ A lazy version of the exception message. """
        return str(self.line)+":"+str(self.char)+": " \
            +'Unexpected text: ' \
            +self.text[0:10] \
            +'. Expected one of: ' \
            +', '.join(self.expected)

    def __str__(self) -> str:
        return self.message


class EndOfInputError(ParseError):
    """
    When we reach the end of input before completing a full parse.
    """

    @property
    def message(self) -> str:
        return 'Unexpected end of input. Expected one of: ' \
            +', '.join(self.expected)


Emitter = Callable[[list[Any]], Any]
"""
Type of emitter functions.
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
        self.emit:Optional[Emitter] = None
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
        if self.emit:
            state.pushBranch()

        if not self.recurse:
            state.pushParser(self)

        try:
            newState = self.recognize(state)
        except ParseError:
            # Nothing that Can recurse will actually throw
            #if not self.recurse:
            state.popParser(self)
            raise

        if newState is None:
            if state.eof:
                raise EndOfInputError(state, self)
            else:
                raise ParseError(state, self)

        if not self.recurse:
            newState.popParser(self)

        if self.emit is not None:
            value = self.emit(newState.popBranch())
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
