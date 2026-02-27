#include "include/kernel.h"
#include "include/stack_verify.h"

/* Stack verification kernel.
 * Each thread allocates 4 local (stack) variables, writes a tid-specific
 * pattern to each, reads them back, and stores results for verification.
 * Pattern: local_i = 0x(II00 << 16) | (tid & 0xFF)  with II = 0x11, 0x22, 0x33, 0x44
 * This exercises the SIMT stack layout: SP = base + (tid % 32) * 4
 * and variable offsets at scalar_var_offset * NUM_THREADS.
 */
void kernel_stack_verify() {
    stack_verify_arg_t* args = (stack_verify_arg_t*) argPtr();
    int tid = blockIdx * blockDim + threadIdx;

    // if (tid >= args->num_threads)
    //     return;

    /* Local (stack-allocated) variables - compiler will use stack slots */
    unsigned int local_a;
    unsigned int local_b;
    unsigned int local_c;
    unsigned int local_d;

    /* Write tid-specific pattern to each local */
    local_a = 0x11000000u | (unsigned int)(tid & 0xFF);
    local_b = 0x22000000u | (unsigned int)(tid & 0xFF);
    local_c = 0x33000000u | (unsigned int)(tid & 0xFF);
    local_d = 0x44000000u | (unsigned int)(tid & 0xFF);

    /* Read back (may fail if stack layout is wrong and we read another thread's slot) */
    unsigned int read_a = local_a;
    unsigned int read_b = local_b;
    unsigned int read_c = local_c;
    unsigned int read_d = local_d;

    /* Store to output buffer for verification */
    int base = tid * STACK_VERIFY_SLOTS_PER_THREAD;
    args->results[base + 0] = read_a;
    args->results[base + 1] = read_b;
    args->results[base + 2] = read_c;
    args->results[base + 3] = read_d;

    /* Pass (1) if all values read back correctly, else fail (0) */
    unsigned int expected_a = 0x11000000u | (unsigned int)(tid & 0xFF);
    unsigned int expected_b = 0x22000000u | (unsigned int)(tid & 0xFF);
    unsigned int expected_c = 0x33000000u | (unsigned int)(tid & 0xFF);
    unsigned int expected_d = 0x44000000u | (unsigned int)(tid & 0xFF);
    if(read_a == expected_a && read_b == expected_b && read_c == expected_c && read_d == expected_d){
        args->results[base + 4] = 1u;
    } else{
        args->results[base + 4] = 0u;
    }
}
