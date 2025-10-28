       section data
       section data
       section code
       global main
       type main func
 main:
 main_block0:
       jal x0, main_block1
 main_block1:
       addi x9, x0, 3
       sw x9, -4(x8)
       addi x9, x0, 4
       sw x9, -8(x8)
       lw x10, -8(x8)
       lw x9, -4(x8)
       mul x9, x10, x9
       sw x9, -12(x8)
       lw x10, -8(x8)
       lw x9, -4(x8)
       div x9, x10, x9
       sw x9, -16(x8)
       lw x9, -8(x8)
       slli x9, x9, 4
       sw x9, -20(x8)
       lw x9, -8(x8)
       srai x9, x9, 1
       sw x9, -24(x8)
       lw x9, -8(x8)
       lui, x10, 0
       lmi, x10, 0
       lli, x10, 255
       and x9, x9, x10
       sw x9, -28(x8)
       lw x9, -8(x8)
       lui, x10, 0
       lmi, x10, 0
       lli, x10, 255
       or x9, x9, x10
       sw x9, -32(x8)
       lw x10, -8(x8)
       lw x9, -4(x8)
       lui, x11, 255
       lmi, x11, 4095
       lli, x11, 4060
       add x11, x8, x11
       xor x9, x10, x9
       sw x9, 0(x11)
       lw x13, -20(x8)
       lw x12, -24(x8)
       lw x11, -28(x8)
       lw x10, -32(x8)
       lui, x9, 255
       lmi, x9, 4095
       lli, x9, 4060
       add x9, x8, x9
       lw x9, 0(x9)
       add x12, x13, x12
       add x11, x12, x11
       add x10, x11, x10
       add x10, x10, x9
       jal x0, main_epilog
 main_epilog:
