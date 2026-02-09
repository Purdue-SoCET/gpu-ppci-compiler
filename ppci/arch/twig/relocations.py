from ...utils.bitfun import BitView, wrap_negative
from ..encoding import Relocation
from .tokens import TwigIToken, TwigSToken, TwigJToken, TwigPToken

#our btype doesn't jump, we can use it for 'jal' 17imm and jalr?
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
#need Abs32Imm12Relocation for lmi, lli
#need RelImm12Relocation for auipc
#need Abs32Imm8Relocation for lui


#AbsAddr32Relocation for dcd2 pseudo instr
#this is for labels not sure if we need

class PBImm11Reloc(Relocation):
    name = "pb_imm11"
    token = TwigPToken

    def calc(self, sym_value, reloc_value):
        assert sym_value % 2 == 0
        assert reloc_value % 2 == 0
        off = (sym_value - reloc_value) // 2   # PC-relative
        return wrap_negative(off, 11)

    def apply(self, sym_value, data, reloc_value):
        value = self.calc(sym_value, reloc_value)
        assert 0 <= value < (1 << 11)

        imm_lo6 = value & 0x3F
        imm_hi5 = (value >> 6) & 0x1F

        tok = self.token.from_data(data)
        tok.rs2 = imm_lo6
        tok.imm = imm_hi5
        return tok.encode()
