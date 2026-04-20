"""
RFC Algorithm

Takes an already allocated instruction stream and applies performs register renaming
to optimize for the Register File Cache (RFC) architecture.
"""

import logging

from ppci.binutils.outstream import OutputStream

logger = logging.getLogger("rfc")


class RFCStream(OutputStream):
    """This is an RFC optimizer output stream.

    It collects instructions in a buffer instead of emitting them immediately.
    When flush() is called, it triggers the rfc algo to optimize the instructions
    for the RFC
    """

    def __init__(self, downstream, arch):
        super().__init__()
        self._downstream = downstream
        self._arch = arch
        self._buffer = []

    def do_emit(self, item):
        """Intercept the emitted item and store it in the buffer."""
        self._buffer.append(item)

    def flush(self):
        """Process the buffered items and flush downstream."""
        if self._buffer:
            if hasattr(self._arch, "rfc_register_renaming"):
                self._arch.rfc_register_renaming(self._buffer)
            else:
                pass

            for item in self._buffer:
                self._downstream.emit(item)

            self._buffer.clear()
