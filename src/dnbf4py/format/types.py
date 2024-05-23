from dataclasses import dataclass
from typing import Any


@dataclass
class SerializationHeaderRecord:
    root_id: int
    header_id: int
    major_version: int
    minor_version: int
