from dataclasses import dataclass
from enum import IntEnum
from typing import Any


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


class BinaryTypeEnum(IntEnum):
    Primitive = 0
    String = 1
    Object = 2
    SystemClass = 3
    Class = 4
    ObjectArray = 5
    StringArray = 6
    PrimitiveArray = 7


@dataclass
class Record:
    type: RecordTypeEnum


@dataclass
class SerializationHeaderRecord(Record):
    root_id: int
    header_id: int
    major_version: int
    minor_version: int


@dataclass
class ClassWithIdRecord(Record):
    object_id: int
    metadata_id: str


@dataclass
class ClassInfo:
    object_id: int
    name: str
    member_count: int
    member_names: list[str]


@dataclass
class SystemClassWithMembersRecord(Record):
    class_info: ClassInfo


@dataclass
class ClassWithMembersRecord(Record):
    class_info: ClassInfo
    library_id: int


@dataclass
class MemberTypeInfo:
    binary_types: list[BinaryTypeEnum]
    additional_infos: list[Any]


@dataclass
class SystemClassWithMembersAndTypesRecord(Record):
    class_info: ClassInfo
    member_type_info: MemberTypeInfo


RecordTypes: list[Record] = [
    SerializationHeaderRecord,
    ClassWithIdRecord,
    SystemClassWithMembersRecord,
    ClassWithMembersRecord,
    SystemClassWithMembersAndTypesRecord,
]
