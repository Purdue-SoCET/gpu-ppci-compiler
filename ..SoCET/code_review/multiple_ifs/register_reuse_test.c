// Test case to demonstrate predicate register reuse
int main() {
    int x = 0;

    // First if: allocates pred1, pred2
    if (x == 1) {
        x = 10;
    } else {
        x = 20;
    }
    // After reconverge: pred1, pred2 freed

    // Second if: should REUSE pred1, pred2
    if (x == 10) {
        x = 100;
    } else {
        x = 200;
    }
    // After reconverge: pred1, pred2 freed again

    // Third if: should REUSE pred1, pred2 again
    if (x == 100) {
        x = 1000;
    } else {
        x = 2000;
    }

    return x;
}
