# Variables
PYTHON = python
PIP = pip
TWIG = twig
TOOL = tool

# Windows
ifeq ($(OS),Windows_NT)
    SHELL = cmd.exe

    CLEAN_CMD = if exist build rd /s /q build & \
                if exist dist rd /s /q dist & \
                if exist *.egg-info rd /s /q *.egg-info & \
                for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" & \
                del /s /q *.pyc 2>nul || exit 0
else
    # Linux/Unix/MacOS
    CLEAN_CMD = rm -rf build/ dist/ *.egg-info && \
                find . -type d -name "__pycache__" -exec rm -rf {} + && \
                find . -type f -name "*.pyc" -delete
endif

.PHONY: help install dev-install clean test

help:
	@echo "Usage:"
	@echo "  make install      - Install the package normally"
	@echo "  make dev-install  - Install the package in editable mode (pip install -e .)"
	@echo "  make clean        - Remove build artifacts and cache"
	@echo "  make test         - Run tests using pytest"

install:
	$(PIP) install .

dev-install:
	$(PIP) install -e .

test:
	$(PYTHON) -m pytest

link:
	$(TWIG) src/test.c src/a.c

debug:
	$(TWIG) -S src/test.c --log debug

disasm:
	$(TOOL) --disasm meminit.hex > disasm.S

package-check:
	@echo "Check code style"
	black --check .
	@echo "Static code analysis"
	flake8 ppci test tools

fix-package-check:
	@echo "Fix code style"
	black .
	@echo "Fix Static code analysis"
	autopep8 --in-place --aggressive --recursive .

clean:
	@echo Cleaning project...
	@$(CLEAN_CMD)