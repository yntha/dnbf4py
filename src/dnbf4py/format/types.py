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


class BinaryArrayTypeEnum(IntEnum):
    Single = 0
    Jagged = 1
    Rectangular = 2
    SingleOffset = 3
    JaggedOffset = 4
    RectangularOffset = 5


class PrimitiveTypeEnum(IntEnum):
    Boolean = 1
    Byte = 2
    Char = 3
    Unused = 4
    Decimal = 5
    Double = 6
    Int16 = 7
    Int32 = 8
    Int64 = 9
    SByte = 10
    Single = 11
    TimeSpan = 12
    DateTime = 13
    UInt16 = 14
    UInt32 = 15
    UInt64 = 16
    Null = 17
    String = 18


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


@dataclass
class ClassWithMembersAndTypesRecord(Record):
    class_info: ClassInfo
    member_type_info: MemberTypeInfo
    library_id: int


@dataclass
class ClassTypeInfo:
    type_name: str
    library_id: int


@dataclass
class BinaryObjectStringRecord(Record):
    object_id: int
    value: str


@dataclass
class BinaryArrayRecord(Record):
    object_id: int
    binary_array_type: BinaryArrayTypeEnum
    rank: int
    lengths: list[int]
    lower_bounds: list[int]
    type: BinaryTypeEnum
    additional_type_info: Any


@dataclass
class MemberPrimitiveTypedRecord(Record):
    primitive_type: PrimitiveTypeEnum
    value: Any


@dataclass
class MemberReferenceRecord(Record):
    id_ref: int


@dataclass
class ObjectNullRecord(Record):
    pass


RecordTypes: list[Record] = [
    SerializationHeaderRecord,
    ClassWithIdRecord,
    SystemClassWithMembersRecord,
    ClassWithMembersRecord,
    SystemClassWithMembersAndTypesRecord,
    ClassWithMembersAndTypesRecord,
    BinaryObjectStringRecord,
    BinaryArrayRecord,
    MemberPrimitiveTypedRecord,
    MemberReferenceRecord,
    ObjectNullRecord,
]
