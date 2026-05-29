import socket
import threading
import time
import random

from generated import messages_pb2

GATEWAY_IP = "127.0.0.1"
GATEWAY_PORT = 6000

CONTROL_PORT = 7001


class Cancela:

    def __init__(self):

        self.sensor_id = "C1"
        self.active = True
        self.interval = 3

        self.state = "CLOSED"  # OPEN / CLOSED


    # =========================
    # UDP (ENVIO DE DADOS)
    # =========================
    def enviar_dados(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while True:

            if self.active:

                carros_passando = random.randint(0, 5)

                msg = messages_pb2.SensorData()
                msg.sensor_id = self.sensor_id
                msg.sensor_type = "gate"
                msg.value = carros_passando
                msg.unit = "cars"
                msg.timestamp = int(time.time())

                sock.sendto(
                    msg.SerializeToString(),
                    (GATEWAY_IP, GATEWAY_PORT)
                )

                print(f"[CANELA] {self.state} -> carros: {carros_passando}")

            time.sleep(self.interval)


    # =========================
    # TCP (CONTROLE)
    # =========================
    def servidor_tcp(self):

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", CONTROL_PORT))
        server.listen(1)

        print("[CANELA] aguardando comandos TCP...")

        conn, addr = server.accept()

        print("[CANELA] gateway conectado")

        while True:

            data = conn.recv(1024).decode()

            if not data:
                break

            print("[COMANDO RECEBIDO]:", data)

            if data == "OPEN":
                self.state = "OPEN"
                print("[CANELA] ABERTA")

            elif data == "CLOSE":
                self.state = "CLOSED"
                print("[CANELA] FECHADA")

            elif data == "TURN_OFF":
                self.active = False

            elif data == "TURN_ON":
                self.active = True

            elif data.startswith("SET_INTERVAL"):
                _, value = data.split()
                self.interval = int(value)

            elif data == "RESET":
                self.state = "CLOSED"
                self.active = True
                self.interval = 3


    # =========================
    # START
    # =========================
    def start(self):

        threading.Thread(target=self.enviar_dados, daemon=True).start()
        threading.Thread(target=self.servidor_tcp, daemon=True).start()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    Cancela().start()