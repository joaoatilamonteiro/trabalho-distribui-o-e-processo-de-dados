import socket
from generated import messages_pb2

HOST = "127.0.0.1"
PORT = 7000


def enviar(client, cmd):
    req = messages_pb2.ControlCommand()
    req.command = cmd

    client.send(req.SerializeToString())

    data = client.recv(10000)

    resp = messages_pb2.ControlCommand()
    resp.ParseFromString(data)

    return resp.value


def menu():
    print("\n--- MENU ---")
    print("1 STATUS")
    print("2 MAPA")
    print("3 RESET")
    print("4 ABRIR CANCELA")
    print("5 FECHAR CANCELA")
    print("6 LISTAR SENSORES")
    print("7 ANALISE")
    print("0 SAIR")


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print("Conectado ao Gateway")

    while True:
        menu()
        op = input("> ")

        if op == "0":
            break

        elif op == "1":
            print(enviar(client, "STATUS"))

        elif op == "2":
            print(enviar(client, "MAPA"))

        elif op == "3":
            print(enviar(client, "RESET"))

        elif op == "4":
            print(enviar(client, "OPEN"))

        elif op == "5":
            print(enviar(client, "CLOSE"))

        elif op == "6":
            print(enviar(client, "LISTAR"))

        elif op == "7":
            print(enviar(client, "ANALISE"))

        else:
            print("Inválido")

    client.close()


if __name__ == "__main__":
    main()
