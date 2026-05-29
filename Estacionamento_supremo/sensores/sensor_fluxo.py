import socket
import random
import time
from generated import messages_pb2

UDP_IP = "127.0.0.1"
UDP_PORT = 6000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:

    msg = messages_pb2.SensorData()

    msg.sensor_id = "fluxo_1"
    msg.sensor_type = "parking_flow"

    # vaga_id vai dentro do value
    msg.value = random.randint(1, 100)

    # entrada ou saída vai no unit
    msg.unit = random.choice(["entrada", "saida"])

    msg.timestamp = int(time.time())

    sock.sendto(msg.SerializeToString(), (UDP_IP, UDP_PORT))

    print(f"Enviado: vaga {msg.value} - {msg.unit}")

    time.sleep(2)
