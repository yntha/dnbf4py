from collections.abc import Generator
from enum import IntEnum
from pathlib import Path
from typing import Self

from datastream import DeserializingStream, SerializingStream

from dnbf4py.format.types import Record, RecordTypeEnum, RecordTypes


class DNBinaryFormat:
    def __init__(self, stream: DeserializingStream):
        self.stream = stream
        self.header_record = None
        self.parsers = [
            self.read_serialized_stream_header,
        ]

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(DeserializingStream(data))

    @classmethod
    def from_file(cls, path: str | Path):
        path = Path(path)

        return cls(DeserializingStream(path.read_bytes()))

    def read_record(self) -> Generator[Record, None, None]:
        while True:
            record_type = RecordTypeEnum(self.stream.read_uint8())

            yield self.parsers[record_type]()

    def read(self):
        record = next(self.read_record())

        if record.type != RecordTypeEnum.SerializedStreamHeader:
            msg = "Expected SerializedStreamHeader record"

            raise ValueError(msg)

        self.header_record = record
