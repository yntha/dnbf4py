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
            self.read_class_with_id,
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

            yield self.parsers[record_type](record_type)

    def read(self):
        record = next(self.read_record())

        if record.type != RecordTypeEnum.SerializedStreamHeader:
            msg = "Expected SerializedStreamHeader record"

            raise ValueError(msg)

        self.header_record = record
    

    def read_serialized_stream_header(self, record_type: int) -> Record:
        root_id = self.stream.read_int32()
        header_id = self.stream.read_int32()
        major_version = self.stream.read_int32()
        minor_version = self.stream.read_int32()

        return RecordTypes[RecordTypeEnum.SerializedStreamHeader](
            record_type=record_type,
            root_id=root_id,
            header_id=header_id,
            major_version=major_version,
            minor_version=minor_version,
        )
    
    def read_class_with_id(self, record_type: int) -> Record:
        object_id = self.stream.read_int32()
        metadata_id = self.stream.read_string()

        return RecordTypes[RecordTypeEnum.ClassWithId](
            record_type=record_type,
            object_id=object_id,
            metadata_id=metadata_id,
        )
