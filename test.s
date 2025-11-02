       section data
       global cos
       type cos func
       global ftoi
       type ftoi func
       global itof
       type itof func
       global sin
       type sin func
       global isqrt
       type isqrt func
       section data
       section code
       global main
       type main func
 main:
       addi x2, x2, -32
       sw x1, 4(x2)
       sw x8, 0(x2)
       addi x8, x2, 8
       addi x2, x2, -16
       sw x9, 12(x2)
 main_block0:
       jal x0, main_block1
 main_block1:
       addi x9, x0, 3
       itof x9, x9
       sw x9, 20(x8)
       lw x9, 20(x8)
       lui, x10, 63
       lmi, x10, 2662
       lli, x10, 1638
       addf x9, x9, x10
       sw x9, 20(x8)
       lw x9, 20(x8)
       ftoi x9, x9
       sw x9, 16(x8)
       lw x10, 20(x8)
       lw x9, 16(x8)
       ftoi x10, x10
       add x9, x10, x9
       sw x9, 12(x8)
       lw x9, 20(x8)
       cos x9, x9
       isqrt x9, x9
       sin x9, x9
       sw x9, 8(x8)
       lw x9, 8(x8)
       ftoi x10, x9
       jal x0, main_epilog
 main_epilog:
       lw x9, 12(x2)
       addi x2, x2, 16
       lw x1, 4(x2)
       lw x8, 0(x2)
       lui, x11, 0
       lmi, x11, 0
       lli, x11, 32
       add x2, x2, x11
       jalr x0,x1, 0
       .align 4
