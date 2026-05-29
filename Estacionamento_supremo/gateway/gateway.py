import socket
import threading
import time

from generated import messages_pb2


# =========================
# ESTADO DO ESTACIONAMENTO
# =========================

TOTAL_VAGAS = 100
entradas = 0
saidas = 0


def calcular_estado():
    ocupadas = entradas - saidas
    if ocupadas < 0:
        ocupadas = 0

    livres = TOTAL_VAGAS - ocupadas
    if livres < 0:
        livres = 0

    return ocupadas, livres


# =========================
# UDP - RECEBER SENSORES
# =========================

UDP_PORT = 6000


def escutar_udp():
    global entradas, saidas

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))

    print("[GATEWAY] escutando sensores UDP...")

    while True:
        data, addr = sock.recvfrom(4096)

        msg = messages_pb2.SensorData()
        msg.ParseFromString(data)

        print(f"[SENSOR] {msg.sensor_type} -> {msg.value}")

        # Lógica simples baseada no tipo de sensor
        if msg.sensor_type == "traffic_flow":
            entradas += int(msg.value)

        elif msg.sensor_type == "exit_flow":
            saidas += int(msg.value)

        elif msg.sensor_type == "parking":
            pass  # só informativo


# =========================
# TCP - CLIENTE
# =========================

TCP_PORT = 7000


def servidor_tcp():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen(1)

    print("[GATEWAY] aguardando cliente TCP...")

    conn, addr = server.accept()
    print("[GATEWAY] cliente conectado")

    while True:

        data = conn.recv(1024).decode()

        if not data:
            break

        print("[CLIENTE]", data)

        ocupadas, livres = calcular_estado()

        if data == "STATUS":

            resposta = f"""
TOTAL_VAGAS: {TOTAL_VAGAS}
OCUPADAS: {ocupadas}
LIVRES: {livres}
"""

            conn.send(resposta.encode())

        elif data == "OPEN_GATE":
            conn.send(b"Cancela aberta")

        elif data == "CLOSE_GATE":
            conn.send(b"Cancela fechada")

        else:
            conn.send(b"Comando desconhecido")


# =========================
# START GATEWAY
# =========================

if __name__ == "__main__":

    print("[GATEWAY] iniciando...")

    threading.Thread(target=escutar_udp, daemon=True).start()
    threading.Thread(target=servidor_tcp, daemon=True).start()

    while True:
        time.sleep(1)