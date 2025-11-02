module main;

global function i32 main() {
  main_block0: {
    blob<4:4> alloca = alloc 4 bytes aligned at 4;
    ptr alloca_addr = &alloca;
    jmp main_block1;
  }

  main_block1: {
    i32 num = 10;
    store num, alloca_addr;
    ptr num_0 = 4;
    ptr tmp = alloca_addr + num_0;
    jmp main_block2;
  }

  main_block2: {
    i32 tmp_load = load alloca_addr;
    i32 num_1 = 0;
    cjmp tmp_load != num_1 ? main_block3 : main_block4;
  }

  main_block3: {
    i32 tmp_load_2 = load alloca_addr;
    i32 num_3 = 1;
    i32 tmp_4 = tmp_load_2 - num_3;
    store tmp_4, alloca_addr;
    jmp main_block2;
  }

  main_block4: {
    i32 tmp_load_5 = load alloca_addr;
    return tmp_load_5;
  }

}
