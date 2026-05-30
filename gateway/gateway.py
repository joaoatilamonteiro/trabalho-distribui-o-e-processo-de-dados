import socket
import threading
import time
from generated import messages_pb2

# =========================
# CONFIGURAÇÕES
# =========================

UDP_PORT = 6000
TOTAL_VAGAS = 100

# vaga_id -> True (ocupada) / False (livre)
vagas = {i: False for i in range(1, TOTAL_VAGAS + 1)}

lock = threading.Lock()


# =========================
# CALCULAR ESTADO
# =========================

def calcular_estado():

    ocupadas = sum(vagas.values())
    livres = TOTAL_VAGAS - ocupadas

    return ocupadas, livres


# =========================
# PROCESSAR EVENTOS
# =========================

def processar_msg(msg):

    vaga = msg.vaga_id
    acao = msg.acao

    if vaga < 1 or vaga > TOTAL_VAGAS:
        return

    with lock:

        if acao in ["ENTRADA", "OCUPADA"]:

            vagas[vaga] = True

        elif acao in ["SAIDA", "LIVRE"]:

            vagas[vaga] = False


# =========================
# UDP - SENSORES
# =========================

def escutar_udp():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))

    print("[GATEWAY] escutando UDP...")

    while True:

        data, addr = sock.recvfrom(4096)

        msg = messages_pb2.SensorData()
        msg.ParseFromString(data)

        processar_msg(msg)

        ocupadas, livres = calcular_estado()

        print(
            f"[SENSOR] {msg.sensor_type} | "
            f"Vaga {msg.vaga_id} -> {msg.acao} | "
            f"Ocupadas={ocupadas} Livres={livres}"
        )


# =========================
# TCP - CLIENTE
# =========================

TCP_PORT = 7000


def handle_client(conn, addr):

    print(f"[CLIENTE] {addr} conectado")

    while True:

        try:

            data = conn.recv(1024).decode().strip()

            if not data:
                break

            ocupadas, livres = calcular_estado()

            if data == "STATUS":

                resposta = f"""
========================
TOTAL: {TOTAL_VAGAS}
OCUPADAS: {ocupadas}
LIVRES: {livres}
========================
"""

                conn.send(resposta.encode())

            elif data == "MAPA":

                mapa = ""

                for i in range(1, TOTAL_VAGAS + 1):

                    estado = "OCUPADA" if vagas[i] else "LIVRE"
                    mapa += f"Vaga {i:03d}: {estado}\n"

                conn.send(mapa.encode())

            elif data == "RESET":

                with lock:
                    for i in vagas:
                        vagas[i] = False

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

        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()


# =========================
# DEBUG
# =========================

def debug():

    while True:

        time.sleep(5)

        ocupadas, livres = calcular_estado()

        print(f"[DEBUG] OCUPADAS={ocupadas} LIVRES={livres}")


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    print("[GATEWAY] iniciado")

    threading.Thread(target=escutar_udp, daemon=True).start()
    threading.Thread(target=servidor_tcp, daemon=True).start()
    threading.Thread(target=debug, daemon=True).start()

    while True:
        time.sleep(1)
