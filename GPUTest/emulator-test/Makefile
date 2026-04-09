PYTHON := python3
EMULATOR := cardinal-ISS/src/emulator.py

# Default Parameters (Overridden by the generic test script)
THREADS ?= 32
BLOCKS ?= 1
START_PC ?= 0
INPUT ?= meminit.hex
FORMAT ?= hex

# The Interface
run:
	$(PYTHON) $(EMULATOR) -t $(THREADS) -b $(BLOCKS) --start-pc $(START_PC) --mem-format $(FORMAT) $(INPUT)

clean:
	rm -f *.out *.log *.hex
	rm -rf test_diffs/* build/*

# compiler commands
O ?= 0
compile-%:
	mkdir -p build
	twig ../benchmark/kernels/$*.c \
		--hex-output build/$*.hex \
		--bin-output build/$*.bin \
		--entry kernel_$* -O$(O) \
		--stack-info-output build/$*.stack.json \
		--packet-histogram build/$*_packets.svg \
		$(TWIG_ARGS)

disasm-%: compile-%
	tool --disasm build/$*.bin > build/$*_disasm.txt

build-%: disasm-%
	mkdir -p tests/complex_tests/$*
	cp -f build/$*.hex tests/complex_tests/$*/$*.hex
	cp -f build/$*.stack.json tests/complex_tests/$*/$*.stack.json

test-%:
	@TEST_ARGS=""; \
	if [ -n "$(t)" ]; then TEST_ARGS="$$TEST_ARGS -t $(t)"; fi; \
	if [ -n "$(l)" ]; then TEST_ARGS="$$TEST_ARGS -l $(l)"; fi; \
	./test_hex.sh $$TEST_ARGS --start-pc 0x24 --arg-pointer 0x1C tests/complex_tests/$*/$*.hex

diffs:
	python3 tests/diffs.py

data:
	make -C ../benchmark clean && make -C ../benchmark run32

dataclean:
	find tests/complex_tests -type f \( -name "*_data*" -o -name "*_exp*" \) -name "*.hex" -delete

datacopy:
	@bench_dir=../benchmark/build; \
	for infile in $${bench_dir}/*Input.txt $${bench_dir}/*Input0.txt; do \
		[ -e "$$infile" ] || continue; \
		filename=$$(basename "$$infile"); \
		kernel=$${filename%Input*}; \
		outdir=tests/complex_tests/$$kernel; \
		mkdir -p $$outdir; \
		cp -f "$$infile" $$outdir/$${kernel}_data.hex; \
		if [ -f "$$bench_dir/$${kernel}Output.txt" ]; then \
			cp -f "$$bench_dir/$${kernel}Output.txt" $$outdir/$${kernel}_exp_t$(t)_b1.hex; \
		elif [ -f "$$bench_dir/$${kernel}Output0.txt" ]; then \
			cp -f "$$bench_dir/$${kernel}Output0.txt" $$outdir/$${kernel}_exp_t$(t)_b1.hex; \
		fi; \
	done

fix:
	sed -i 's/\r$$//' setup.sh
	sed -i 's/\r$$//' test_hex.sh

BLUE = \033[1;34m
NC = \033[0m   # No Color
SHELL := /bin/bash

auto-data-%:
	@echo -e "\n$(BLUE)>>> [1/5] Generating CPU standard test data (make data)...$(NC)"
	make data

	@echo -e "\n$(BLUE)>>> [2/5] Copying and converting test data (make datacopy)...$(NC)"
	make datacopy

auto-test-%:
	@echo -e "\n$(BLUE)>>> [3/5] Compiling C code with twig and extracting Hex (make build-$*)...$(NC)"
	#make build-$* TWIG_ARGS="--no-packetize"
	make build-$*

	@echo -e "\n$(BLUE)>>> [4/5] Starting emulator for comparison testing (make test-$*)...$(NC)"
	-make test-$*

	@echo -e "\n$(BLUE)>>> [5/5] Generating memory difference report (make diffs)...$(NC)"
	make diffs
	@echo -e "\n$(BLUE)>>> Test process completed! Please check the reports in the test_diffs/ directory.$(NC)"
