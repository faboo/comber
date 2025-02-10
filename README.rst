====
Comber
====

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
    assignment = C+ 'let' + keyword + '=' + (value | function_call)
    grammar = (import_statement | assignment | function_call)[0, inf]

Our toy grammar can handle simple import statements, variable assignment, and function calling. For example:

.. code-block::
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



====
TODO
====

----
Available Operators
----

Operators that Python allows to overridden


========  ==============  =====
Operator  Method          Current use
========  ==============  =====
+         __add__         sequences
|         __or__          selection
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
-         __sub__
%         __mod__
*         __mul__
**        __pow__         zero or more, with provided separator
/         __truediv__
//        __floordiv__
&         __and__
^         __xor__
<<        __lshift__
>>        __rshift__
in        __contains__


Unary operators:

========  ===========  =====
Operator  Method       Current use
========  ===========  =====
~         __invert__   optional
not       __not__
-         __neg__
+         __pos__      zero or more

And:

========  =========  =====
Operator  Method     Current Use
========  =========  =====

()        __call__   parse a string
