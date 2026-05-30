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
    msg.sensor_type = "traffic_flow"

    # vaga afetada
    msg.vaga_id = random.randint(1, 100)

    # ação real do sistema
    msg.acao = random.choice(["ENTRADA", "SAIDA"])

    msg.timestamp = int(time.time())

    sock.sendto(
        msg.SerializeToString(),
        (UDP_IP, UDP_PORT)
    )

    print(f"[FLUXO] vaga {msg.vaga_id} -> {msg.acao}")

    time.sleep(2)
