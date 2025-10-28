int main() {
    int n = 3;
    int x = 4;
    int y = x*n;
    int z = x/n;
    int a = x << 4;
    int b = x >> 1;
    int c = x & 0xff;
    int d = x | 0xff;
    int e = x ^ n;
    return a+b+c+d+e;
}
