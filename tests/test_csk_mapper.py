import pytest
import numpy as np
from csk_mapper import CSKMapper

def test_csk_mapping_demapping_no_noise():
    # Create random bit array of even length
    original_bits = np.random.randint(0, 2, 1000, dtype=np.uint8)
    
    # Map to CSK
    mapped_rgb = CSKMapper.map_bits_to_csk(original_bits)
    
    # Ensure shape is (500, 3) because every 2 bits become 1 RGB symbol
    assert mapped_rgb.shape == (500, 3)
    
    # Demap back to bits
    demapped_bits = CSKMapper.demap_csk_to_bits(mapped_rgb)
    
    # Assert 100% match
    np.testing.assert_array_equal(original_bits, demapped_bits)
