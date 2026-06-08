# Sistema Distribuído: Estacionamento Inteligente 
# Arquitetura do Projeto

```markdown

# Este projeto simula o ambiente de uma Cidade Inteligente (Smart City) com foco na gestão de um estacionamento distribuído. A aplicação foi desenvolvida para demonstrar conceitos de Sistemas Distribuídos, como comunicação via Sockets (TCP/UDP), serialização com Protocol Buffers, descoberta dinâmica de nós (Multicast), persistência em banco de dados SQLite e tolerância a falhas.

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

---

## Como Executar o Sistema (Modo Automático)

A arquitetura foi otimizada para ser **totalmente portátil e orquestrada**. Não é necessário instalar bibliotecas manualmente ou configurar servidores web externos como o XAMPP ou Docker.

**Pré-requisito único:** Ter o Python instalado na máquina alvo.

1. **Início Rápido:** Dê um **duplo clique** no arquivo `iniciar.bat` localizado na raiz do projeto.
2. **O que o orquestrador faz de forma autônoma:**
* Cria o ambiente virtual (`.venv`) e instala as dependências (`protobuf`, `grpcio-tools`).
* Faz o download de um servidor PHP Portátil para uso local.
* Inicia os três sensores e aguarda a prontidão da rede.
* Inicia o Gateway (ativando o SQLite e as escutas TCP/UDP/Multicast).
* Abre o terminal do Cliente Analítico para controle do sistema.
* Sobe o Painel Web com a extensão do banco de dados ativada. 


3. **Acesso ao Dashboard:** O painel visual estará disponível no navegador através do endereço: `http://localhost:8080`

---

## Comandos do Cliente Analítico

No terminal do Cliente Analítico, você pode interagir com toda a rede utilizando o menu numérico:

* **1 - STATUS** : Retorna a contagem em tempo real de vagas ocupadas e livres.
* **2 - MAPA** : Lista o status físico individual de cada uma das 100 vagas.
* **3 - RESET** : Formata o banco de dados, zera os contadores de fluxo e reinicia o sistema do zero.
* **4 - ABRIR CANCELA** : Envia um comando de controle TCP para a cancela física.
* **5 - FECHAR CANCELA** : Envia um comando de controle TCP para fechar a cancela.
* **6 - LISTAR SENSORES** : Lista todos os dispositivos que responderam à descoberta via Multicast.
* **7 - ANALISE** : Mostra as estatísticas agregadas (Entradas, Saídas e % de Ocupação).
* **8 - FALHA** : Simula a queda crítica de um nó. Envia um comando de "CRASH" para o sensor da Cancela, demonstrando a tolerância a falhas do Gateway, que isola o componente indisponível sem derrubar a rede.
* **0 - SAIR** : Encerra a interface do cliente e desconecta o TCP.

