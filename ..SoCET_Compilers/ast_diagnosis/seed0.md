## Functions

int main() {
}

Compilation unit with 1 declarations
    Function storage=None typ=Function-type name=main
        Function-type
            Basic type int
        Compound

----------------------------------------------------------------------

int main() {
    return 0;
}
Compilation unit with 1 declarations
    Function storage=None typ=Function-type name=main
        Function-type
            Basic type int
        Compound
            Return
                Numeric literal 0 <Basic type int>
                    Basic type int

----------------------------------------------------------------------
int* main() {
    return 0;
}

Compilation unit with 1 declarations
    Function storage=None typ=Function-type name=main
        Function-type
            Pointer-type
                Basic type int
        Compound
            Return
                Cast Pointer-type
                    Pointer-type
                        Basic type int
                    Numeric literal 0 <Basic type int>
                        Basic type int

----------------------------------------------------------------------
int main(char C, double D) {
    return 0;
}

Compilation unit with 1 declarations
    Function storage=None typ=Function-type name=main
        Function-type
            Parameter [typ=Basic type char name=C]
                Basic type char
            Parameter [typ=Basic type double name=D]
                Basic type double
            Basic type int
        Compound
            Return
                Numeric literal 0 <Basic type int>
                    Basic type int

----------------------------------------------------------------------
void main() {
}

Compilation unit with 1 declarations
    Function storage=None typ=Function-type name=main
        Function-type
            Basic type void
        Compound
