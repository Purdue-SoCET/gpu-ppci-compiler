# Delegate to emulator-test. Prefer: make -C emulator-test run KERNEL=<name>
.PHONY: help run-triangle run-vertexShader run-pixel run-saxpy

help:
	@echo "From repo root:"
	@echo "  make -C emulator-test run KERNEL=triangle COUNT=2"
	@echo "  make run-triangle    # alias (same as above with KERNEL=triangle)"

run-triangle:
	@$(MAKE) -C emulator-test run KERNEL=triangle THREADS=961

run-vertexShader:
	@$(MAKE) -C emulator-test run KERNEL=vertexShader

run-pixel:
	@$(MAKE) -C emulator-test run KERNEL=pixel THREADS=1024

run-saxpy:
	@$(MAKE) -C emulator-test run KERNEL=saxpy

%:
	@$(MAKE) -C emulator-test $@
	@$(MAKE) -C benchmark $@
