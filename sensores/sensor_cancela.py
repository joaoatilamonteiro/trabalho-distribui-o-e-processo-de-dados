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

            # só gera eventos quando aberta
            if self.active and self.state == "OPEN":

                msg = messages_pb2.SensorData()

                msg.sensor_id = self.sensor_id
                msg.sensor_type = "gate"

                msg.vaga_id = random.randint(1, 100)

                msg.acao = "ENTRADA"

                msg.timestamp = int(time.time())

                sock.sendto(
                    msg.SerializeToString(),
                    (GATEWAY_IP, GATEWAY_PORT)
                )

                print(
                    f"[CANCELA] carro entrou na vaga {msg.vaga_id}"
                )

            time.sleep(self.interval)


    # =========================
    # TCP (CONTROLE COM PROTOBUF)
    # =========================
    def servidor_tcp(self):

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", CONTROL_PORT))
        server.listen(1)

        print("[CANCELA] aguardando comandos TCP...")

        conn, addr = server.accept()

        print("[CANCELA] gateway conectado")

        while True:

            data = conn.recv(1024)

            if not data:
                break

            cmd = messages_pb2.ControlCommand()
            cmd.ParseFromString(data)

            print(f"[COMANDO] {cmd.command}")

            if cmd.command == "OPEN":
                self.state = "OPEN"
                print("[CANCELA] ABERTA")

            elif cmd.command == "CLOSE":
                self.state = "CLOSED"
                print("[CANCELA] FECHADA")

            elif cmd.command == "TURN_OFF":
                self.active = False

            elif cmd.command == "TURN_ON":
                self.active = True

            elif cmd.command == "SET_INTERVAL":
                self.interval = int(cmd.value)

            elif cmd.command == "RESET":
                self.state = "CLOSED"
                self.active = True
                self.interval = 3


    # =========================
    # START
    # =========================
    def start(self):

        threading.Thread(
            target=self.enviar_dados,
            daemon=True
        ).start()

        threading.Thread(
            target=self.servidor_tcp,
            daemon=True
        ).start()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    Cancela().start()
