from collections.abc import Generator
from pathlib import Path
from typing import Self

from datastream import DeserializingStream

from dnbf4py.format.types import (
    ArrayInfo,
    ArrayOfValueWithCode,
    BinaryArrayTypeEnum,
    BinaryTypeEnum,
    ClassInfo,
    ClassTypeInfo,
    MemberPrimitiveUnTyped,
    MemberTypeInfo,
    MessageFlags,
    PrimitiveTypeEnum,
    Record,
    RecordTypeEnum,
    RecordTypes,
    StringValueWithCode,
    ValueWithCode,
)


class DNBinaryFormat:
    def __init__(self, stream: DeserializingStream):
        self.stream = stream
        self.header_record = None
        self.parsers = [
            self.read_serialized_stream_header,
            self.read_class_with_id,
            self.read_system_class_with_members,
            self.read_class_with_members,
            self.read_system_class_with_members_and_types,
            self.read_class_with_members_and_types,
            self.read_binary_object_string,
            self.read_binary_array,
            self.read_member_primitive_typed,
            self.read_member_reference,
            self.read_object_null,
            self.read_message_end,
            self.read_binary_library,
            self.read_object_null_multiple_256,
            self.read_object_null_multiple,
            self.read_array_single_primitive,
            self.read_array_single_object,
            self.read_array_single_string,
            self.read_binary_method_call,
            self.read_binary_method_return,
        ]
        self.varint_max_bytes = 5

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        return cls(DeserializingStream(data))

    @classmethod
    def from_file(cls, path: str | Path) -> Self:
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

    def read_system_class_with_members(self, record_type: int) -> Record:
        class_info = self.read_class_info()

        return RecordTypes[RecordTypeEnum.SystemClassWithMembers](
            record_type=record_type,
            class_info=class_info,
        )

    def read_class_with_members(self, record_type: int) -> Record:
        class_info = self.read_class_info()
        library_id = self.stream.read_int32()

        return RecordTypes[RecordTypeEnum.ClassWithMembers](
            record_type=record_type,
            class_info=class_info,
            library_id=library_id,
        )

    def read_member_type_info(self) -> MemberTypeInfo:
        binary_types = [self.stream.read_uint8() for _ in range(class_info.member_count)]
        additional_infos = [self.stream.read() for _ in range(class_info.member_count)]

        return MemberTypeInfo(
            binary_types=binary_types,
            additional_infos=additional_infos,
        )

    def read_system_class_with_members_and_types(self, record_type: int) -> Record:
        class_info = self.read_class_info()
        member_type_info = self.read_member_type_info()

        return RecordTypes[RecordTypeEnum.SystemClassWithMembersAndTypes](
            record_type=record_type,
            class_info=class_info,
            member_type_info=member_type_info,
        )

    def read_class_with_members_and_types(self, record_type: int) -> Record:
        class_info = self.read_class_info()
        library_id = self.stream.read_int32()
        member_type_info = self.read_member_type_info()

        return RecordTypes[RecordTypeEnum.ClassWithMembersAndTypes](
            record_type=record_type,
            class_info=class_info,
            member_type_info=member_type_info,
            library_id=library_id,
        )

    def read_binary_object_string(self, record_type: int) -> Record:
        object_id = self.stream.read_int32()
        value = self.read_length_prefixed_string()

        return RecordTypes[RecordTypeEnum.BinaryObjectString](
            record_type=record_type,
            object_id=object_id,
            value=value,
        )

    def read_class_type_info(self) -> ClassTypeInfo:
        type_name = self.read_length_prefixed_string()
        library_id = self.stream.read_int32()

        return ClassTypeInfo(
            type_name=type_name,
            library_id=library_id,
        )

    def read_binary_array(self, record_type: int) -> Record:
        object_id = self.stream.read_int32()
        binary_array_type = BinaryArrayTypeEnum(self.stream.read_uint8())
        rank = self.stream.read_int32()
        lengths = [self.stream.read_int32() for _ in range(rank)]
        lower_bounds = [self.stream.read_int32() for _ in range(rank)]
        type_enum = BinaryTypeEnum(self.stream.read_uint8())
        type_info = None

        if type_enum == BinaryTypeEnum.Primitive:
            type_info = PrimitiveTypeEnum(self.stream.read_uint8())
        elif type_enum == BinaryTypeEnum.PrimitiveArray:
            type_info = PrimitiveTypeEnum(self.stream.read_uint8())
        elif type_enum == BinaryTypeEnum.SystemClass:
            type_info = self.read_length_prefixed_string()  # should be class name
        elif type_enum == BinaryTypeEnum.Class:
            type_info = self.read_class_type_info()
        else:
            raise ValueError("Invalid BinaryTypeEnum")

        return RecordTypes[RecordTypeEnum.BinaryArray](
            record_type=record_type,
            object_id=object_id,
            binary_array_type=binary_array_type,
            rank=rank,
            lengths=lengths,
            lower_bounds=lower_bounds,
            type=type_enum,
            additional_type_info=type_info,
        )

    def read_member_primitive_typed(self, record_type: int) -> Record:
        primitive_type = PrimitiveTypeEnum(self.stream.read_uint8())
        value = self.stream.read()  # TODO: read based on primitive type

        return RecordTypes[RecordTypeEnum.MemberPrimitiveTyped](
            record_type=record_type,
            primitive_type=primitive_type,
            value=value,
        )

    def read_member_reference(self, record_type: int) -> Record:
        id_ref = self.stream.read_int32()

        return RecordTypes[RecordTypeEnum.MemberReference](
            record_type=record_type,
            id_ref=id_ref,
        )

    def read_object_null(self, record_type: int) -> Record:
        return RecordTypes[RecordTypeEnum.ObjectNull](
            record_type=record_type,
        )

    def read_message_end(self, record_type: int) -> Record:
        return RecordTypes[RecordTypeEnum.MessageEnd](
            record_type=record_type,
        )

    def read_binary_library(self, record_type: int) -> Record:
        library_id = self.stream.read_int32()
        library_name = self.read_length_prefixed_string()

        return RecordTypes[RecordTypeEnum.BinaryLibrary](
            record_type=record_type,
            library_id=library_id,
            library_name=library_name,
        )

    def read_object_null_multiple_256(self, record_type: int) -> Record:
        null_count = self.stream.read_uint8()

        return RecordTypes[RecordTypeEnum.ObjectNullMultiple256](
            record_type=record_type,
            null_count=null_count,
        )

    def read_object_null_multiple(self, record_type: int) -> Record:
        null_count = self.stream.read_int32()

        return RecordTypes[RecordTypeEnum.ObjectNullMultiple](
            record_type=record_type,
            null_count=null_count,
        )

    def read_array_info(self) -> ArrayInfo:
        object_id = self.stream.read_int32()
        length = self.stream.read_int32()

        return ArrayInfo(
            object_id=object_id,
            length=length,
        )

    def read_array_single_primitive(self, record_type: int) -> Record:
        array_info = self.read_array_info()
        binary_array_type = BinaryArrayTypeEnum(self.stream.read_uint8())
        type_enum = PrimitiveTypeEnum(self.stream.read_uint8())

        return RecordTypes[RecordTypeEnum.ArraySinglePrimitive](
            record_type=record_type,
            array_info=array_info,
            binary_array_type=binary_array_type,
            type=type_enum,
        )

    def read_array_single_object(self, record_type: int) -> Record:
        array_info = self.read_array_info()

        return RecordTypes[RecordTypeEnum.ArraySingleObject](
            record_type=record_type,
            array_info=array_info,
        )

    def read_array_single_string(self, record_type: int) -> Record:
        array_info = self.read_array_info()

        return RecordTypes[RecordTypeEnum.ArraySingleString](
            record_type=record_type,
            array_info=array_info,
        )
    
    def read_string_value_with_code(self) -> StringValueWithCode:
        primitive_type = PrimitiveTypeEnum(self.stream.read_uint8())
        string_value = self.stream.read_string()

        if primitive_type != PrimitiveTypeEnum.String:
            raise ValueError("Expected PrimitiveTypeEnum.String")

        return StringValueWithCode(
            primitive_type=primitive_type,
            string_value=string_value,
        )
    
    def read_value_with_code(self) -> ValueWithCode:
        primitive_type = PrimitiveTypeEnum(self.stream.read_uint8())
        value = self.stream.read()  # todo: read based on primitive type

        return ValueWithCode(
            primitive_type=primitive_type,
            value=value,
        )
    
    def read_array_of_value_with_code(self) -> ArrayOfValueWithCode:
        length = self.stream.read_int32()
        values = [self.read_value_with_code() for _ in range(length)]

        return ArrayOfValueWithCode(
            length=length,
            values=values,
        )
    
    def read_binary_method_call(self, record_type: int) -> Record:
        message_flags = MessageFlags(self.stream.read_uint8())
        method_name = self.read_string_value_with_code()
        type_name = self.read_string_value_with_code()
        call_context = self.read_string_value_with_code()
        args = self.read_array_of_value_with_code()

        return RecordTypes[RecordTypeEnum.BinaryMethodCall](
            record_type=record_type,
            message_flags=message_flags,
            method_name=method_name,
            type_name=type_name,
            call_context=call_context,
            args=args,
        )
    
    def read_binary_method_return(self, record_type: int) -> Record:
        message_flags = MessageFlags(self.stream.read_uint8())
        return_value = self.read_value_with_code()
        call_context = self.read_string_value_with_code()
        args = self.read_array_of_value_with_code()

        return RecordTypes[RecordTypeEnum.BinaryMethodReturn](
            record_type=record_type,
            message_flags=message_flags,
            return_value=return_value,
            call_context=call_context,
            args=args,
        )
    
    def read_member_primitive_untyped(self) -> MemberPrimitiveUnTyped:
        value = self.stream.read()

        return MemberPrimitiveUnTyped(
            value=value,
        )
