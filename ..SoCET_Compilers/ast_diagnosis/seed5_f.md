## Basic For Loop

int main() {

    int a = 10;
    for(int i = 0; i < 10; i++) {
        a += i;
    }
    return a;
}

Compilation unit with 1 declarations
    Function storage=None typ=Function-type name=main
        Function-type
            Basic type int
        Compound
            Declaration statement
                Variable [storage=None typ=Basic type int name=a]
                    Basic type int
                    Numeric literal 10 <Basic type int>
                        Basic type int
            Declaration statement
                Variable [storage=None typ=Basic type int name=i]
                    Basic type int
                    Numeric literal 0 <Basic type int>
                        Basic type int
            For
                BinaryOperator < <Basic type int>
                    Id i <Basic type int>
                    Numeric literal 10 <Basic type int>
                        Basic type int
                    Basic type int
                UnaryOperator x++
                    Id i <Basic type int>
                    Basic type int
                Compound
                    Expression statement
                        BinaryOperator += <Basic type int>
                            Id a <Basic type int>
                            Id i <Basic type int>
                            Basic type int
            Return
                Id a <Basic type int>
