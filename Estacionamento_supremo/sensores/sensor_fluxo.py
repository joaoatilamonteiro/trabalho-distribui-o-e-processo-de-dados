import socket
import time
import random

from generated import messages_pb2


GATEWAY_IP = "127.0.0.1"
GATEWAY_PORT = 6000

sensor_id = "F1"


def main():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("[FLUXO] sensor iniciado...")

    while True:

        fluxo = random.randint(0, 30)  # carros por ciclo

        msg = messages_pb2.SensorData()
        msg.sensor_id = sensor_id
        msg.sensor_type = "traffic_flow"
        msg.value = fluxo
        msg.unit = "cars/min"
        msg.timestamp = int(time.time())

        sock.sendto(
            msg.SerializeToString(),
            (GATEWAY_IP, GATEWAY_PORT)
        )

        print(f"[FLUXO] carros/min: {fluxo}")

        time.sleep(3)


if __name__ == "__main__":
    main()