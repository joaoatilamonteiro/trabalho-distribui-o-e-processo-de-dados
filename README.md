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
4. Execução dos Sensores
   ```bash
   python -m sensores.sensor_estaciona
   ```
   
   ```bash
   python -m sensores.sensor_fluxo
   ```
   
   ```bash
   python -m sensores.sensor_cancela
   ```
   
