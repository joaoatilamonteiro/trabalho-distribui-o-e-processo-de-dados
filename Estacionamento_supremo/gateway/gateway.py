import socket
import threading
import time
from generated import messages_pb2

# =========================
# ESTADO GLOBAL
# =========================

TOTAL_VAGAS = 100
entradas = 0
saidas = 0

lock = threading.Lock()


# =========================
# FUNÇÃO ESTADO
# =========================

def calcular_estado():
    ocupadas = entradas - saidas

    if ocupadas < 0:
        ocupadas = 0

    if ocupadas > TOTAL_VAGAS:
        ocupadas = TOTAL_VAGAS

    livres = TOTAL_VAGAS - ocupadas

    return ocupadas, livres


# =========================
# UDP - SENSORES
# =========================

UDP_PORT = 6000


def escutar_udp():
    global entradas, saidas

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))

    print("[GATEWAY] UDP escutando...")

    while True:
        data, addr = sock.recvfrom(4096)

        msg = messages_pb2.SensorData()
        msg.ParseFromString(data)

        print(f"[SENSOR] {msg.sensor_type} | value={msg.value}")

        with lock:
            if msg.sensor_type == "traffic_flow":
                entradas += int(msg.value)

            elif msg.sensor_type == "exit_flow":
                saidas += int(msg.value)

        ocupadas, livres = calcular_estado()
        print(f"[ESTADO] Ocupadas={ocupadas} | Livres={livres}")


# =========================
# TCP - CLIENTE (MULTI CONEXÃO)
# =========================

TCP_PORT = 7000


def handle_client(conn, addr):
    print(f"[CLIENTE CONECTADO] {addr}")

    while True:
        try:
            data = conn.recv(1024).decode().strip()

            if not data:
                break

            print(f"[CLIENTE] {data}")

            ocupadas, livres = calcular_estado()

            if data == "STATUS":
                resposta = f"""
====================
TOTAL: {TOTAL_VAGAS}
OCUPADAS: {ocupadas}
LIVRES: {livres}
====================
"""
                conn.send(resposta.encode())

            elif data == "RESET":
                global entradas, saidas
                with lock:
                    entradas = 0
                    saidas = 0
                conn.send(b"RESET OK")

            else:
                conn.send(b"COMANDO INVALIDO")

        except:
            break

    conn.close()
    print("[CLIENTE DESCONECTADO]")


def servidor_tcp():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen(5)

    print("[GATEWAY] TCP pronto...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


# =========================
# DEBUG LOOP (IMPORTANTE)
# =========================

def debug_estado():
    while True:
        time.sleep(5)
        ocupadas, livres = calcular_estado()
        print(f"[DEBUG] OCUPADAS={ocupadas} LIVRES={livres}")


# =========================
# START
# =========================

if __name__ == "__main__":
    print("[GATEWAY] iniciando sistema...")

    threading.Thread(target=escutar_udp, daemon=True).start()
    threading.Thread(target=servidor_tcp, daemon=True).start()
    threading.Thread(target=debug_estado, daemon=True).start()

    while True:
        time.sleep(1)
