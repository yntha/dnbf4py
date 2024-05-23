from collections.abc import Generator
from enum import IntEnum
from pathlib import Path
from typing import Self

from datastream import DeserializingStream, SerializingStream

from dnbf4py.format.types import Record, RecordTypes


class RecordTypeEnum(IntEnum):
    SerializedStreamHeader = 0
    ClassWithId = 1
    SystemClassWithMembers = 2
    ClassWithMembers = 3
    SystemClassWithMembersAndTypes = 4
    ClassWithMembersAndTypes = 5
    BinaryObjectString = 6
    BinaryArray = 7
    MemberPrimitiveTyped = 8
    MemberReference = 9
    ObjectNull = 10
    MessageEnd = 11
    BinaryLibrary = 12
    ObjectNullMultiple256 = 13
    ObjectNullMultiple = 14
    ArraySinglePrimitive = 15
    ArraySingleObject = 16
    ArraySingleString = 17
    MethodCall = 21
    MethodReturn = 22


class DNBinaryFormat:
    def __init__(self, stream: DeserializingStream):
        self.stream = stream
        self.header_record = None

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

            yield RecordTypes[record_type]

    def read(self):
        record = next(self.read_record())

        if record.type != RecordTypeEnum.SerializedStreamHeader:
            msg = "Expected SerializedStreamHeader record"

            raise ValueError(msg)

        self.header_record = record
