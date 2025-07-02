import struct
from typing import List, Union

def normalize_words(words: List[int]) -> List[int]:
    """Ensure values are treated as unsigned 16-bit integers."""
    return [w & 0xFFFF for w in words]

def _read_words(data: List[int], count: int, index: int, inverse: bool) -> bytes:
    words = data[index:index + count]
    words = normalize_words(words[::-1] if not inverse else words)
    return struct.pack(f'>{count}H', *words)

def _write_words(raw: bytes, count: int, inverse: bool) -> List[int]:
    words = list(struct.unpack(f'>{count}H', raw))
    return words if inverse else words[::-1]

# === 32-bit FLOAT ===
def to_float32(data: List[int], index: int = 0, inverse: bool = True) -> float:
    return round(struct.unpack('>f', _read_words(data, 2, index, inverse))[0],3)

def from_float32(value: float, inverse: bool = True) -> List[int]:
    return _write_words(struct.pack('>f', value), 2, inverse)

# === 64-bit DOUBLE ===
def to_double64(data: List[int], index: int = 0, inverse: bool = True) -> float:
    return round(struct.unpack('>d', _read_words(data, 4, index, inverse))[0],3)

def from_double64(value: float, inverse: bool = True) -> List[int]:
    return _write_words(struct.pack('>d', value), 4, inverse)

# === 64-bit LONG (signed) ===
def to_long64(data: List[int], index: int = 0, inverse: bool = True) -> int:
    return round(struct.unpack('>q', _read_words(data, 4, index, inverse))[0],3)

def from_long64(value: int, inverse: bool = True) -> List[int]:
    return _write_words(struct.pack('>q', value), 4, inverse)

# === 64-bit ULONG (unsigned) ===
def to_ulong64(data: List[int], index: int = 0, inverse: bool = True) -> int:
    return round(struct.unpack('>Q', _read_words(data, 4, index, inverse))[0],3)

def from_ulong64(value: int, inverse: bool = True) -> List[int]:
    return _write_words(struct.pack('>Q', value), 4, inverse)

# === 32-bit SIGNED INTEGER ===
def to_int32(data: List[int], index: int = 0, inverse: bool = True) -> int:
    return struct.unpack('>i', _read_words(data, 2, index, inverse))[0]

def from_int32(value: int, inverse: bool = True) -> List[int]:
    return _write_words(struct.pack('>i', value), 2, inverse)

# === 32-bit UNSIGNED INTEGER ===
def to_uint32(data: List[int], index: int = 0, inverse: bool = True) -> int:
    return struct.unpack('>I', _read_words(data, 2, index, inverse))[0]

def from_uint32(value: int, inverse: bool = True) -> List[int]:
    return _write_words(struct.pack('>I', value), 2, inverse)


