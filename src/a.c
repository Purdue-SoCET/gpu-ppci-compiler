#include "a.h"

float test (int alpha, int beta, int theta)
{
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
    return cos(alpha);
}
