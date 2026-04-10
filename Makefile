# Variables
PYTHON ?= python
PIP ?= pip
CI_VENV ?= .venv-ci

# Windows
ifeq ($(OS),Windows_NT)
    SHELL = cmd.exe

    CLEAN_CACHE_CMD = for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" & \
                      del /s /q *.pyc 2>nul & \
                      del /s /q *.pyo 2>nul || exit 0
    CLEAN_CMD = if exist build rd /s /q build & \
                if exist dist rd /s /q dist & \
                for /d %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d" & \
                $(CLEAN_CACHE_CMD)

	CI_PYTHON = $(CI_VENV)\Scripts\python.exe
    CI_STAMP = $(CI_VENV)\.setup-stamp
    CI_BOOTSTRAP_CMD = if not exist "$(CI_PYTHON)" $(PYTHON) -m venv $(CI_VENV)
    CI_INSTALL_CMD = $(CI_PYTHON) -c "from pathlib import Path; import sys; stamp = Path(r'$(CI_STAMP)'); print('CI virtualenv already configured.') if stamp.exists() else None; sys.exit(0 if stamp.exists() else 1)" || ($(CI_PYTHON) -m pip install black flake8 pytest && $(CI_PYTHON) -c "from pathlib import Path; Path(r'$(CI_STAMP)').touch()")
else
    # Linux/Unix/MacOS
    CLEAN_CACHE_CMD = find . -type d -name "__pycache__" -exec rm -rf {} + && \
                      find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
    CLEAN_CMD = rm -rf build/ dist/ *.egg-info && \
                $(CLEAN_CACHE_CMD)

	CI_PYTHON = $(CI_VENV)/bin/python
    CI_STAMP = $(CI_VENV)/.setup-stamp
    CI_BOOTSTRAP_CMD = test -x "$(CI_PYTHON)" || $(PYTHON) -m venv $(CI_VENV)
    CI_INSTALL_CMD = $(CI_PYTHON) -c "from pathlib import Path; import sys; stamp = Path('$(CI_STAMP)'); print('CI virtualenv already configured.') if stamp.exists() else None; sys.exit(0 if stamp.exists() else 1)" || ($(CI_PYTHON) -m pip install black flake8 pytest && $(CI_PYTHON) -c "from pathlib import Path; Path('$(CI_STAMP)').touch()")
endif

.PHONY: help install dev-install clean clean-cache test
.PHONY: ci-setup ci-style-check ci-test ci-check ci-fix

help:
	@echo General targets:
	@echo   make install         - Install the package
	@echo   make dev-install     - Install the package in editable mode
	@echo   make test            - Run pytest
	@echo   make clean           - Remove build artifacts and cache
	@echo   make clean-cache     - Remove Python cache files only
	@$(PYTHON) -c "print()"
	@echo CI targets:
	@echo   make ci-setup        - Create the local CI virtualenv once
	@echo   make ci-style-check  - Run black and flake8 like GitHub CI
	@echo   make ci-test         - Run pytest like GitHub CI
	@echo   make ci-check        - Run the full local CI flow
	@echo   make ci-fix          - Format all Python files with black only
	@$(PYTHON) -c "print()"
	@echo CI options:
	@echo   PYTHON=py            - Use Windows launcher instead of python

install:
	$(PIP) install .

dev-install:
	$(PIP) install -e .

test:
	$(PYTHON) -m pytest

clean:
	@echo Cleaning project...
	@$(CLEAN_CMD)

clean-cache:
	@echo Cleaning cache...
	@$(CLEAN_CACHE_CMD)

# Test
link:
	$(TWIG) src/test.c src/a.c

histogram:
	$(TWIG) src/test.c src/a.c --packet-histogram packets.svg

debug:
	$(TWIG) -S src/test.c --log debug

disasm:
	$(TOOL) --disasm meminit.hex > disasm.S

# GitHub CI process
ci-setup:
	@echo Setting up CI virtualenv...
	@$(CI_BOOTSTRAP_CMD)
	@$(CI_INSTALL_CMD)

ci-style-check: ci-setup
	@echo Running black check...
	@$(CI_PYTHON) -m black --check .
	@echo Running flake8...
	@$(CI_PYTHON) -m flake8 ppci test tools

ci-test: ci-setup
	@echo Running pytest...
	@$(CI_PYTHON) -m pytest

ci-check: ci-style-check ci-test

ci-fix:
	@$(MAKE) ci-setup PYTHON=$(PYTHON) PIP=$(PIP) CI_VENV=$(CI_VENV)
	@echo Applying conservative CI fixes with black...
	@$(CI_PYTHON) -m black .
	@echo Run 'make ci-style-check' or 'make ci-check' to verify.
