#ifndef SAXPY_H
#define SAXPY_H

typedef struct {
    int n;
    float a;
    float *x;
    float *y;
} saxpy_arg_t;

#ifdef CPU_SIM
void kernel_saxpy(void*);
#else
void kernel_saxpy();
#endif

#endif
