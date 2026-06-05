
```markdown
# Sistema Distribuído: Estacionamento Inteligente (Smart Parking)

Este projeto simula o ambiente de uma Cidade Inteligente (Smart City) com foco na gestão de um estacionamento distribuído. A aplicação foi desenvolvida para demonstrar conceitos de Sistemas Distribuídos, como comunicação via Sockets (TCP/UDP), serialização com Protocol Buffers, descoberta dinâmica de nós (Multicast), persistência em banco de dados SQLite e tolerância a falhas.

## 🗂️ Estrutura do Projeto

```text
trabalho-distribui-o-e-processo-de-dados/
├── cliente/
│   └── cliente.py             # Cliente Analítico (Interface de controle via TCP)
├── gateway/
│   └── gateway.py             # Gerente Central (Gerencia TCP, UDP Multicast/Unicast e Banco SQLite)
├── generated/
│   ├── messages.proto         # Contrato oficial de mensagens (Protocol Buffers)
│   ├── messages_pb2.py        # Código Python gerado automaticamente
│   └── messages_pb2.pyi       # Arquivo de tipagem (ajuda o VS Code no autocompletar)
├── painel/
│   ├── index.php              # Dashboard visual interativo do estacionamento
│   └── dadosSQL.db            # Banco de dados SQLite persistente (Gerado automaticamente)
├── sensores/
│   ├── sensor_cancela.py      # Fonte Controlável (Recebe TCP, gera tráfego UDP e simula falha)
│   ├── sensor_estaciona.py    # Fonte Contínua c/ Descoberta (Multicast e tráfego UDP)
│   └── sensor_fluxo.py        # Fonte Contínua Simples (Gera tráfego UDP de entrada/saída)
├── iniciar.bat                # Orquestrador automatizado para inicialização dos nós
├── .gitignore                 # Arquivos ignorados pelo Git (.venv, *.db, __pycache__)
└── README.md                  # Documentação do projeto

```

##Como Preparar o Ambiente

1. **Criar o ambiente virtual:**
```bash
python -m venv .venv

```


2. **Ativar o ambiente virtual:**
```bash
# No Windows:
.venv\Scripts\activate

# No Linux/Mac:
source .venv/bin/activate

```


3. **Instalar dependências:**
```bash
pip install protobuf grpcio-tools

```



## Como Executar o Sistema

A arquitetura foi otimizada para rodar de forma orquestrada e simplificada.

### 1. Inicializando o Backend (Servidor e Sensores)

Não é mais necessário abrir os terminais um por um.

* Dê um **duplo clique** no arquivo `iniciar.bat` na raiz do projeto.
* Ele iniciará os sensores, aguardará a prontidão da rede e, em seguida, iniciará o Gateway (ativando o Multicast) e o terminal do Cliente Analítico automaticamente.

### 2. Inicializando o Frontend (Dashboard e Banco de Dados)

O painel foi configurado para não depender de ferramentas externas pesadas (como o XAMPP).

1. Abra um terminal na raiz do projeto.
2. Navegue até a pasta do painel:
```bash
cd painel

```


3. Inicie o servidor embutido do PHP:
```bash
php -S localhost:8080

```


4. Acesse o painel pelo navegador no endereço: `http://localhost:8080`

## Comandos do Cliente Analítico

No terminal do Cliente Analítico, você pode interagir com todo o sistema utilizando o menu:

* `1 - STATUS` : Retorna a contagem em tempo real de vagas ocupadas e livres.
* `2 - MAPA` : Lista o status físico individual de cada uma das 100 vagas.
* `3 - RESET` : Formata o banco de dados, zera os contadores de fluxo e reinicia o sistema do zero.
* `4 - ABRIR CANCELA` : Envia um comando de controle TCP para a cancela física.
* `5 - FECHAR CANCELA` : Envia um comando de controle TCP para fechar a cancela.
* `6 - LISTAR SENSORES` : Lista todos os dispositivos que responderam à descoberta via Multicast.
* `7 - ANALISE` : Mostra as estatísticas agregadas (Entradas, Saídas e % de Ocupação).
* `8 - FALHA` : Simula a queda de um nó. Envia um comando de "CRASH" para o sensor da Cancela, demonstrando a tolerância a falhas do Gateway que isola o componente indisponível.
* `0 - SAIR` : Encerra a interface do cliente.

```

```