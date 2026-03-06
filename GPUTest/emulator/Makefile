PYTHON := python3
EMULATOR := src/emulator.py

# Default Parameters (Overridden by the generic test script)
THREADS ?= 32
BLOCKS ?= 1
START_PC ?= 0
INPUT ?= meminit.hex
FORMAT ?= hex
O ?= 0

# The Interface
run:
	$(PYTHON) $(EMULATOR) -t $(THREADS) -b $(BLOCKS) --start-pc $(START_PC) --mem-format $(FORMAT) $(INPUT)

compile-%:
	mkdir -p build
	twig ../benchmark/kernels/$*.c --hex-output build/$*.bin --entry kernel_$* -O$(O)

disasm-%: compile-%
	tool --disasm build/$*.bin > build/$*_disasm.txt

build-%: disasm-%
	mkdir -p tests/complex_tests/$*
	awk 'NR>2 && $$3 != "" {print $$3}' build/$*_disasm.txt > tests/complex_tests/$*/$*.hex

clean:
	rm -f *.out *.log *.hex
	rm -rf test_diffs/* build/*

dataclean:
	find tests/complex_tests -type f \( -name "*_data*" -o -name "*_exp*" \) -name "*.hex" -delete

data:
	@bench_dir=../benchmark/build; \
	for infile in $${bench_dir}/*Input.txt $${bench_dir}/*Input0.txt; do \
		[ -e "$$infile" ] || continue; \
		filename=$$(basename "$$infile"); \
		kernel=$${filename%Input*}; \
		outdir=tests/complex_tests/$$kernel; \
		mkdir -p $$outdir; \
		cp -f "$$infile" $$outdir/$${kernel}_data.hex; \
		if [ -f "$$bench_dir/$${kernel}Output.txt" ]; then \
			cp -f "$$bench_dir/$${kernel}Output.txt" $$outdir/$${kernel}_exp_t32_b1.hex; \
		elif [ -f "$$bench_dir/$${kernel}Output0.txt" ]; then \
			cp -f "$$bench_dir/$${kernel}Output0.txt" $$outdir/$${kernel}_exp_t32_b1.hex; \
		fi; \
	done
