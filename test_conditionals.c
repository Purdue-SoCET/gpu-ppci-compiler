int simple_if(int a, int b) {
    int result = 0;
    if (a < b) {
        result = 1;
    } else {
        result = 2;
    }
    return result;
}

int compound_or(int a, int b, int c, int d) {
    int result = 0;
    if (a < b || c >= d) {
        result = 1;
    } else {
        result = 2;
    }
    return result;
}

int compound_and(int a, int b, int c, int d) {
    int result = 0;
    if (a == b && c != d) {
        result = 1;
    } else {
        result = 2;
    }
    return result;
}

int triple_or(int a, int b, int c, int d, int e, int f) {
    int result = 0;
    if (a < b || c > d || e <= f) {
        result = 10;
    }
    return result;
}

int mixed_and_or(int a, int b, int c, int d) {
    int result = 0;
    if (a < b && c < d || a == d) {
        result = 42;
    }
    return result;
}

int negation(int a, int b) {
    int result = 0;
    if (!(a < b)) {
        result = 99;
    }
    return result;
}
