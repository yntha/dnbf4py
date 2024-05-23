from typing import *
from pathlib import Path
from datastream import DeserializingStream, SerializingStream


class DNBinaryFormat:
    def __init__(self, stream: DeserializingStream):
        self.stream = stream
