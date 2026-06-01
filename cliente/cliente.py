import socket

from generated import messages_pb2
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

def envia_requisicao(client,comando_str):
    requisicao = messages_pb2.ControlCommand()
    requisicao.command = comando_str

    client.send(requisicao.SerializeToString())

    informacao = client.recv(10000)
    if not informacao:
        return "conexao perdida"

    resposta = messages_pb2.ControlCommand()
    resposta.ParseFromString(informacao)

    return resposta.value

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
            print(envia_requisicao(client,"STATUS"))

        elif op == "2":
            print(envia_requisicao(client,"MAPA"))


        elif op == "3":
            print(envia_requisicao(client,"RESET"))

        elif op == "4":
            print(envia_requisicao(client,"OPEN"))


        elif op == "5":
            print(envia_requisicao(client,"CLOSE"))


        else:
            print("comando invalido!")

    client.close()


if __name__ == "__main__":
    main()