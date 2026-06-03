import socket
import threading
import time
import sqlite3
import os

from generated import messages_pb2

# =========================
# CONFIGURAÇÕES
# =========================

UDP_PORT = 6000
TCP_PORT = 7000
TOTAL_VAGAS = 100

DB_NAME = "dadosSQL.db"

vagas = {i: False for i in range(1, TOTAL_VAGAS + 1)}

total_entradas = 0
total_saidas = 0

cancela_aberta = True

lock = threading.Lock()

# =========================
# BANCO DE DADOS
# =========================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vagas (
            id INTEGER PRIMARY KEY,
            ocupada INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sistema (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS snapshot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ocupadas INTEGER,
            livres INTEGER,
            cancela TEXT,
            entradas INTEGER,
            saidas INTEGER,
            timestamp INTEGER
        )
    """)

    for i in range(1, TOTAL_VAGAS + 1):
        cur.execute(
            "INSERT OR IGNORE INTO vagas (id, ocupada) VALUES (?, 0)",
            (i,)
        )

    cur.execute(
        "INSERT OR IGNORE INTO sistema (chave, valor) VALUES ('cancela', 'OPEN')"
    )

    conn.commit()
    conn.close()


# =========================
# UPDATE BANCO
# =========================

def update_vaga(vaga_id, estado):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "UPDATE vagas SET ocupada=? WHERE id=?",
        (1 if estado else 0, vaga_id)
    )

    conn.commit()
    conn.close()


def update_cancela(estado):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "UPDATE sistema SET valor=? WHERE chave='cancela'",
        (estado,)
    )

    conn.commit()
    conn.close()


# =========================
# ESTADO
# =========================

def calcular_estado():
    ocupadas = sum(vagas.values())
    return ocupadas, TOTAL_VAGAS - ocupadas


# =========================
# UDP
# =========================

def escutar_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))

    print("[GATEWAY] UDP ativo")

    while True:
        try:
            data, addr = sock.recvfrom(4096)

            msg = messages_pb2.SensorData()
            msg.ParseFromString(data)

            processar_msg(msg)

            ocupadas, livres = calcular_estado()

            print(
                f"[SENSOR {msg.sensor_id}] vaga {msg.vaga_id} "
                f"-> {msg.acao} | OCUP={ocupadas} LIV={livres}"
            )

        except Exception as e:
            print(f"[ERRO UDP] {e}")


# =========================
# PROCESSAMENTO
# =========================

def processar_msg(msg):
    global total_entradas, total_saidas, cancela_aberta

    vaga = msg.vaga_id
    acao = msg.acao

    if vaga < 1 or vaga > TOTAL_VAGAS:
        return

    with lock:
        ocupadas = sum(vagas.values())

        # ENTRADA
        if acao in ["ENTRADA", "entrada", "OCUPADA", "ocupada"]:

            if not cancela_aberta:
                print("[GATEWAY] IGNORADO (cancela fechada)")
                return

            if ocupadas < TOTAL_VAGAS:
                vagas[vaga] = True
                update_vaga(vaga, True)
                total_entradas += 1

        # SAÍDA
        elif acao in ["SAIDA", "saida", "LIVRE", "livre"]:
            if vagas[vaga]:
                vagas[vaga] = False
                update_vaga(vaga, False)
                total_saidas += 1


# =========================
# TCP CLIENTE
# =========================

def handle_client(conn, addr):
    global cancela_aberta

    print(f"[CLIENTE] conectado {addr}")

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            req = messages_pb2.ControlCommand()
            req.ParseFromString(data)

            resp = messages_pb2.ControlCommand(command="REPLY")

            if req.command == "STATUS":
                ocupadas, livres = calcular_estado()
                resp.value = f"OCUP {ocupadas} | LIV {livres}"

            elif req.command == "MAPA":
                with lock:
                    resp.value = "\n".join(
                        f"Vaga {i}: {'OCUPADA' if vagas[i] else 'LIVRE'}"
                        for i in vagas
                    )

            elif req.command == "RESET":
                with lock:
                    for i in vagas:
                        vagas[i] = False
                        update_vaga(i, False)

                resp.value = "RESET OK"

            elif req.command == "ANALISE":
                ocupadas, _ = calcular_estado()
                taxa = (ocupadas / TOTAL_VAGAS) * 100

                resp.value = (
                    f"ENTRADAS: {total_entradas}\n"
                    f"SAIDAS: {total_saidas}\n"
                    f"OCUPACAO: {taxa:.2f}%"
                )

            elif req.command == "LISTAR":
                resp.value = (
                    "P1 - Parking Sensor\n"
                    "fluxo_1 - Traffic Sensor\n"
                    "C1 - Cancela"
                )

            elif req.command == "OPEN":
                cancela_aberta = True
                update_cancela("OPEN")
                resp.value = "CANCELA ABERTA"

            elif req.command == "CLOSE":
                cancela_aberta = False
                update_cancela("CLOSED")
                resp.value = "CANCELA FECHADA"

            else:
                resp.value = "COMANDO INVALIDO"

            conn.send(resp.SerializeToString())

        except Exception as e:
            print(f"[ERRO CLIENTE] {e}")
            break

    conn.close()


# =========================
# SNAPSHOT 1 MIN
# =========================

def salvar_snapshot():
    while True:
        time.sleep(60)

        with lock:
            ocupadas = sum(vagas.values())
            livres = TOTAL_VAGAS - ocupadas
            entradas = total_entradas
            saidas = total_saidas
            cancela = "OPEN" if cancela_aberta else "CLOSED"

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO snapshot (
                ocupadas,
                livres,
                cancela,
                entradas,
                saidas,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ocupadas,
            livres,
            cancela,
            entradas,
            saidas,
            int(time.time())
        ))

        conn.commit()
        conn.close()

        print("[SNAPSHOT] salvo no dadosSQL.db")


# =========================
# TCP SERVER
# =========================

def servidor_tcp():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen(5)

    print("[GATEWAY] TCP ativo")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    print("================================")
    print("   GATEWAY INTELIGENTE")
    print("================================")

    # 🔥 REMOVE BANCO ANTIGO SEMPRE
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print("[GATEWAY] Banco antigo removido")

    init_db()

    threading.Thread(target=servidor_tcp, daemon=True).start()
    threading.Thread(target=escutar_udp, daemon=True).start()
    threading.Thread(target=salvar_snapshot, daemon=True).start()

    while True:
        time.sleep(1)
