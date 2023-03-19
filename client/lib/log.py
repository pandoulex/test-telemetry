#!/usr/bin/python
from __future__ import unicode_literals

import logging
import struct


class CustomLogger(logging.Handler):
    def __init__(self, socket):
        super(CustomLogger, self).__init__()
        self._socket = socket
        self._packet_type = struct.pack('<c', b'L')

    def emit(self, record):
        """
        :param logging.LogRecord record:
        """
        log_level = struct.pack('<i', record.levelno)
        msg = self.format(record).encode('utf-8')
        print("sending log: %s" % msg)
        packet_len = struct.pack('<L', len(log_level) + len(msg))
        self._socket.sendall(self._packet_type + packet_len + log_level + msg)
