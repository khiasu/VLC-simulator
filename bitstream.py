import os
import numpy as np

def generate_random_bytes(num_bytes: int) -> bytes:
    """Generates a random sequence of bytes."""
    return os.urandom(num_bytes)

def bytes_to_bit_array(data: bytes) -> np.ndarray:
    """Converts a sequence of bytes into a 1D NumPy array of bits (0s and 1s)."""
    # np.unpackbits requires a uint8 array
    bit_array = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    return bit_array

def bit_array_to_bytes(bits: np.ndarray) -> bytes:
    """Converts a 1D NumPy array of bits back into a sequence of bytes."""
    byte_array = np.packbits(bits)
    return byte_array.tobytes()
