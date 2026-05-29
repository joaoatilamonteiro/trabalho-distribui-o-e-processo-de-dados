import socket
import struct
import threading
import time
import random

from generated import messages_pb2


# =========================
# CONFIGURAÇÕES
# =========================

GATEWAY_IP = "127.0.0.1"
GATEWAY_PORT = 6000

MULTICAST_GROUP = "224.1.1.1"
MULTICAST_PORT = 5007

sensor_id = "P1"


# =========================
# ENVIO DE DADOS (UDP)
# =========================

def enviar_dados():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:

        msg = messages_pb2.SensorData()

        msg.sensor_id = sensor_id
        msg.sensor_type = "parking"

        # vaga aleatória
        msg.vaga_id = random.randint(1, 100)

        # estado da vaga
        msg.acao = random.choice([
            "OCUPADA",
            "LIVRE"
        ])

        msg.timestamp = int(time.time())

        sock.sendto(
            msg.SerializeToString(),
            (GATEWAY_IP, GATEWAY_PORT)
        )

        print(
            f"[{sensor_id}] vaga {msg.vaga_id} -> {msg.acao}"
        )

        time.sleep(3)


# =========================
# DESCOBERTA (MULTICAST)
# =========================

def escutar_multicast():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", MULTICAST_PORT))

    mreq = struct.pack(
        "4sL",
        socket.inet_aton(MULTICAST_GROUP),
        socket.INADDR_ANY
    )

    sock.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        mreq
    )

    print(f"[{sensor_id}] escutando multicast...")

    while True:

        data, addr = sock.recvfrom(1024)

        if data.decode(errors="ignore") == "DISCOVER_SENSORS":

            msg = messages_pb2.DiscoveryMessage()

            msg.sensor_id = sensor_id
            msg.sensor_type = "parking"
            msg.ip = "127.0.0.1"
            msg.tcp_port = 7000
            msg.active = True

            sock.sendto(
                msg.SerializeToString(),
                addr
            )

            print(f"[{sensor_id}] respondeu descoberta")


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    print("Sensor de estacionamento iniciado...")

    threading.Thread(
        target=escutar_multicast,
        daemon=True
    ).start()

    threading.Thread(
        target=enviar_dados,
        daemon=True
    ).start()

    while True:
        time.sleep(1)
