# Workflow (from emulator-test/):
#   make data-<kernel> && make datacopy && make build-<kernel> && make run KERNEL=<kernel>
#   `make run` defaults to KERNEL=vertexShader. Shorthand: make run-saxpy, run-triangle, run-pixel, run-vertexShader.
# Pixel: CPU launch is 1024 threads (32×32). Use `make data-pixel` (copies exp as t1024), `make test-pixel`,
#   and `make run KERNEL=pixel THREADS=1024` (or `make run-pixel` from repo root).
# Optional: COUNT=1|2, THREADS=, BLOCKS=. (Pattern rules like run-% are not portable on BSD make.)
# MEMACCESS=1 reads, 2 writes, 3 both → memory histogram JSON + PNG (needs matplotlib in venv).
# MEMACCESS_BINSIZE=bytes per bin (default 64); use 256 or 4096 to merge addresses for busy kernels like triangle.
# MEMACCESS_OUT=build/myhist
# MEMCOAL=1 → PNG build/$(KERNEL)_memcloalescing.png (distinct 128 B lines/op, x-axis 1–32).

ifeq ($(origin PYTHON),undefined)
  ifneq ($(wildcard cardinal-ISS/.venv/Scripts/python.exe),)
    PYTHON := cardinal-ISS/.venv/Scripts/python.exe
  else
    ifneq ($(wildcard cardinal-ISS/.venv/bin/python),)
      PYTHON := cardinal-ISS/.venv/bin/python
    else
      PYTHON := python3
    endif
  endif
endif

TWIG ?= twig
TOOL ?= tool
EMULATOR := cardinal-ISS/src/emulator.py

KERNEL ?= vertexShader
THREADS ?= 32
BLOCKS ?= 1
START_PC ?= 0
FORMAT ?= hex
COUNT ?=
REF_THREADS ?= $(if $(t),$(t),32)
REF_BLOCKS ?= $(if $(b),$(b),1)

COUNT_ARG := $(if $(COUNT),--count $(COUNT),)
MEMACCESS_OUT ?=
MEMACCESS_BINSIZE ?= 64
MEMACCESS_ARG := $(if $(filter 1 2 3,$(MEMACCESS)),--mem-hist $(MEMACCESS) --mem-hist-bin-size $(MEMACCESS_BINSIZE) --mem-hist-out $(if $(MEMACCESS_OUT),$(MEMACCESS_OUT),build/memaccess_$(KERNEL)),)
MEMCOAL_ARG := $(if $(filter 1,$(MEMCOAL)),--mem-coal --mem-coal-out build/memcoales_$(KERNEL).png,)

O ?= 0

# --- data / compile / run -------------------------------------------------

data:
	@$(MAKE) data-$(KERNEL)

# saxpy uses cpu_sim/saxpy_main.c via benchmark `custom`, not the graphics run32 main.
data-saxpy:
	$(MAKE) -C ../benchmark clean
	$(MAKE) -C ../benchmark custom KERNEL=saxpy
	@$(PYTHON) tests/saxpy_relocate.py

# run32 uses block_dim = 32×32 = 1024 for pixel; copy golden as _exp_t1024_b1 (generic datacopy defaults to t32).
data-pixel:
	$(MAKE) -C ../benchmark clean && $(MAKE) -C ../benchmark run32 KERNEL=pixel
	@bench_dir=../benchmark/build; outdir=tests/complex_tests/pixel; \
	mkdir -p $$outdir; \
	if [ -f $$bench_dir/pixelInput.txt ]; then \
		cp -f $$bench_dir/pixelInput.txt $$outdir/pixel_data.hex; \
	else echo "Missing $$bench_dir/pixelInput.txt (enable PIXEL_PRINT_DEBUG in cpu_sim/main.c)"; exit 1; \
	fi; \
	if [ -f $$bench_dir/pixelOutput.txt ]; then \
		cp -f $$bench_dir/pixelOutput.txt $$outdir/pixel_exp_t1024_b1.hex; \
	elif [ -f $$bench_dir/pixelOutput0.txt ]; then \
		cp -f $$bench_dir/pixelOutput0.txt $$outdir/pixel_exp_t1024_b1.hex; \
	else echo "Missing pixelOutput.txt"; exit 1; \
	fi

data-%:
	$(MAKE) -C ../benchmark clean && $(MAKE) -C ../benchmark run32 KERNEL=$*

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
			cp -f "$$bench_dir/$${kernel}Output.txt" $$outdir/$${kernel}_exp_t$(REF_THREADS)_b$(REF_BLOCKS).hex; \
		elif [ -f "$$bench_dir/$${kernel}Output0.txt" ]; then \
			cp -f "$$bench_dir/$${kernel}Output0.txt" $$outdir/$${kernel}_exp_t$(REF_THREADS)_b$(REF_BLOCKS).hex; \
		fi; \
	done; \
	if [ -f ../benchmark/build/saxpyInput.txt ] && [ -f ../benchmark/build/saxpyOutput.txt ]; then \
		$(PYTHON) tests/saxpy_relocate.py; \
	fi

compile-%:
	mkdir -p build
	$(TWIG) ../benchmark/kernels/$*.c \
		--hex-output build/$*.hex \
		--bin-output build/$*.bin \
		--entry kernel_$* -O$(O) \
		--stack-info-output build/$*.stack.json \
		--packet-histogram build/$*_packets.svg \
		$(TWIG_ARGS)

