====
Comber
====

Comber is a parser combinator library that allows the creation of parsers in plain Python with a BNF flavor.

.. code-block:: python
    from comboer import C, cs, rs, inf
    
    sp = cs(' \t\n')[0, inf]
    keyword = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')
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
**        __pow__
/         __truediv__
//        __floordiv__
&         __and__
^         __xor__
<<        __lshift__
>>        __rshift__
in        __contains__
[ ]       __getitem__


Unary operators:

========  ===========  =====
Operator  Method       Current use
========  ===========  =====
not       __not__
~         __invert__
-         __neg__
+         __pos__

Possibly useful: __call__
