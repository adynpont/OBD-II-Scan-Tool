import serial, time
import serial.tools.list_ports

class ELMConnection:
    def __init__(self, port=None, baud=38400, timeout=1):
        if port is None:
            port = self.auto_detect()
        if not port:
            raise Exception("No OBD-II device detected. Check your connection and ignition")
        self.ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(1)
        self.initialize()

    def auto_detect(self):
        for p in serial.tools.list_ports.comports():
            try:
                s = serial.Serial(p.device, baudrate=38400, timeout=1)
                s.write(b"ATZ\r")
                time.sleep(0.5)
                r = s.read_all().decode(errors="ignore")
                s.close()
                if "ELM327" in r.upper():
                    return p.device
            except:
                pass
        return None

    def send(self, cmd):
        self.ser.write((cmd + "\r").encode())
        time.sleep(0.2)
        return self.ser.read_all().decode(errors="ignore").strip()

    def initialize(self):
        for c in ["ATZ", "ATE0", "ATL0", "ATS0", "ATH0", "ATSP0"]:
            self.send(c)
