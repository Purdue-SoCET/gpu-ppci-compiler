"""Packetization using the pipe-filter approach.

We intercept all emitted instructions for a frame, buffer them,
and then apply the architecture-specific packetization logic
(dependency checking, start/end bit tagging) when flushed.
"""

import logging

from ppci.binutils.outstream import OutputStream

logger = logging.getLogger("packetize")


class PacketizeStream(OutputStream):
    """This is a packetizing output stream.

    It collects instructions in a buffer instead of emitting them immediately.
    When flush() is called, it triggers the architecture's packetize logic
    to group instructions, and then emits the modified instructions downstream.
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
            if hasattr(self._arch, 'packetize'):
                self._arch.packetize(self._buffer)
            else:
                pass

            for item in self._buffer:
                self._downstream.emit(item)

            self._buffer.clear()