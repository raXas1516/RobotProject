from nanpy import ArduinoApi  # imports nanpy
from nanpy.serialmanager import SerialManager  # serial connection helper for nanpy
from flask import Flask, abort  # imports flask

app = Flask(__name__)

# Map each named direction to the integer code understood by the Arduino.
DIRECTIONS = {
    'centre': 0,
    'up': 1,
    'upright': 2,
    'right': 3,
    'downright': 4,
    'down': 5,
    'downleft': 6,
    'left': 7,
    'upleft': 8,
    'stop': 9,
}

try:  # attempts to connect to Arduino
    connection = SerialManager(device='/dev/USB0')  # stores the address of the arduino
    a = ArduinoApi(connection=connection)
except Exception:
    connection = None
    a = None
    print('Failed to connect with Arduino')


@app.route('/<direction>')
def com_arduino(direction):
    if direction not in DIRECTIONS:
        abort(404)  # unknown direction
    dir_num = DIRECTIONS[direction]
    # TODO: forward dir_num to the Arduino once the firmware protocol is defined.
    return str(dir_num)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
