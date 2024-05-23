from collections.abc import Generator
from enum import IntEnum
from pathlib import Path
from typing import Self

from datastream import DeserializingStream, SerializingStream

from dnbf4py.format.types import ClassInfo, Record, RecordTypeEnum, RecordTypes


class DNBinaryFormat:
    def __init__(self, stream: DeserializingStream):
        self.stream = stream
        self.header_record = None
        self.parsers = [
            self.read_serialized_stream_header,
            self.read_class_with_id,
        ]
        self.varint_max_bytes = 5

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
    def read_varint(self) -> int:
        result = 0
        shift = 0
        shift_amount = 7

        while shift <= (self.varint_max_bytes * (shift_amount - 1)):
            byte = self.stream.read_uint8()

            result |= (byte & 0x7F) << shift
            shift += shift_amount

            if byte & 0x80 == 0:
                break
        
        return result
    
    def read_length_prefixed_string(self) -> str:
        length = self.read_varint()
        string_data = self.stream.read(length)

        return string_data.decode("utf-8")
        
    
    def read_class_info(self) -> ClassInfo:
        object_id = self.stream.read_int32()
        name = self.read_length_prefixed_string()
        member_count = self.stream.read_int32()
        member_names = [self.read_length_prefixed_string() for _ in range(member_count)]

        return ClassInfo(
            object_id=object_id,
            name=name,
            member_count=member_count,
            member_names=member_names,
        )
    
