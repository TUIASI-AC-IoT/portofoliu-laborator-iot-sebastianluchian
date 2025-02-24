import socket
import time

# Completati cu adresa IP a platformei ESP32
PEER_IP = "192.168.89.30"
PEER_PORT = 10001

MESSAGE = b"Salut!"
GPIO_KEY = "GPIO4"
GPIO_VALUE = "0"
GPIO_VALUE_INT = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cnt = 0
while 1:
    try:
        # TO_SEND = MESSAGE + bytes(str(i),"ascii")
        # TO_SEND = GPIO_KEY + "=" + GPIO_VALUE
        gpio_val = "1"
        if cnt % 2:
            gpio_val = "0"
        TO_SEND = str.encode(GPIO_KEY + "=" + gpio_val)
        sock.sendto(TO_SEND, (PEER_IP, PEER_PORT))
        print("Am trimis mesajul: ", TO_SEND)
        time.sleep(1)
        cnt += 1
    except KeyboardInterrupt:
        break