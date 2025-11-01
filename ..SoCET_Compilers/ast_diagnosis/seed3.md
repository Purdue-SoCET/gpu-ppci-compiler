## Two Nested If-Else Statements

int main() {

    int a = 5;
    int b = 10;

    // If
    if(a < b)  {
        // Compound
        a += 10;

        // If
        if(a < b)  {
            // Compound
            a += 10;
        }

        else {
            // Compound
            b -= 10;
        }
    }
    
    else {
        // If
        if(a < b)  {
            // Compound
            a += 10;
        }

        else {
            // Compound
            b -= 10;
        }
        // Compound
        b -= 10;
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
                    Numeric literal 5 <Basic type int>
                        Basic type int
            Declaration statement
                Variable [storage=None typ=Basic type int name=b]
                    Basic type int
                    Numeric literal 10 <Basic type int>
                        Basic type int
            If
                BinaryOperator < <Basic type int>
                    Id a <Basic type int>
                    Id b <Basic type int>
                    Basic type int
                Compound
                    Expression statement
                        BinaryOperator += <Basic type int>
                            Id a <Basic type int>
                            Numeric literal 10 <Basic type int>
                                Basic type int
                            Basic type int
                    If
                        BinaryOperator < <Basic type int>
                            Id a <Basic type int>
                            Id b <Basic type int>
                            Basic type int
                        Compound
                            Expression statement
                                BinaryOperator += <Basic type int>
                                    Id a <Basic type int>
                                    Numeric literal 10 <Basic type int>
                                        Basic type int
                                    Basic type int
                        Compound
                            Expression statement
                                BinaryOperator -= <Basic type int>
                                    Id b <Basic type int>
                                    Numeric literal 10 <Basic type int>
                                        Basic type int
                                    Basic type int
                Compound
                    If
                        BinaryOperator < <Basic type int>
                            Id a <Basic type int>
                            Id b <Basic type int>
                            Basic type int
                        Compound
                            Expression statement
                                BinaryOperator += <Basic type int>
                                    Id a <Basic type int>
                                    Numeric literal 10 <Basic type int>
                                        Basic type int
                                    Basic type int
                        Compound
                            Expression statement
                                BinaryOperator -= <Basic type int>
                                    Id b <Basic type int>
                                    Numeric literal 10 <Basic type int>
                                        Basic type int
                                    Basic type int
                    Expression statement
                        BinaryOperator -= <Basic type int>
                            Id b <Basic type int>
                            Numeric literal 10 <Basic type int>
                                Basic type int
                            Basic type int
            Return
                Id a <Basic type int>
