from nanpy import ArduinoApi #imports nanpy
from time import sleep #imports sleep
from flask import Flask #imports flask

app = Flask(__name__)

try: #attempts to connect to Arduino
    connection = SerialManager(device='/dev/USB0') #stores the address of the arduino in connection
    a = ArduinoApi(connection=connection)
except:
    print('Failed to connect with Arduino')
direction = ['']

@app.route('/<direction>')
def int comArduino(direction):
    if (direction == 'centre'):
        dirNum=0
    elif (direction == 'up'):
        dirNum=1
    elif (direction == 'upright'):
        dirNum=2
    elif (direction == 'right'):
        dirNum=3
    elif (direction == 'downright'):
        dirNum=4
    elif (direction == 'down'):
        dirNum=5
    elif (direction == 'downleft'):
        dirNum=6
    elif (direction == 'left'):
        dirNum=7
    elif (direction == 'upleft'):
        dirNum=8
    elif (direction == 'stop'):
        dirNum=9
    return dirNum

if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0')
