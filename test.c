//extern float cos(float);
//extern int ftoi(float);
//extern float itof(int);
//extern float sin(float);
//extern float isqrt(float);

int main() {
    float y = itof(3);
    y = y + (float)1.3;
    int x = y;
    int w = (int)y + x;
    float z = sin(isqrt(cos(y)));
    return ftoi(z);
}
