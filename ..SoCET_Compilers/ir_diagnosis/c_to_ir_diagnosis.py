def build(self, src: io.TextIOBase, filename: str, reporter=None):
        if reporter:
            reporter.heading(2, "C builder")
            reporter.message(
                f"Welcome to the C building report for {filename}"
            )
        cdialect = self.coptions["std"]
        self.logger.info("Starting C compilation (%s)", cdialect)
                                                                    # <<<<<========= IMPORTANT STARTS HERE
        context = CContext(self.coptions, self.arch_info) # holds all global state needed during compilation, such as the compilation options
        compile_unit = _parse(src, filename, context) # <<<<<<<<====== Analyze to Build AST

        if reporter:
            f = io.StringIO()
            print_ast(compile_unit, file=f)
            reporter.dump_source("C-ast", f.getvalue())
        cgen = CCodeGenerator(context) # <<<<<<<<====== Walks down AST To Build IR
        return cgen.gen_code(compile_unit)

# ---------------------------------------------------------------------------------

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

    ir_module = cbuilder.build(source, filename, reporter=reporter) # <<<==== IMPORTANT PART TO LOOK INTO
    # Performs entire frontend pipeline
    # 1) Preprocessing; handling #include and #define
    # 2) Parsing: Reads C code and breaks into tokens to build (AST)
    # 3) Generates IR by walking down AST
    # 4) Stores IR in ir_module
    return ir_module
