module main;

global function i32 main() {
  main_block0: {
    blob<4:4> alloca = alloc 4 bytes aligned at 4;
    ptr alloca_addr = &alloca;
    i32 num = 10;
    store num, alloca_addr;
    ptr num_0 = 4;
    ptr tmp = alloca_addr + num_0;
    blob<4:4> alloca_1 = alloc 4 bytes aligned at 4;
    ptr alloca_addr_2 = &alloca_1;
    i32 num_3 = 0;
    store num_3, alloca_addr_2;
    ptr num_4 = 4;
    ptr tmp_5 = alloca_addr_2 + num_4;
    jmp main_block1;
  }

  main_block1: {
    i32 tmp_load = load alloca_addr_2;
    i32 num_6 = 10;
    cjmp tmp_load < num_6 ? main_block2 : main_block3;
  }

  main_block2: {
    i32 tmp_load_7 = load alloca_addr_2;
    i32 tmp_load_8 = load alloca_addr;
    i32 tmp_9 = tmp_load_8 + tmp_load_7;
    store tmp_9, alloca_addr;
    i32 tmp_load_10 = load alloca_addr_2;
    i32 num_11 = 1;
    i32 tmp_12 = tmp_load_10 + num_11;
    store tmp_12, alloca_addr_2;
    jmp main_block1;
  }

  main_block3: {
    i32 tmp_load_13 = load alloca_addr;
    return tmp_load_13;
  }

}
