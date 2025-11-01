## Declarations and Expressions

int main() {
    int a = 1;
    int b = 2;
    int c = 1 + 2;
    return c;
}

Compilation unit with 1 declarations
    Function storage=None typ=Function-type name=main
        Function-type
            Basic type int
        Compound
            Declaration statement
                Variable [storage=None typ=Basic type int name=a]
                    Basic type int
                    Numeric literal 1 <Basic type int>
                        Basic type int
            Declaration statement
                Variable [storage=None typ=Basic type int name=b]
                    Basic type int
                    Numeric literal 2 <Basic type int>
                        Basic type int
            Declaration statement
                Variable [storage=None typ=Basic type int name=c]
                    Basic type int
                    BinaryOperator + <Basic type int>
                        Numeric literal 1 <Basic type int>
                            Basic type int
                        Numeric literal 2 <Basic type int>
                            Basic type int
                        Basic type int
            Return
                Id c <Basic type int>
----------------------------------------------------------------------
