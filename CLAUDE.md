# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

RobotProject holds the code for a robot controlled over the network. The single
application file, `pirobocode.py`, runs a Flask web server (intended to run on a
Raspberry Pi) that receives directional commands over HTTP and relays them to an
Arduino over a serial connection using the `nanpy` library.

## Running

There is no build system, test suite, or linter configured in this repository.

```bash
pip install nanpy flask   # runtime dependencies (no requirements.txt exists yet)
python pirobocode.py      # starts the Flask server on 0.0.0.0:5000 (debug mode)
```

The server expects an Arduino on the serial device path hard-coded in
`pirobocode.py` (`/dev/USB0`). If the Arduino is not connected it logs a failure
and continues to start.

## Architecture

- **HTTP-to-Arduino bridge:** Flask exposes a single dynamic route, `/<direction>`,
  where `direction` is one of the named compass-style commands
  (`centre`, `up`, `upright`, `right`, `downright`, `down`, `downleft`, `left`,
  `upleft`, `stop`). Each name maps to an integer code 0–9 that represents the
  movement to send to the Arduino. The Arduino firmware (not in this repo)
  interprets these codes to drive the motors.
- **Serial connection** is established once at startup via `nanpy`'s
  `SerialManager` / `ArduinoApi` and held in module-level globals (`connection`,
  `a`) for reuse across requests.

## Notes for future work

- `pirobocode.py` currently does not run as written: `SerialManager` is used but
  never imported (it lives in `nanpy.serialmanager`), the route handler is
  declared `def int comArduino(...)` which is invalid Python, and the handler
  returns an `int` where Flask requires a string/Response. Expect to fix these
  before the server will start.
