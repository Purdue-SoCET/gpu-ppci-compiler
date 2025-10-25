import io

from ...utils.reporting import DummyReportGenerator
from .builder import CBuilder
from .options import COptions
from .preprocessor import CPreProcessor
from .token import CTokenPrinter


def preprocess(f, output_file, coptions=None):
    """Pre-process a file into the other file."""
    if coptions is None:
        coptions = COptions()
    preprocessor = CPreProcessor(coptions)
    filename = f.name if hasattr(f, "name") else None
    tokens = preprocessor.process_file(f, filename=filename)
    CTokenPrinter().dump(tokens, file=output_file)


def c_to_ir(source: io.TextIOBase, march, coptions=None, reporter=None):
    """C to ir translation.

    Args:
        source (file-like object): The C source to compile.
        march (str): The targetted architecture.
        coptions: C specific compilation options.

    Returns:
        An :class:`ppci.ir.Module`.
    """

    if not reporter:  # pragma: no cover
        reporter = DummyReportGenerator()

    if not coptions:  # pragma: no cover
        coptions = COptions()

    from ...api import get_arch # <<== IMPORTANT FOR US
    # Gets architecture

    march = get_arch(march) # Loads architecture
    cbuilder = CBuilder(march.info, coptions) #<== IMPORTANT FOR US
    #Given target architecture and C options


    assert isinstance(source, io.TextIOBase)
    if hasattr(source, "name"):
        filename = getattr(source, "name")
        # Gets file name from source for error messages
    else:
        filename = None

    ir_module = cbuilder.build(source, filename, reporter=reporter)
    # Performs entire frontend pipeline
    # 1) Preprocessing; handling #include and #define
    # 2) Parsing: Reads C code and breaks into tokens to build (AST)
    # 3) Generates IR by walking down AST
    # 4) Stores IR in ir_module
    return ir_module
