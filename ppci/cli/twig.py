import argparse
import sys

from .. import api
from ..lang.c import CAstPrinter, create_ast
from ..lang.c.options import COptions, coptions_parser
from .base import LogSetup, base_parser  # NOTE: don't import march_parser
from .compile_base import compile_parser, do_compile
from ..arch import get_arch  # to resolve 'twig' arch

parser = argparse.ArgumentParser(
    description="Twig C compiler (alias of 'ppci-cc -m twig')",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[base_parser, compile_parser, coptions_parser],
)
parser.add_argument("-E", action="store_true", default=False, help="Stop after preprocessing")
parser.add_argument("-M", action="store_true", default=False, help="Emit makefile dependency rule")
parser.add_argument("--ast", action="store_true", default=False, help="Dump C AST and stop")
parser.add_argument("-c", action="store_true", default=False, help="Compile, but do not link")
parser.add_argument("sources", metavar="source", nargs="+", type=argparse.FileType("r"))

def twig(argv=None):
    args = parser.parse_args(argv)
    with LogSetup(args) as log_setup:
        march = get_arch("twig")  # hard-code target arch

        coptions = COptions()
        coptions.process_args(args)

        if args.E:
            with open(args.output, "w") as out:
                for src in args.sources:
                    api.preprocess(src, out, coptions)
            return 0

        if args.M:
            # Fill if you implement dep scanning; placeholder now.
            return 0

        if args.ast:
            with open(args.output, "w") as out:
                printer = CAstPrinter(file=out)
                for src in args.sources:
                    filename = getattr(src, "name", None)
                    ast = create_ast(src, march.info, filename=filename, coptions=coptions)
                    printer.print(ast)
            return 0

        ir_modules = []
        for src in args.sources:
            irm = api.c_to_ir(src, march, coptions=coptions, reporter=log_setup.reporter)
            ir_modules.append(irm)

        do_compile(ir_modules, march, log_setup.reporter, log_setup.args)
        return 0

if __name__ == "__main__":
    sys.exit(twig(sys.argv[1:]))
