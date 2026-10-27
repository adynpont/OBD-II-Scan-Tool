import ctypes
import os

_lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "libelm327.so"))

_lib.py_open_port.argtypes = []
_lib.py_open_port.restype = ctypes.c_int

_lib.py_send_command.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
_lib.py_send_command.restype = ctypes.c_int

_lib.py_close_port.argtypes = [ctypes.c_int]
_lib.py_close_port.restype = None


class ELM327:
    def __init__(self):
        self.fd = _lib.py_open_port()
        if self.fd < 0:
            raise Exception("Failed to open ELM327 device")
        # Echo off, linefeeds off, spaces on, headers off, auto protocol
        for at_cmd in ("ATE0", "ATL0", "ATS1", "ATH0", "ATSP0"):
            self.send(at_cmd)

    def send(self, cmd: str) -> str:
        full_cmd = (cmd + "\r").encode()
        buf = ctypes.create_string_buffer(256)
        n = _lib.py_send_command(self.fd, full_cmd, buf, 256)
        if n <= 0:
            raise Exception("No response from device")
        return buf.value.decode(errors="ignore").strip()

    def close(self):
        if self.fd >= 0:
            _lib.py_close_port(self.fd)
            self.fd = -1

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass