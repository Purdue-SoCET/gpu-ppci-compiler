"""Pytest configuration: skip tests not relevant to the twig backend
and C compilation pipeline.

Kept: C language tests, codegen, core infrastructure (IR, ISA,
encoding, assembler, optimizer, bitfun, bintools, hexutil),
graph/util helpers, arch/test_arch.py (generic frame tests),
parsing tools, test_commands, test_emulation, test_static_link,
and all sample tests.
"""

import os

_here = os.path.dirname(__file__)

# Directories to skip entirely (relative to this conftest)
_skip_dirs = [
    os.path.join(_here, "wasm"),
    os.path.join(_here, "format"),
    os.path.join(_here, "cli"),
    os.path.join(_here, "binutils"),
    os.path.join(_here, "lang", "fortran"),
]

# Individual files to skip (relative to this conftest)
_skip_files = [
    # Architecture-specific tests (not twig)
    os.path.join(_here, "arch", "test_armasm.py"),
    os.path.join(_here, "arch", "test_thumbasm.py"),
    os.path.join(_here, "arch", "test_x86asm.py"),
    os.path.join(_here, "arch", "test_x86_sse.py"),
    os.path.join(_here, "arch", "test_x86_c_inline_asm.py"),
    os.path.join(_here, "arch", "test_riscvasm.py"),
    os.path.join(_here, "arch", "test_riscvrvcasm.py"),
    os.path.join(_here, "arch", "test_msp430asm.py"),
    os.path.join(_here, "arch", "test_stm8asm.py"),
    os.path.join(_here, "arch", "test_or1k.py"),
    os.path.join(_here, "arch", "test_mips.py"),
    os.path.join(_here, "arch", "test_m68k.py"),
    os.path.join(_here, "arch", "test_microblaze.py"),
    os.path.join(_here, "arch", "test_avr.py"),
    os.path.join(_here, "arch", "test_xtensa.py"),
    os.path.join(_here, "arch", "test_6500asm.py"),
    # Other language frontends (not C)
    os.path.join(_here, "lang", "test_bf.py"),
    os.path.join(_here, "lang", "test_c3.py"),
    os.path.join(_here, "lang", "test_ocaml.py"),
    os.path.join(_here, "lang", "test_pascal.py"),
    os.path.join(_here, "lang", "test_python.py"),
    os.path.join(_here, "lang", "test_python2wasm.py"),
    os.path.join(_here, "lang", "test_ws.py"),
    # x86 JIT / codepage
    os.path.join(_here, "test_codepage.py"),
    # Other non-relevant features
    os.path.join(_here, "test_java.py"),
    os.path.join(_here, "test_llvmir.py"),
    os.path.join(_here, "test_doc.py"),
    os.path.join(_here, "test_program.py"),
    os.path.join(_here, "test_tasks.py"),
]

collect_ignore = _skip_dirs + _skip_files
