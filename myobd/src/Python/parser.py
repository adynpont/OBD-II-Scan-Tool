FUEL_SYSTEM_STATUS = {
    0x01: "Open loop (insufficient temp)",
    0x02: "Closed loop",
    0x04: "Open loop (load/decel)",
    0x08: "Open loop (system failure)",
    0x10: "Closed loop (feedback fault)",
}

O2_PIDS = {"0114", "0115", "0116", "0117", "0118", "0119", "011A", "011B"}


def _data_bytes(pid, response):
    # Find the "41 <pid>" reply on any line, skipping echo, SEARCHING..., headers, etc.
    mode = f"{int(pid[:2], 16) + 0x40:02X}"
    pid_byte = pid[2:].upper()
    for line in response.replace("\n", "\r").split("\r"):
        tokens = line.upper().split()
        for i in range(len(tokens) - 1):
            if tokens[i] == mode and tokens[i + 1] == pid_byte:
                try:
                    return [int(t, 16) for t in tokens[i + 2:]]
                except ValueError:
                    return None
    return None


def parse_response(pid, response):
    pid = pid.upper()
    data = _data_bytes(pid, response)
    if not data:
        return None

    if pid == "010C" and len(data) >= 2:
        return ((data[0] * 256) + data[1]) / 4
    elif pid == "010D":
        return round(data[0] * 0.621371)
    elif pid == "0105":
        return data[0] - 40
    elif pid == "0103":
        return FUEL_SYSTEM_STATUS.get(data[0], f"Unknown (0x{data[0]:02X})")
    elif pid == "010A":
        return data[0] * 3
    elif pid == "0110" and len(data) >= 2:
        return ((data[0] * 256) + data[1]) / 100
    elif pid in O2_PIDS:
        return data[0] / 200
    return None
