import pytest
from rs_codec import RSCodecManager
from config import SystemConfig
from bitstream import generate_random_bytes

def test_rs_encode_decode_no_errors():
    manager = RSCodecManager()
    payload = generate_random_bytes(100)
    
    for profile in SystemConfig.RS_PROFILES:
        encoded = manager.encode_frame(payload, profile)
        decoded, corrections, success = manager.decode_frame(encoded, profile)
        
        assert success is True
        assert decoded == payload
        assert corrections == 0

def test_rs_error_correction_capacity():
    manager = RSCodecManager()
    payload = generate_random_bytes(223) # fits perfectly in (255, 223)
    profile = (255, 223)
    
    encoded = bytearray(manager.encode_frame(payload, profile))
    
    # (255, 223) has 32 parity bytes, can correct up to 16 byte errors
    # Let's inject 10 errors
    for i in range(10):
        encoded[i] = encoded[i] ^ 0xFF
        
    decoded, corrections, success = manager.decode_frame(bytes(encoded), profile)
    
    assert success is True
    assert decoded == payload
    assert corrections > 0

def test_rs_uncorrectable_errors():
    manager = RSCodecManager()
    payload = generate_random_bytes(223)
    profile = (255, 223)
    
    encoded = bytearray(manager.encode_frame(payload, profile))
    
    # Inject 20 errors, which exceeds the correction capacity of 16
    for i in range(20):
        encoded[i] = encoded[i] ^ 0xFF
        
    decoded, corrections, success = manager.decode_frame(bytes(encoded), profile)
    
    assert success is False
