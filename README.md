```bash
Sensores_estacionamento/
│
├── sensores/
│   ├── sensor_estaciona.py   # Sensor de vagas do estacionamento
│   ├── sensor_fluxo.py       # Sensor de fluxo de veículos
│   ├── sensor_cancela.py     # Cancela eletrônica (controlável via TCP)
│
├── proto/
├── generated/
├── venv/
└── README.md
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

   5. Cliente teste
   ```bash
   python -m cliente.cliente
   ```
   1 - STATUS
   2 - MAPA
   3 - RESET
   4 - OPEN cancela
   5 - CLOSE cancela

