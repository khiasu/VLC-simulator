import pytest
import numpy as np
from csk_mapper import CSKMapper
from optical_channel import OpticalChannel

def test_dimming_reduces_power():
    bits = np.random.randint(0, 2, 200, dtype=np.uint8)
    symbols = CSKMapper.map_bits_to_csk(bits)
    
    # Transmit with high SNR (negligible noise) and identity crosstalk to isolate dimming effect
    identity_crosstalk = np.eye(3)
    
    # Full power at photodiode (prior to receiver AGC amplification)
    rx_full = OpticalChannel.transmit(symbols, snr_db=100, dimming_factor=1.0, crosstalk_matrix=identity_crosstalk, apply_agc=False)
    # Dimmed power at photodiode
    rx_dim = OpticalChannel.transmit(symbols, snr_db=100, dimming_factor=0.5, crosstalk_matrix=identity_crosstalk, apply_agc=False)
    
    power_full = np.mean(rx_full ** 2)
    power_dim = np.mean(rx_dim ** 2)
    
    # Dimmed power at photodiode should be lower
    assert power_dim < power_full
    assert pytest.approx(power_dim, rel=0.1) == power_full * (0.5 ** 2)

def test_dimming_with_agc_increases_errors():
    # When AGC normalizes the constellation, the amplified noise causes more demapping errors
    bits = np.random.randint(0, 2, 2000, dtype=np.uint8)
    symbols = CSKMapper.map_bits_to_csk(bits)
    
    np.random.seed(42)
    rx_undimmed = OpticalChannel.transmit(symbols, snr_db=16, dimming_factor=1.0)
    bits_undimmed = CSKMapper.demap_csk_to_bits(rx_undimmed)
    errors_undimmed = np.sum(bits != bits_undimmed)
    
    np.random.seed(42)
    rx_dimmed = OpticalChannel.transmit(symbols, snr_db=16, dimming_factor=0.5)
    bits_dimmed = CSKMapper.demap_csk_to_bits(rx_dimmed)
    errors_dimmed = np.sum(bits != bits_dimmed)
    
    assert errors_dimmed > errors_undimmed

def test_noise_increases_errors():
    bits = np.random.randint(0, 2, 2000, dtype=np.uint8)
    symbols = CSKMapper.map_bits_to_csk(bits)
    
    # Transmit with high SNR (clean channel)
    rx_clean = OpticalChannel.transmit(symbols, snr_db=40, dimming_factor=1.0)
    bits_clean = CSKMapper.demap_csk_to_bits(rx_clean)
    errors_clean = np.sum(bits != bits_clean)
    
    # Transmit with low SNR (very noisy channel)
    rx_noisy = OpticalChannel.transmit(symbols, snr_db=0, dimming_factor=1.0)
    bits_noisy = CSKMapper.demap_csk_to_bits(rx_noisy)
    errors_noisy = np.sum(bits != bits_noisy)
    
    # Low SNR should have significantly more errors than high SNR
    assert errors_noisy > errors_clean
