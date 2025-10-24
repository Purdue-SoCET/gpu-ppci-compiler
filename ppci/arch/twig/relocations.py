from ...utils.bitfun import BitView, wrap_negative
from ..encoding import Relocation
from .tokens import TwigIToken, TwigSToken, TwigJToken

#this is normally for btype in risc-v
#since our btype doesn't jump, we can use it for 'jal' 6imm jump
class BImm6Relocation(Relocation):
    name = "b_imm6"
    token = TwigJToken
    field = "imm"

    def calc(self, sym_value, reloc_value):
        assert sym_value % 2 == 0
        assert reloc_value % 2 == 0
        offset = (sym_value - reloc_value) // 2
        return wrap_negative(offset, 6)

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

#need Abs32Imm12Relocation for lmi, lli
#need RelImm12Relocation for auipc
#need Abs32Imm8Relocation for lui


#AbsAddr32Relocation for dcd2 pseudo instr
#this is for labels not sure if we need
