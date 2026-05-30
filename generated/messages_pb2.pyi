from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DiscoveryMessage(_message.Message):
    __slots__ = ("sensor_id", "sensor_type", "ip", "tcp_port", "active")
    SENSOR_ID_FIELD_NUMBER: _ClassVar[int]
    SENSOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    TCP_PORT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    sensor_id: str
    sensor_type: str
    ip: str
    tcp_port: int
    active: bool
    def __init__(self, sensor_id: _Optional[str] = ..., sensor_type: _Optional[str] = ..., ip: _Optional[str] = ..., tcp_port: _Optional[int] = ..., active: bool = ...) -> None: ...

class SensorData(_message.Message):
    __slots__ = ("sensor_id", "sensor_type", "value", "unit", "timestamp", "vaga_id", "acao")
    SENSOR_ID_FIELD_NUMBER: _ClassVar[int]
    SENSOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VAGA_ID_FIELD_NUMBER: _ClassVar[int]
    ACAO_FIELD_NUMBER: _ClassVar[int]
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: int
    vaga_id: int
    acao: str
    def __init__(self, sensor_id: _Optional[str] = ..., sensor_type: _Optional[str] = ..., value: _Optional[float] = ..., unit: _Optional[str] = ..., timestamp: _Optional[int] = ..., vaga_id: _Optional[int] = ..., acao: _Optional[str] = ...) -> None: ...

class ControlCommand(_message.Message):
    __slots__ = ("command", "value")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    command: str
    value: str
    def __init__(self, command: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
