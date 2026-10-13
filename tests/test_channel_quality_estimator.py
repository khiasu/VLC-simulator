import pytest
import numpy as np
from channel_quality_estimator import ChannelQualityEstimator
from config import SystemConfig

def test_sliding_window_metrics():
    # Initialize estimator with a small window of 5 frames
    estimator = ChannelQualityEstimator(window_size=5)
    
    # 1. Update with 3 successful frames
    for i in range(3):
        estimator.update_link_history(frame_id=i, crc_pass=True, corrected_symbols=0, estimated_snr=20.0)
        
    state = estimator.get_channel_state()
    assert state['recent_fer'] == 0.0
    assert state['avg_snr_db'] == 20.0
    assert state['crc_failure_streak'] == 0
    assert state['avg_corrections'] == 0.0
    
    # 2. Update with 3 failed frames (should push out 1 successful frame since maxlen=5)
    for i in range(3, 6):
        estimator.update_link_history(frame_id=i, crc_pass=False, corrected_symbols=10, estimated_snr=5.0)
        
    state = estimator.get_channel_state()
    
    # Window currently holds: [Pass(20dB), Pass(20dB), Fail(5dB), Fail(5dB), Fail(5dB)]
    # FER = 3 failures out of 5 = 0.6
    assert pytest.approx(state['recent_fer']) == 0.6
    assert state['crc_failure_streak'] == 3
    assert state['avg_corrections'] == 6.0 # (0+0+10+10+10) / 5
    assert state['avg_snr_db'] == 11.0     # (20+20+5+5+5) / 5

def test_estimate_snr_perfect_signal():
    estimator = ChannelQualityEstimator()
    constellation = SystemConfig.CSK_4_MAP
    
    # Create perfect received symbols perfectly matching the constellation
    ref_vectors = np.array(list(constellation.values()))
    # Duplicate them to simulate 40 received symbols
    received_rgb = np.tile(ref_vectors, (10, 1))
    
    estimated_snr = estimator.estimate_snr_from_symbols(received_rgb, constellation)
    
    # Perfect signal (zero noise) should hit the artificial cap of 100.0 dB
    assert estimated_snr == 100.0

def test_estimate_snr_noisy_signal():
    estimator = ChannelQualityEstimator()
    constellation = SystemConfig.CSK_4_MAP
    
    ref_vectors = np.array(list(constellation.values()))
    received_rgb = np.tile(ref_vectors, (100, 1))
    
    # Inject significant Gaussian noise
    noise = np.random.normal(0, 0.2, received_rgb.shape)
    received_noisy = received_rgb + noise
    
    estimated_snr = estimator.estimate_snr_from_symbols(received_noisy, constellation)
    
    # The noise should cause the estimated SNR to drop significantly below the perfect 100 dB mark
    assert estimated_snr < 30.0
