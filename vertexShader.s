lli x31, 128, 0
lli x32, 32, 0

lli x33, 0x7f, 0
slli x33, x33, 23, 0

csrr x10, 3, 0
csrr x11, 0, 0
csrr x12, 1, 0
csrr x13, 2, 0
mul x12, x12, x13, 0
add x11, x11, x12, 0

lw x20, 4(x10), 0
lw x40, 0(x20), 0
mulf x43, x40, x40, 0
lw x41, 4(x20), 0
mulf x44, x41, x41, 0
sltf x42, x43, x44, 0
bne 1, x42, x0, 0

add x60, x0, x0, 0
add x61, x0, x0, 0
addf x60, x0, x33, 1
addf x61, x0, x33, 0
add x62, x0, x0, 0

lw x42, 8(x20), 0
mulf x7, x61, x42, 0
mulf x8, x62, x41, 0
subf x50, x7, x8, 0

mulf x7, x62, x40, 0
mulf x8, x60, x42, 0
subf x51, x7, x8, 0

mulf x7, x60, x41, 0
mulf x8, x61, x40, 0
subf x52, x7, x8, 0

mulf x7, x50, x50, 0
mulf x8, x51, x51, 0
mulf x9, x52, x52, 0
addf x7, x7, x8, 0
addf x7, x7, x9, 0
isqrt x12, x7, 0

mulf x50, x50, x12, 0
mulf x51, x51, x12, 0
mulf x52, x52, x12, 0

addf x53, x0, x40, 0
addf x54, x0, x41, 0
addf x55, x0, x42, 0

mulf x7, x51, x55, 0
mulf x8, x52, x54, 0
subf x56, x7, x8, 0

mulf x7, x52, x53, 0
mulf x8, x50, x55, 0
subf x57, x7, x8, 0

mulf x7, x50, x54, 0
mulf x8, x51, x53, 0
subf x58, x7, x8, 0

mulf x7, x53, x53, 0
mulf x8, x54, x54, 0
mulf x9, x55, x55, 0
addf x7, x7, x8, 0
addf x7, x7, x9, 0
isqrt x13, x7, 0

mulf x53, x53, x13, 0
mulf x54, x54, x13, 0
mulf x55, x55, x13, 0

mulf x7, x56, x56, 0
mulf x8, x57, x57, 0
mulf x9, x58, x58, 0
addf x7, x7, x8, 0
addf x7, x7, x9, 0
isqrt x14, x7, 0

mulf x56, x56, x14, 0
mulf x57, x57, x14, 0
mulf x58, x58, x14, 0

addf x47, x0, x0, 0
addf x48, x0, x0, 0
addf x49, x0, x0, 0

lw x21, 12(x10), 0

addi x7, x0, 20, 0
mul x22, x11, x7, 0
add x22, x22, x21, 0
lw x23, 0(x22), 0
lw x24, 4(x22), 0
lw x25, 8(x22), 0

lw x26, 0(x10), 0
lw x27, 0(x26), 0
lw x28, 4(x26), 0
lw x29, 8(x26), 0

subf x47, x23, x27, 0
subf x48, x24, x28, 0
subf x49, x25, x29, 0

addf x17, x33, x0, 0

lw x6, 8(x10), 0
lw x7, 0(x6), 0
cos x15, x7, 0
sin x16, x7, 0

subf x18, x0, x16, 0

addf x34, x0, x0, 0
addf x35, x0, x0, 0
addf x36, x0, x0, 0

mulf x7, x50, x47, 0
addf x34, x34, x7, 0
mulf x7, x51, x48, 0
addf x34, x34, x7, 0
mulf x7, x52, x49, 0
addf x34, x34, x7, 0

mulf x7, x53, x47, 0
mulf x8, x54, x48, 0
mulf x9, x55, x49, 0
addf x7, x7, x8, 0
addf x35, x7, x9, 0

mulf x7, x56, x47, 0
mulf x8, x57, x48, 0
mulf x9, x58, x49, 0
addf x7, x7, x8, 0
addf x36, x7, x9, 0

addf x37, x0, x0, 0
addf x38, x0, x0, 0
addf x39, x0, x0, 0

mulf x7, x15, x34, 0
mulf x8, x18, x36, 0
addf x37, x7, x8, 0

mulf x38, x17, x35, 0

mulf x7, x16, x34, 0
mulf x8, x15, x36, 0
addf x39, x7, x8, 0

mulf x7, x50, x37, 0
mulf x8, x53, x38, 0
mulf x9, x56, x39, 0
addf x7, x7, x8, 0
addf x34, x9, x7, 0

mulf x7, x51, x37, 0
mulf x8, x54, x38, 0
mulf x9, x57, x39, 0
addf x7, x7, x8, 0
addf x35, x9, x7, 0

mulf x7, x52, x37, 0
mulf x8, x55, x38, 0
mulf x9, x58, x39, 0
addf x7, x7, x8, 0
addf x36, x9, x7, 0

addf x37, x34, x27, 0
addf x38, x35, x28, 0
addf x39, x36, x29, 0

lw x6, 16(x10), 0
addi x7, x0, 20, 0
mul x22, x11, x7, 0
add x6, x6, x22, 0

sw x37, 0(x6), 0
sw x38, 4(x6), 0
sw x39, 8(x6), 0

add x21, x21, x22, 0

lw x7, 12(x21), 0
lw x8, 16(x21), 0

sw x7, 12(x6), 0
sw x8, 16(x6), 0

lw x5, 20(x10), 0
lw x6, 0(x5), 0
lw x7, 4(x5), 0
lw x8, 8(x5), 0

subf x37, x37, x6, 0
subf x38, x38, x7, 0
subf x39, x39, x8, 0

lw x6, 24(x10), 0

lw x50, 0(x6), 0
lw x51, 4(x6), 0
lw x52, 8(x6), 0
lw x53, 12(x6), 0
lw x54, 16(x6), 0
lw x55, 20(x6), 0
lw x56, 24(x6), 0
lw x57, 28(x6), 0
addi x6, x6, 4, 0
lw x58, 28(x6), 0

mulf x7, x37, x50, 0
mulf x8, x38, x51, 0
mulf x9, x39, x52, 0
addf x7, x7, x8, 0
addf x47, x7, x9, 0

mulf x7, x37, x53, 0
mulf x8, x38, x54, 0
mulf x9, x39, x55, 0
addf x7, x7, x8, 0
addf x48, x7, x9, 0

mulf x7, x37, x56, 0
mulf x8, x38, x57, 0
mulf x9, x39, x58, 0
addf x7, x7, x8, 0
addf x49, x7, x9, 0

sltf x6, x0, x49, 0
bne 1, x6, x0, 0

lw x5, 28(x10), 1
addi x7, x0, 20, 1
mul x22, x11, x7, 1
add x5, x22, x5, 1
divf x6, x47, x49, 1
sw x6, 0(x5), 1

divf x6, x48, x49, 1
sw x6, 4(x5), 1

divf x6, x17, x49, 1
sw x6, 8(x5), 1

lw x7, 12(x10), 1
add x7, x22, x7, 1

lw x8, 12(x7), 1
lw x9, 16(x7), 1

sw x8, 12(x5), 1
sw x9, 16(x5), 1

halt
