def parse_response(pid, response):
    parts = response.replace("\r", " ").replace("\n", " ").split()
    if "NO" in response.upper() or len(parts) < 3:
        return None
    if pid == "010C":
        A, B = int(parts[-2], 16), int(parts[-1], 16)
        return ((A * 256) + B) / 4
    elif pid == "010D":
        return int(parts[-1], 16)
    elif pid == "0105":
        return int(parts[-1], 16) - 40
    return None
