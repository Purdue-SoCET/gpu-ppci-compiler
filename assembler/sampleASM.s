add x10, x11, x12, 29, 1, 0
sub x10, x11, x12, pred, start, end
mul x10, x11, x12, pred, start, end
div x10, x11, x12, pred, start, end
and x10, x11, x12, pred, start, end
xor x10, x11, x12, pred, start, end
or x10, x11, x12, pred, start, end
slt x10, x11, x12, pred, start, end
sltu x10, x11, x12, pred, start, end
addf x10, x11, x12, pred, start, end
subf x10, x11, x12, pred, start, end
mulf x10, x11, x12, pred, start, end
divf x10, x11, x12, pred, start, end
sll x10, x11, x12, pred, start, end
srl x10, x11, x12, pred, start, end
branched:
    sra x10, x11, x12, pred, start, end
    lb x10, x11, 0, pred, start, end
    lh x10, x11, 0, pred, start, end
lw x10, x11, 0, pred, start, end
jalr x10, x11, branched, pred, start, end
isqrt x10, x11, 0, pred, start, end
sin x10, x11, 0, pred, start, end
cos x10, x11, 0, pred, start, end
addi x10, x11, 5, pred, start, end
xori x10, x11, 1, pred, start, end
ori x10, x11, 1, pred, start, end
slli x10, x11, 1, pred, start, end
srli x10, x11, 1, pred, start, end
srai x10, x11, 1, pred, start, end
slti x10, x11, 1, pred, start, end
sltiu x10, x11, 1, pred, start, end
itof x10, x11, 0, pred, start, end
ftoi x10, x11, 0, pred, start, end
sb x11, x12, 1, pred, start, end
sh x11, x12, 1, pred, start, end
sw x11, x12, 1, pred, start, end
beq p10, x11, x12, pred, start, end
bne p10, x11, x12, pred, start, end
bge p10, x11, x12, pred, start, end
bgeu p10, x11, x12, pred, start, end
blt p10, x11, x12, pred, start, end
bltu p10, x11, x12, pred, start, end
lui x10, 50, pred, start, end
lmi x10, 50, pred, start, end
lli x10, 50, pred, start, end
auipc x10, 100, pred, start, end
jal x10, x11, 50, pred, start, end
jpnz p11, x12, pred, start, end
csrr x10, x1000, pred, start, end
csrw x1000, x11, pred, start, end
