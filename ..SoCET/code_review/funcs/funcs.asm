       .section data
       global threadId
       type threadId func
       global cos
       type cos func
       global sin
       type sin func
       global isqrt
       type isqrt func
       .section data
       .section code
       global main
       type main func
 main:
       lui, x11, 255
       lmi, x11, 4095
       lli, x11, 2160
       add x2, x2, x11
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 128
       add x11, x2, x11
       sw x1, 0(x11)
       sw x8, 0(x2)
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 256
       add x8, x2, x11
       sw x9, 0(x8)
 main_block0:
       jal x0, main_block1
 main_block1:
       lui, x10, 64
       lmi, x10, 1167
       lli, x10, 1475
       addi x9, x0, 2
       itof x9, x9
       divf x9, x10, x9
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 1024
       add x11, x8, x11
       sw x9, 0(x11)
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 1024
       add x11, x8, x11
       lw x9, 0(x11)
       cos x9, x9
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 896
       add x11, x8, x11
       sw x9, 0(x11)
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 1024
       add x11, x8, x11
       lw x9, 0(x11)
       sin x9, x9
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 768
       add x11, x8, x11
       sw x9, 0(x11)
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 1024
       add x11, x8, x11
       lw x9, 0(x11)
       isqrt x9, x9
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 640
       add x11, x8, x11
       sw x9, 0(x11)
       jal x1, threadId
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 512
       add x11, x8, x11
       sw x10, 0(x11)
       addi x10, x0, 0
       jal x0, main_epilog
 main_epilog:
       lw x9, 0(x8)
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 128
       add x11, x2, x11
       lw x1, 0(x11)
       lw x8, 0(x2)
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 1936
       add x2, x2, x11
       jalr x0,x1, 0
       .align 4
