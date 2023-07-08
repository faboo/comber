from comber import C, rs, delayed, inf


def test_restsh():
    string = rs(r'"(\\"|[^"])*"')@('string')
    integer = rs(r'[+-]?[0-9]+')@('integer')
    floating = rs(r'[+-]?[0-9]+\.[0-9]+')@('float')
    symbol = rs(r'[_a-zA-Z][_a-zA-Z0-9]*')@('symbol')
    operator = rs(r'[-+*/|&^$@?~=<>]+')@('operator')

    expression = delayed()
    constant = string | integer | floating
    boolean = C+ '!' + expression
    variable = symbol
    objectRef = expression + '.' + symbol
    array = C+ '[' + expression[0, inf, ','] + ']'
    closure = C+ '\\' + symbol[0, inf, ','] + '.' + expression
    dictObject = C+ '{' + (symbol + ':' + expression)[0, inf, ','] + '}'
    call = expression + '(' + (symbol + ':' + expression)[0, inf, ','] + ')'
    opcall = expression + operator + expression
    tryex = C+ 'try' + expression
    subscript = expression + '[' + expression + ']'
    group = C+ '(' + expression + ')'
    ifthen = C+ 'if' + expression + 'then' + expression
    define = C+ 'let' + variable
    lvalue = define | objectRef | variable
    rvalue = expression
    describe = C+ 'help' + ~expression
    ext = C+ 'exit'
    imprt = C+ 'import' + symbol
    assignment = lvalue + '=' + rvalue
    block = expression[1, inf, ';']

    expression.fill(
        variable |
        array |
        dictObject |
        constant |
        closure |
        boolean |
        tryex |
        ifthen |
        subscript | 
        call |
        opcall |
        group |
        block |
        objectRef)
    
    statement = describe | ext | imprt | define | assignment | expression



