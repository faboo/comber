""""""
Comber
""""""

Comber is a parser combinator library for creating text parsers in plain Python with a BNF flavor.

For instance, we could define a simple grammar for calling functions on integer values like this:

.. code-block:: python

    from comber import C, rs, inf
    
    keyword = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')@('keyword')
    number = rs(r'[0-9]+')@('number', int)
    value = keyword | number
    package = keyword[1, inf, ',']
    import_statement = C+ 'import' + package
    function_call = keyword + '(' + value**',' + ')'
    assignment = C+ 'let' + keyword + '=' + (function_call | value)
    grammar = (import_statement | assignment | function_call)[0, inf]

Our toy grammar can handle simple import statements, variable assignment, and function calling. For example::

    import math
    import sys.io
    
    let user_number = read()
    let double = multiple(user_number, 2)
    
    print(double)

To use our parser, we simply pass a string to it:

.. code-block:: python

    from comber import ParseError

    code = "add(17, 3)"
    try:
        parseState = grammar(code)
        print(f'Parsed tokens: {parseState.tree}')
    except ParseError as ex:
        print(ex)

The `grammar` call returns the final parser state on a successful parse, from which you can retrieve the final parse
tree. In our case, it is effectively a list::

    ['add', '(', 17, 3, ')']

Our grammar only supports variables and integers. Suppose we tried to assign pythong-style string to a variable::
    
    let text = "Here's some text"

If we tried to parse this, we'd get an exception like::

    1:12: Unexpected Text: "Here's som. Expected one of: @keyword, @number


.. contents:: Contents
   :depth: 3


================
Building Parsers
================

The most basic parsers are string literals (which match exactly), `rs` for matching a regular expression, and `cs` for
matching any of the strings of an iterable.

The `rs` parser can be seen in our toy grammar above. Standard Python regular expressions are supported. The entire
match is used as the result of the parse, regardless of groupings etc.

The `cs` parse takes any iterable of strings. The first string that exactly matches (the start of) the input text. If
none of the strings match, the parse fails. Since strings are themselves iterables, we could add addition and
subtraction to our toy grammar like this:

.. code-block:: python

    from comber import C, cs

    addition = value + cs('+-') + value
    assignment = C+ 'let' + keyword + '=' + (addition | function_call | value)

String literals can only be used in combination with other parsers. If a string literal would start a sequence, or
otherwise appear alone, make use of the C parser.

------------
The C Parser
------------

The C parser, on its own, consumes no text, produces no tokens, and always succeeds. It's most useful for starting a
parser that would otherwise begin with a string literal. E.g. this:

.. code-block:: python

    'let' + keyword + '=' + (function_call | value)

would actually throw a Python error because 'let' isn't *really* a parser - yet! That's where `C` comes in:

.. code-block:: python

    C+ 'let' + keyword + '=' + (function_call | value)

`C` starts off the sequence, so we can use any combination of parsers and string literals we like from there. It works
similarly with alternatives, so if we wanted to allow `set` to be used as a synonym for `let`, we might do:

.. code-block:: python

    (C| 'let'|'set') + keyword + '=' + (function_call | value)

`C` can also be used to wrap a parser to protect it from optimization; for instance, embedding one sequence or
alternative set inside another. If, for instance, we extended our grammar to allow a bare value to be a whole statement:

.. code-block:: python

    value = (keyword | number)@'value'
    grammar = (import_statement | assignment | function_call | value)[0, inf]


-----------------
Basic Combinators
-----------------

Parsers can be combined in series with `+`:

.. code-block:: python

    name + address + pet

A sequence of parsers is evaluated left to right, each consuming text before the next is evaluated. If at any point in
the sequence a parser fails, the entire sequence fails.

A set of alternatives is built with `|`:

.. code-block:: python

    name | idnumber | location

Alternatives are considered left to right, with the first successful match being the match for the entire set. Be
careful! This means that for some sets of alternatives, the "obvious" parser may not be the one used, simply because it
came after another match. 

Both sequences and alternatives will flatten like combinators, such that:

.. code-block:: python

    name = firstname + lastname
    salutation = C+ 'Hello' + name + '!'

is equivalent to:

.. code-block:: python

    salutation = C+ 'Hello' + firstname + lastname + '!'

If you need to mantain the logical separation (to parse correctly, or maintain the name of a subparser), wrap the
subparser with `C`:

.. code-block:: python

    name = C(firstname + lastname)
    salutation = C+ 'Hello' + name + '!'

----------
Repetition
----------

The most flexible option for specifying repetition is brackets:

.. code-block:: python

    keyword[0, 10, ',']

The above would parse `keyword` zero to ten times, separated by a comma. The separator is optional - without it, the
result would simply parse `keyword` zero to ten times.

We could also specify parsing an exact number of times:

.. code-block:: python

    keyword[10]

Or, with a separator: 

.. code-block:: python

    keyword[0, None, ',']

Infinity - `math.inf` - is a valid maximum value. For convenience, it can be imported directly from Comber:

.. code-block:: python

    from comber import inf

    param_list = keyword[0, inf, ',']

There are several convenience combinators for common types of repetition.

For zero or more with a separator, using `**`:

.. code-block:: python

    parser*','

Or zero or more without a separator, using the unary `+`:

.. code-block:: python

    +parser

You can declare a parser as *optional* with `~`:

.. code-block:: python

    ~parser

------------------
Recursive Grammars
------------------


====================
Building Parse Trees
====================


==============
Error Handling
==============



========
Pitfalls
========

Under the covers, Comber is essentially a recursive descent parser. It's best suited for relatively shallow grammars
parsing small amounts of text.



====
TODO
====

-------------------
Available Operators
-------------------

Operators that Python allows to overridden


========  ==============  ===========
Operator  Method          Current use
========  ==============  ===========
\+        __add__         sequences
\|        __or__          selection
[ ]       __getitem__     repeat
@         __matmul__      names and internalization
<         __lt__
>         __gt__
<=        __le__
>=        __ge__
==        __eq__
!=        __ne__
is        _is
is not    is_not
\-        __sub__
%         __mod__
\*        __mul__
\**       __pow__         zero or more, with provided separator
/         __truediv__
//        __floordiv__
&         __and__
^         __xor__
<<        __lshift__
>>        __rshift__
in        __contains__
========  ==============  ===========


Unary operators:

========  ===========  ===========
Operator  Method       Current use
========  ===========  ===========
~         __invert__   optional
not       __not__
\-        __neg__
\+        __pos__      zero or more
========  ===========  ===========

And::

    ()        __call__   parse a string
