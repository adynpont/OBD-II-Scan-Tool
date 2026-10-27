# OBD-II Scan Project

A simple OBD-II scanner for Linux. It talks to a USB ELM327 adapter and has a small Tkinter GUI. It can read trouble codes (DTCs) and show live sensor data from your vehicle.

The serial connection is handled in C (`libelm327.so`). The OBD logic and GUI are written in Python and call into the C library through `ctypes`.

## Features

- Auto-detects an ELM327 adapter on `/dev/ttyUSB*` or `/dev/ttyACM*`
- Reads diagnostic trouble codes (Mode 03), for example `P0301`
- Live sensor readings, refreshed once per second:

| Sensor | PID | Units |
|---|---|---|
| Engine RPM | `010C` | rpm |
| Vehicle speed | `010D` | mph |
| Coolant temperature | `0105` | °C (red at 100 °C and above) |
| Fuel system status | `0103` | text, e.g. "Closed loop" |
| Fuel pressure | `010A` | kPa |
| MAF airflow rate | `0110` | g/s |
| O2 sensors 1–8 | `0114`–`011B` | volts |

A sensor shows `--` when the vehicle doesn't report it. This is normal. Many cars don't support fuel pressure (`010A`), and most have only 2–4 O2 sensors.

## Requirements

- Linux
- A USB ELM327 OBD-II adapter (Bluetooth adapters aren't supported yet)
- Python 3 with Tkinter (`sudo apt install python3-tk` on Debian/Ubuntu)
- `gcc` to build the C library

## Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/adynpont/OBD-II-Scan-Project.git
   cd OBD-II-Scan-Project
   ```

2. **Build the C library.** The `.so` isn't committed, so you need to build it once:

   ```bash
   gcc -shared -fPIC -o myobd/src/Python/libelm327.so myobd/src/C/Elm327_Connection.c
   ```

3. **Give your user access to the serial port** (only needed once, then log out and back in):

   ```bash
   sudo usermod -aG dialout $USER
   ```

## Usage

1. Plug the ELM327 into your car's OBD-II port and into your computer.
2. Turn the ignition on, or start the engine for live data.
3. Start the GUI:

   ```bash
   cd myobd/src/Python
   python3 gui.py
   ```

- **Scan for Codes** reads stored trouble codes.
- **Sensor Data** opens the live sensor view. **Back** returns to the main menu and stops the updates.

### Using it from Python

```python
from myobd import OBD

car = OBD()
print(car.get_rpm())
print(car.get_coolant_temp())
print(car.get_dtc())    # e.g. ['P0301']
car.clear_dtc()         # clears codes and turns off the check engine light
```

Run this from inside `myobd/src/Python`.

## Project structure

```
myobd/src/
├── C/
│   └── Elm327_Connection.c   # Serial port setup, ELM327 auto-detect, send/receive
└── Python/
    ├── elm327.py             # ctypes wrapper around libelm327.so, adapter init
    ├── myobd.py              # OBD class: sensor queries and DTC decoding
    ├── parser.py             # Decodes Mode 01 PID responses into values
    └── gui.py                # Tkinter GUI
```

## How it works

1. `Elm327_Connection.c` scans `/dev` for USB serial devices. It sends `ATZ` to each one at 38400 baud until one replies with `ELM327`.
2. `elm327.py` sets up the adapter: echo off, headers off, spaces on, automatic protocol.
3. Each query sends a PID (for example `0105`) and reads until the ELM327's `>` prompt.
4. `parser.py` finds the `41 <PID>` reply in the response and converts the data bytes using the standard SAE J1979 formulas.

## Troubleshooting

- **"No ELM327 device found":** check that the adapter shows up with `ls /dev/ttyUSB* /dev/ttyACM*`, and that you're in the `dialout` group.
- **All sensors show `--`:** make sure the ignition is on. Some clone adapters take a few seconds to find the vehicle's protocol on the first query.
- **`OSError` loading `libelm327.so`:** you haven't built the library yet. See Setup step 2.

## Disclaimer

Clearing codes also resets your car's emissions readiness monitors. Don't clear codes right before an emissions inspection. Use at your own risk.
