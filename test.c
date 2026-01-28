//extern float cos(float);
// extern int ftoi(float);
//extern float itof(int);
//extern float sin(float);
//extern float isqrt(float);

int main() {
    int alpha = 3;
    int beta = 7;
    int theta = 3;
    while(beta != 0){
        beta--;
        theta = beta;
        sin((float)beta);
        while(theta != 0){
            theta--;
            alpha++;
            cos((float)alpha);
        }
    }
    return alpha;
}