disasm-%: compile-%
	$(TOOL) --disasm build/$*.bin > build/$*_disasm.txt

build-%: disasm-%
	mkdir -p tests/complex_tests/$*
	cp -f build/$*.hex tests/complex_tests/$*/$*.hex
	cp -f build/$*.stack.json tests/complex_tests/$*/$*.stack.json

# One merge + emulator invocation for any kernel (KERNEL must match tests/complex_tests/<KERNEL>/).
MEMINIT := build/meminit-$(KERNEL).hex
KHEX := tests/complex_tests/$(KERNEL)/$(KERNEL).hex
KDATA := tests/complex_tests/$(KERNEL)/$(KERNEL)_data.hex
KSTACK := tests/complex_tests/$(KERNEL)/$(KERNEL).stack.json

meminit:
	@test -f $(KHEX) || (echo "Missing $(KHEX); run: make build-$(KERNEL)"; exit 1)
	@mkdir -p build
	awk '{v=$$0; gsub(/^0x/,"",v); printf "0x%08x 0x%s\n", (NR-1)*4, v}' $(KHEX) > $(MEMINIT)
	@test -f $(KDATA) && cat $(KDATA) >> $(MEMINIT) || true

run: meminit
	@FLAGS=$$($(PYTHON) tests/emu_run_flags.py $(MEMINIT) --stack-json $(KSTACK)); \
	$(PYTHON) $(EMULATOR) -t $(THREADS) -b $(BLOCKS) --start-pc $(START_PC) \
		--mem-format $(FORMAT) $(COUNT_ARG) $(MEMACCESS_ARG) $(MEMCOAL_ARG) $$FLAGS $(MEMINIT)

# Convenience forwards (same as `make run KERNEL=...`; COUNT=/THREADS= pass through from the command line).
# Triangle test image uses bb_size 31×31 → 961 threads (see triangle_data.hex words 3–4).
run-triangle:
	@$(MAKE) run KERNEL=triangle THREADS=961

run-vertexShader:
	@$(MAKE) run KERNEL=vertexShader

run-pixel:
	@$(MAKE) run KERNEL=pixel THREADS=1024

run-saxpy:
	@$(MAKE) run KERNEL=saxpy

# --- misc -----------------------------------------------------------------

setup:
	cd cardinal-ISS && bash setup.sh

clean:
	rm -f *.out *.log meminit.hex
	rm -rf test_diffs/* build/*

test-%:
	@TEST_ARGS=""; \
	if [ -n "$(t)" ]; then TEST_ARGS="$$TEST_ARGS -t $(t)"; fi; \
	if [ -n "$(l)" ]; then TEST_ARGS="$$TEST_ARGS -l $(l)"; fi; \
	bash ./test_hex.sh $$TEST_ARGS tests/complex_tests/$*/$*.hex

# After test-%: pattern also matches test-pixel; this recipe must come last so it wins.
test-pixel:
	@TEST_ARGS=""; \
	if [ -n "$(t)" ]; then TEST_ARGS="$$TEST_ARGS -t $(t)"; else TEST_ARGS="$$TEST_ARGS -t 1024"; fi; \
	if [ -n "$(l)" ]; then TEST_ARGS="$$TEST_ARGS -l $(l)"; fi; \
	bash ./test_hex.sh $$TEST_ARGS tests/complex_tests/pixel/pixel.hex

# CPU vs emu: float bits differ slightly; RELAX_FP_HEX enables tests/hex_mem_compare.py.
test-vertexShader:
	@TEST_ARGS=""; \
	if [ -n "$(t)" ]; then TEST_ARGS="$$TEST_ARGS -t $(t)"; fi; \
	if [ -n "$(l)" ]; then TEST_ARGS="$$TEST_ARGS -l $(l)"; fi; \
	RELAX_FP_HEX=1 bash ./test_hex.sh $$TEST_ARGS tests/complex_tests/vertexShader/vertexShader.hex

# Default -t 961 matches bb_size[0]*bb_size[1] in triangle_data.hex (31×31). Override with make test-triangle t=N
test-triangle:
	@TEST_ARGS=""; \
	if [ -n "$(t)" ]; then TEST_ARGS="$$TEST_ARGS -t $(t)"; else TEST_ARGS="$$TEST_ARGS -t 961"; fi; \
	if [ -n "$(l)" ]; then TEST_ARGS="$$TEST_ARGS -l $(l)"; fi; \
	RELAX_FP_HEX=1 bash ./test_hex.sh $$TEST_ARGS tests/complex_tests/triangle/triangle.hex

diffs:
	$(PYTHON) tests/diffs.py

dataclean:
	find tests/complex_tests -type f \( -name "*_data*" -o -name "*_exp*" \) -name "*.hex" -delete

fix:
	sed -i 's/\r$$//' cardinal-ISS/setup.sh
	sed -i 's/\r$$//' test_hex.sh

SHELL := /bin/bash

.PHONY: data data-saxpy data-pixel datacopy compile-% disasm-% build-% meminit run run-triangle run-vertexShader run-pixel run-saxpy setup clean test-pixel test-vertexShader test-triangle test-% diffs dataclean fix
