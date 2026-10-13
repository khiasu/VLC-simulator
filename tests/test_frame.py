import pytest
import numpy as np
from bitstream import generate_random_bytes, bytes_to_bit_array, bit_array_to_bytes
from frame import FrameManager

def test_bitstream_roundtrip():
    original_bytes = generate_random_bytes(100)
    bits = bytes_to_bit_array(original_bytes)
    recovered_bytes = bit_array_to_bytes(bits)
    assert original_bytes == recovered_bytes

def test_frame_header_parsing_and_crc():
    payload = generate_random_bytes(200)
    frame_id = 42
    rs_profile_idx = 2
    
    # Build
    frame_bytes = FrameManager.build_frame(frame_id, payload, rs_profile_idx)
    
    # Parse
    header, parsed_payload, is_crc_valid = FrameManager.parse_frame(frame_bytes)
    
    assert header['frame_id'] == frame_id
    assert header['payload_len'] == 200
    assert header['rs_profile_idx'] == rs_profile_idx
    assert parsed_payload == payload
    assert is_crc_valid is True

def test_frame_crc_failure_detection():
    payload = generate_random_bytes(200)
    frame_bytes = bytearray(FrameManager.build_frame(1, payload, 0))
    
    # Mutate a byte in the payload to simulate an error
    frame_bytes[10] = frame_bytes[10] ^ 0xFF
    
    header, parsed_payload, is_crc_valid = FrameManager.parse_frame(bytes(frame_bytes))
    
    assert is_crc_valid is False
