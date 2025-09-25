       .section data
       global cos
       type cos func
       global sin
       type sin func
       .section data
       ALIGN(4)
       global rs1
 rs1:
       .byte 1
       .byte 0
       .byte 0
       .byte 0
       ALIGN(4)
       global rs2
 rs2:
       .byte 2
       .byte 0
       .byte 0
       .byte 0
       .section code
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
       j main_block1
 main_block1:
       auipc x9, %pcrel_hi(main_literal_0)
       lw x9%pcrel_lo(main_literal_0)(x9)
       lw x12, 0(x9)
       auipc x9, %pcrel_hi(main_literal_1)
       lw x9%pcrel_lo(main_literal_1)(x9)
       lw x13, 0(x9)
       customcos x10, x12, x13
       sw x10, 20(x8)
       auipc x9, %pcrel_hi(main_literal_0)
       lw x9%pcrel_lo(main_literal_0)(x9)
       lw x12, 0(x9)
       addi x13, x0, 5
       customsin x10, x12, x13
       sw x10, 16(x8)
       auipc x9, %pcrel_hi(main_literal_0)
       lw x9%pcrel_lo(main_literal_0)(x9)
       lw x9, 0(x9)
       addi x10, x0, 1
       beq x9, x10, main_block3
       j main_block2
 main_block2:
       lw x10, 20(x8)
       j main_epilog
 main_block3:
       auipc x10, %pcrel_hi(main_literal_1)
       lw x10%pcrel_lo(main_literal_1)(x10)
       addi x9, x0, 3
       sw x9, 0(x10)
       j main_block2
 main_epilog:
       lw x9, 12(x2)
       addi x2, x2, 16
       lw x1, 4(x2)
       lw x8, 0(x2)
       addi x2, x2, 32
       jalr x0,x1, 0
       .section data
       .align 4
 main_literal_0:
       dcd=rs1
 main_literal_1:
       dcd=rs2
       .section code
       .align 4
