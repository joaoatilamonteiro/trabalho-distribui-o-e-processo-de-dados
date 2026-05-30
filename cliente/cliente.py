import socket

HOST = "127.0.0.1"
PORT = 7000


def menu():
    print("\n===== CLIENTE ANALÍTICO =====")
    print("1 - STATUS do estacionamento")
    print("2 - MAPA de vagas")
    print("3 - RESET sistema")
    print("4 - OPEN cancela")
    print("5 - CLOSE cancela")
    print("0 - sair")


def main():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print("Conectado ao gateway!")

    while True:

        menu()
        op = input("Escolha: ")

        if op == "0":
            break

        elif op == "1":
            client.send(b"STATUS")
            print(client.recv(4096).decode())

        elif op == "2":
            client.send(b"MAPA")
            print(client.recv(10000).decode())

        elif op == "3":
            client.send(b"RESET")
            print(client.recv(4096).decode())

        elif op == "4":
            client.send(b"OPEN")
            print("Cancela aberta")

        elif op == "5":
            client.send(b"CLOSE")
            print("Cancela fechada")

        else:
            print("Comando inválido")

    client.close()


if __name__ == "__main__":
    main()