import socket
import threading
import time
from generated import messages_pb2


# CONFIGURAÇÕES


UDP_PORT = 6000
TCP_PORT = 7000
MULTICAST_GROUP = "224.1.1.1"
MULTICAST_PORT = 5007

TOTAL_VAGAS = 100

vagas = {i: False for i in range(1, TOTAL_VAGAS + 1)}
sensores_registrados = {}
lock = threading.Lock()


# DESCOBERTA MULTICAST


def realizar_descoberta():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(5.0)

    print("[GATEWAY] Iniciando descoberta de sensores (Multicast)...")
    sock.sendto(b"DISCOVER_SENSORS", (MULTICAST_GROUP, MULTICAST_PORT))

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            msg = messages_pb2.DiscoveryMessage()
            msg.ParseFromString(data)
            
            with lock:
                sensores_registrados[msg.sensor_id] = {
                    "tipo": msg.sensor_type,
                    "ip": msg.ip if msg.ip != "127.0.0.1" else addr[0],
                    "tcp_port": msg.tcp_port
                }
            print(f"[DESCOBERTA] Sensor {msg.sensor_id} ({msg.sensor_type}) registrado!")
        except socket.timeout:
            print("[GATEWAY] Fim da janela de descoberta.")
            break
        except Exception as e:
            pass
            
    sock.close()


# PROCESSAR EVENTOS UDP


def calcular_estado():
    with lock:
        ocupadas = sum(vagas.values())
        livres = TOTAL_VAGAS - ocupadas
    return ocupadas, livres

def processar_msg(msg):
    
    vaga = msg.vaga_id
    acao = msg.acao

    if vaga < 1 or vaga > TOTAL_VAGAS:
        return

    with lock:
        if acao in ["entrada", "ocupada", "OCUPADA", "ENTRADA"]:
            vagas[vaga] = True
        elif acao in ["saida", "livre", "LIVRE", "SAIDA"]:
            vagas[vaga] = False

def escutar_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))

    print("[GATEWAY] Escutando UDP (Telemetria)...")

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            msg = messages_pb2.SensorData()
            msg.ParseFromString(data)

            processar_msg(msg)
            ocupadas, livres = calcular_estado()

            print(f"[SENSOR {msg.sensor_id}] Vaga {msg.vaga_id} -> {msg.acao} | Ocupadas={ocupadas} Livres={livres}")
        except Exception as e:
            print(f"[ERRO UDP] {e}")


# ENVIAR COMANDO TCP PARA SENSOR


def enviar_comando_sensor(sensor_id, comando_str):
    """Encaminha um comando para um sensor específico."""
    with lock:
        if sensor_id not in sensores_registrados:
            return f"ERRO: Sensor {sensor_id} nao encontrado na rede."
        info = sensores_registrados[sensor_id]
    
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((info["ip"], info["tcp_port"]))
        
        
        cmd = messages_pb2.ControlCommand(command=comando_str)
        client.send(cmd.SerializeToString())
        client.close()
        
        return f"Sucesso: '{comando_str}' enviado para {sensor_id}"
    except Exception as e:
        return f"Falha ao conectar com {sensor_id}: {e}"


# TCP - CLIENTE


def handle_client(conn, addr):
    print(f"[CLIENTE] {addr} conectado")

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            
            req = messages_pb2.ControlCommand()
            req.ParseFromString(data)
            
            
            resp = messages_pb2.ControlCommand(command="REPLY")

            if req.command == "STATUS":
                ocupadas, livres = calcular_estado()
                resp.value = f"TOTAL: {TOTAL_VAGAS} | OCUPADAS: {ocupadas} | LIVRES: {livres}"
                
            elif req.command == "MAPA":
                mapa = []
                with lock:
                    for i in range(1, TOTAL_VAGAS + 1):
                        estado = "OCUPADA" if vagas[i] else "LIVRE"
                        mapa.append(f"Vaga {i:03d}: {estado}")
                resp.value = "\n".join(mapa)

            elif req.command == "RESET":
                with lock:
                    for i in vagas: vagas[i] = False
                resp.value = "Sistema Resetado!"

            elif req.command in ["OPEN", "CLOSE"]:
                
                resultado = enviar_comando_sensor("C1", req.command)
                resp.value = resultado

            else:
                resp.value = "COMANDO INVALIDO"

            conn.send(resp.SerializeToString())

        except Exception as e:
            print(f"[ERRO CLIENTE] {e}")
            break

    conn.close()
    print(f"[CLIENTE] {addr} desconectado")


def servidor_tcp():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen(5)

    print("[GATEWAY] TCP pronto para Clientes...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


# MAIN


if __name__ == "__main__":
    print("====================================")
    print("   GATEWAY INTELIGENTE INICIADO")
    print("====================================")

    realizar_descoberta()

    threading.Thread(target=escutar_udp, daemon=True).start()
    threading.Thread(target=servidor_tcp, daemon=True).start()

    while True:
        time.sleep(1)
