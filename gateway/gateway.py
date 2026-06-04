import socket
import threading
import time
import sqlite3

from generated import messages_pb2

# =========================
# CONFIGURAÇÕES
# =========================

UDP_PORT = 6000
TCP_PORT = 7000
TOTAL_VAGAS = 100
MULTICAST_GROUP = "224.1.1.1"
MULTICAST_PORT = 5007
sensores_registrados = {}
DB_NAME = "painel/dadosSQL.db"

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
# carrega banco
# =========================

def carregar_memoria():
    global total_entradas, total_saidas, cancela_aberta

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT id, ocupada FROM vagas")

    for linha in cur.fetchall():
        vagas[linha[0]] = bool(linha[1])

    cur.execute("SELECT valor FROM sistema WHERE chave = 'cancela'")
    resultado_cancela = cur.fetchone()
    if resultado_cancela:
        cancela_aberta = (resultado_cancela[0] == "OPEN")
    cur.execute("SELECT entradas, saidas FROM snapshot ORDER BY id DESC LIMIT 1")
    resultado_snap = cur.fetchone()
    if resultado_snap:
        total_entradas = resultado_snap[0]
        total_saidas = resultado_snap[1]

    conn.close()
    print("memoria restaurada!")


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
# realizar descoberta
# =========================

def realizar_descoberta():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(5.0)

    print("Iniciando descoberta de sensores ")
    sock.sendto(b"DISCOVER_SENSORS",(MULTICAST_GROUP, MULTICAST_PORT))

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            msg = messages_pb2.DiscoveryMessage()
            msg.ParseFromString(data)

            with lock:
                sensores_registrados[msg.sensor_id] = {
                    "tipo": msg.sensor_type,
                    "ip": msg.ip if msg.ip != "127.0.0.1" else addr[0],
                    "tcp_port":msg.tcp_port
                }
        except socket.timeout:
            print("fim da janela de descoberta")
            break
        except Exception as e:
            pass
    sock.close()


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

            if not vagas[vaga]:
                ocupadas = sum(vagas.values())
                if ocupadas < TOTAL_VAGAS:
                    vagas[vaga] = True
                    update_vaga(vaga, True)
                    total_entradas +=1
            else:
                return

        # SAÍDA
        elif acao in ["SAIDA", "saida", "LIVRE", "livre"]:
            if vagas[vaga]:
                vagas[vaga] = False
                update_vaga(vaga, False)
                total_saidas += 1
# =========================
# ENVIO TCP PARA SENSORES
# =========================

def enviar_comando_sensor(sensor_id, comando):
    if sensor_id not in sensores_registrados:
        return f"Sensor {sensor_id} não encontrado na rede"

    info = sensores_registrados[sensor_id]

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((info["ip"], info["tcp_port"]))
        cmd_msg = messages_pb2.ControlCommand()
        cmd_msg.command = comando
        s.send(cmd_msg.SerializeToString())
        s.close()

        return "OK"
    except Exception as e:
        return f"ERRO {e}"

# =========================
# TCP CLIENTE
# =========================

def handle_client(conn, addr):
    global cancela_aberta, total_saidas, total_entradas

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
                resp.value = f"OCUPADAS {ocupadas} | LIVRES {livres}"

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
                    total_entradas = 0
                    total_saidas = 0
                conn_db = sqlite3.connect(DB_NAME)
                cur = conn_db.cursor()
                cur.execute("DELETE FROM snapshot")
                conn_db.commit()
                conn_db.close()

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
                with lock:
                    if not sensores_registrados:
                        resp.value = "Nenhum sensor registrado ativo no momento."
                    else:
                        lista = ["=== Sensores Conectados ==="]
                        for s_id, info in sensores_registrados.items():
                            lista.append(
                                f"ID: {s_id} | Tipo: {info['tipo']} | Endereço: {info['ip']}:{info['tcp_port']}")
                        resp.value = "\n".join(lista)

            elif req.command == "OPEN":
                cancela_aberta = True
                update_cancela("OPEN")
                rede = enviar_comando_sensor("C1", "OPEN")
                resp.value = f"CANCELA ABERTA\nRede: {rede}"

            elif req.command == "CLOSE":
                cancela_aberta = False
                update_cancela("CLOSED")
                rede = enviar_comando_sensor("C1", "CLOSE")
                resp.value = f"CANCELA FECHADA\nRede: {rede}"

            elif req.command == "FALHA":
                pass

            else:
                resp.value = "COMANDO INVALIDO"

            conn.send(resp.SerializeToString())

        except Exception as e:
            print(f"[ERRO CLIENTE] {e}")
            break

    conn.close()


# =========================
# SNAPSHOT 20 Se
# =========================

def salvar_snapshot():
    while True:
        time.sleep(2)

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


    init_db()
    carregar_memoria()
    realizar_descoberta()
    threading.Thread(target=servidor_tcp, daemon=True).start()
    threading.Thread(target=escutar_udp, daemon=True).start()
    threading.Thread(target=salvar_snapshot, daemon=True).start()


    while True:
        time.sleep(1)
