#include "include/kernel.h"
#include "include/saxpy.h"

#ifdef CPU_SIM
void kernel_saxpy(void* arg)
#else
void kernel_saxpy()
#endif
{
    #ifdef CPU_SIM
    saxpy_arg_t* args = (saxpy_arg_t*) arg;
    #else
    saxpy_arg_t* args = (saxpy_arg_t*) argPtr();
    #endif

    // Calculate the global thread index
    int i = blockIdx * blockDim + threadIdx;

    // Perform the calculation if the index is within bounds
    if (i < args->n) {
        args->y[i] = args->a * args->x[i] + args->y[i];
    }
}
