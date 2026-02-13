# MMIO, Global Memory Space, and Launch Protocol 

 - Will be:

        - shared memory
        - host and gpu 4GB shared address space
        - host will also have its own memory
        - after kernel launch, host will poll until GPU is done

## MMIO:

| Address | Value | Description |
| :--- | :--- | :--- |
| 0x00 | Control Registers | bit 0: Start GPU (1=RUN) <br> bit 1: GPU reset (1=RESET)|
| 0x04 | Status Register | bit 0: GPU Done (1=DONE) <br> bit 1: GPU Idle (1=IDLE) <br> bit 2: GPU Error (1=ERROR)|
| 0x08 | Device ID Register | GPU ID |
| 0x0C | Kernel Entry Point Register | Physical Address of instruction starting point|
| 0x10 | Block Register | Block dimension: Threads per block|
| 0x14 | Grid Register | Grid dimension: Number of blocks|
| 0x18 | Total Threads Register | Total Threads |
| 0x1C | Kernel Arguments Addresss Register| Physical Address of Arguments|
| 0x20 | Kernel Argument Size | Bytes to fetch from Arguments|

## Global Memory Map:

| Address | Size | Space |
| :--- | :--- | :--- |
|0x0000_0000 to <br> 0x0000_0020| 36B|MMIO|
|0x0000_0024 to <br> 0x000F_FFFC| 1MB|Instructions|
|0x0010_0000 to <br> 0x00FF_FFFC| 15MB|Arguments|
|0x1000_0000 to <br> 0xF0FF_FFFC| 3.75GB|Heap|
|0xF100_0000 to <br> 0xFFFF_FFFC| 250MB|Stack|

## Potential Launch Protocol:

1. Host writes kernel to instruction space and data to heap.

2. Host writes to the MMIO, this includes the entry point, dimensions, total threads, argument pointers, and argument size.

3. Host polls the status register until the GPU is IDLE, then writes to the control register to start the GPU.

4. GPU reads the control register, then turns the idle bit off. 

5. GPU latches MMIO values to hardware registers.

6. GPU spawns threads and starts fetch instructions from entry point.

7. GPU writes back values to the heap and once the final thread expires, sends the DONE flag high.
