import io
from flask import Flask, send_file
import re
import os.path
import socket
import time


# Completati cu adresa IP a platformei ESP32
PEER_IP = "192.168.89.20"
PEER_PORT = 10001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

app = Flask(__name__)

@app.route('/firmware.bin')
def firm():
    with open(".pio\\build\\esp-wrover-kit\\firmware.bin", 'rb') as bites:
        print(bites)
        return send_file(
                     io.BytesIO(bites.read()),
                     mimetype='application/octet-stream'
               )

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/version")
def get_version():
    with open("include\\version.h", "r") as file:
        build_number_match = re.search(r'#define BUILD_NUMBER "(\d+)"', file.read())
        build_number = build_number_match.group(1) if build_number_match else None
        print(build_number)
    # try:
    #     to_send = str.encode(build_number)
    #     sock.sendto(to_send, (PEER_IP, PEER_PORT))
    #     print("Am trimis mesajul: ", to_send)
    # except:
    #     raise Exception
    return str.encode(build_number)

if __name__ == '__main__':
    app.run(host='0.0.0.0', ssl_context=('ca_cert.pem', 'ca_key.pem'), debug=True)