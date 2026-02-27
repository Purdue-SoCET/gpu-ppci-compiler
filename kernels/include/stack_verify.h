#ifndef STACK_VERIFY_H
#define STACK_VERIFY_H

/* Stack verification kernel: each thread writes known values to local
 * (stack) variables, reads them back, and stores to output buffer.
 * Used to verify SP/FP and SIMT stack layout. */

#define STACK_VERIFY_NUM_LOCALS 4
#define STACK_VERIFY_SLOTS_PER_THREAD (STACK_VERIFY_NUM_LOCALS + 1)  /* +1 for pass/fail */

typedef struct {
    unsigned int *results;  /* [tid * SLOTS_PER_THREAD + 0..3] = locals, +4 = pass (1) or fail (0) */
    int num_threads;
} stack_verify_arg_t;

void kernel_stack_verify();

#endif
