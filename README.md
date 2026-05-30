```bash
trabalho-distribui-o-e-processo-de-dados/
├── cliente/
│   └── cliente.py             # Cliente Analítico (Interface de controle e consultas)
├── gateway/
│   └── gateway.py             # Gerente Central do sistema (Gerencia TCP e escuta UDP)
├── generated/
│   ├── messages.proto         # Contrato oficial de mensagens (Protocol Buffers)
│   ├── messages_pb2.py        # Código Python gerado automaticamente
│   └── messages_pb2.pyi       # Arquivo de tipagem (ajuda o VS Code no autocompletar)
├── sensores/
│   ├── sensor_cancela.py      # Fonte Controlável (Comandos TCP e tráfego UDP)
│   ├── sensor_estaciona.py    # Fonte Contínua c/ Descoberta (Multicast e UDP)
│   └── sensor_fluxo.py        # Fonte Contínua Simples (Apenas tráfego UDP)
├── .gitignore                 # Arquivos ignorados pelo Git (.venv, __pycache__)
└── README.md                  # Documentação do projeto

```


Como testar os sensores:


1. Criar ambiente virtual
   ```bash
   python -m venv venv
   ```

2. Ativar ambiente virtual
   ```bash
   venv\Scripts\activate
   ```
3. Instalar dependências
   ```bash
   pip install protobuf grpcio-tools
   ```
4. Executar o Gateway
   ```bash
   python -m gateway.gateway
   ```

5. Execução dos Sensores(Em outros terminais)
   ```bash
   python -m sensores.sensor_estaciona
   ```
   
   ```bash
   python -m sensores.sensor_fluxo
   ```
   
   ```bash
   python -m sensores.sensor_cancela
   ```

6. Cliente teste
   ```bash
   python -m cliente.cliente
   ```
   1 - STATUS
   2 - MAPA
   3 - RESET
   4 - OPEN cancela
   5 - CLOSE cancela

