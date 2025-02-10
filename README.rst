====
Comber
====

Comber is a parser combinator library that allows the creation of parsers in plain Python with a BNF flavor.

.. code-block:: python
    from comber import C, cs, rs, inf
    
    sp = cs(' \t\n')[0, inf]
    keyword = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')@('keyword')
    import_statement = C + 'import' + sp + keyword


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
