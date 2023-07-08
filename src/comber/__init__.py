"""
Comber

"""
from math import inf
from .parser import ParseError, EndOfInputError
from .combinator import C, Id, Lit, Seq, Choice, Repeat
from .extras import cs, rs, delayed
