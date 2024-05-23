from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dnbf4py.format.format import RecordTypeEnum


@dataclass
class Record:
    type: RecordTypeEnum


@dataclass
class SerializationHeaderRecord:
    root_id: int
    header_id: int
    major_version: int
    minor_version: int
