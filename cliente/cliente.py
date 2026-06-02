import socket

from generated import messages_pb2
HOST = "127.0.0.1"
PORT = 7000


def menu():
    print("\n===== CLIENTE ANALÍTICO =====")
    print("1 - STATUS do estacionamento")
    print("2 - MAPA de vagas")
    print("3 - Reinicia sistema")
    print("4 - Abre cancela")
    print("5 - Fecha cancela")
    print("6 - Listar sensores conectados")
    print("7 - Relatório analítico")
    print("8 - BOTÃO DE FALHA")
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

        elif op == "6":
            print(envia_requisicao(client,"LISTAR"))

        elif op == "7":
            print(envia_requisicao(client,"ANALISE"))

        elif op == "8":
            print(envia_requisicao(client, "FALHA"))


        else:
            print("comando invalido!")

    client.close()


if __name__ == "__main__":
    main()