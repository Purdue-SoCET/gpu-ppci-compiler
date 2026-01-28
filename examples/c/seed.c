extern int threadId();

int main() {
    
    float a = (float)3.14 / 2;
    float b = cos(a);
    float c = sin(a);
    float d = isqrt(a);

    int x = threadId();

    return 0;
}