from elm327 import ELM327
from parser import parse_response


class OBD:
    def __init__(self):
        self.conn = ELM327()

    def _query(self, pid):
        resp = self.conn.send(pid)
        return parse_response(pid, resp)

    def get_rpm(self):
        return self._query("010C")

    def get_speed(self):
        return self._query("010D")

    def get_coolant_temp(self):
        return self._query("0105")

    def get_dtc(self):
        resp = self.conn.send("03")
        return self._parse_dtc(resp)

    def clear_dtc(self):
        resp = self.conn.send("04")
        if "44" in resp.upper():
            return True
        return False

    def fuel_system_status(self):
        return self._query("0103")

    def get_fuel_pressure(self):
        return self._query("010A")

    def get_maf_airflow_rate(self):
        return self._query("0110")

    O2_PIDS = {
        1: "0114", 2: "0115", 3: "0116", 4: "0117",
        5: "0118", 6: "0119", 7: "011A", 8: "011B",
    }

    def get_oxygen(self, sensor_num):
        pid = self.O2_PIDS.get(sensor_num)
        if not pid:
            raise ValueError(f"Invalid O2 sensor number: {sensor_num}")
        return self._query(pid)

    def _parse_dtc(self, response):
        if not response:
            return []

        parts = response.replace("\r", " ").replace("\n", " ").split()
        if parts and parts[0].upper() == "43":
            parts = parts[1:]

        codes = []
        first_char_map = {0: "P", 1: "C", 2: "B", 3: "U"}

        for i in range(0, len(parts) - 1, 2):
            try:
                byte1 = int(parts[i], 16)
                byte2 = int(parts[i + 1], 16)
            except ValueError:
                continue

            if byte1 == 0 and byte2 == 0:
                continue

            first_char = first_char_map[(byte1 >> 6) & 0x03]
            digit2 = (byte1 >> 4) & 0x03
            digit3 = byte1 & 0x0F
            digit4 = (byte2 >> 4) & 0x0F
            digit5 = byte2 & 0x0F

            code = f"{first_char}{digit2}{digit3:X}{digit4:X}{digit5:X}"
            codes.append(code)

        return codes