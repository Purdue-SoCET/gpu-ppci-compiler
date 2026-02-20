from ...utils.bitfun import wrap_negative
from ..encoding import Relocation
from .tokens import TwigJToken, TwigPDisasToken


# our btype doesn't jump, we can use it for 'jal' 17imm and jalr?
class JImm17Relocation(Relocation):
    name = "j_imm17"
    token = TwigJToken
    field = "imm"

    def calc(self, sym_value, reloc_value):
        assert sym_value % 2 == 0
        assert reloc_value % 2 == 0
        offset = (sym_value - reloc_value) // 2
        return wrap_negative(offset, 17)

    def apply(self, sym_value, data, reloc_value):
        """Apply this relocation type given some parameters.

        This is the default implementation which stores the outcome of
        the calculate function into the proper token."""
        assert self.token is not None
        token = self.token.from_data(data)
        assert self.field is not None
        assert hasattr(token, self.field)
        setattr(token, self.field, self.calc(sym_value, reloc_value))
        return token.encode()


# TDOO: Check for all relocations
# need Abs32Imm12Relocation for lmi, lli
# need RelImm12Relocation for auipc
# need Abs32Imm8Relocation for lui


# AbsAddr32Relocation for dcd2 pseudo instr
# this is for labels not sure if we need


class PBImm12Relocation(Relocation):
    """Relocation for jpnz: 12-bit PC-relative offset in bits [24:13]."""

    name = "pb_imm12"
    token = TwigPDisasToken
    field = "imm"

    def calc(self, sym_value, reloc_value):
        assert sym_value % 2 == 0
        assert reloc_value % 2 == 0
        off = (sym_value - reloc_value) // 2  # PC-relative
        return wrap_negative(off, 12)

    def apply(self, sym_value, data, reloc_value):
        value = self.calc(sym_value, reloc_value)
        assert 0 <= value < (1 << 12)

        tok = self.token.from_data(data)
        tok.imm = value
        return tok.encode()
