//extern float cos(float);
//extern int ftoi(float);
//extern float itof(int);
//extern float sin(float);
//extern float isqrt(float);

int main() {
    int alpha = 3;
    int beta;
    if(alpha < 3){
        beta = 4;
    } else {
        beta = 6;
    }
    int theta = 0;
    while(beta > 0){
        beta--;
        theta = theta * 2 + 1;
    }
    return theta;
}
