import pytest
import json
import os
from adaptive_controller import AdaptiveLinkController
from config import SystemConfig

@pytest.fixture(scope="module")
def mock_thresholds():
    # Setup dummy thresholds file specifically designed for this test
    json_path = "test_adaptive_thresholds.json"
    thresholds = {
        "(255, 223)": -999.0,
        "(255, 239)": 10.0,
        "(255, 247)": 999.0,   # Simulated as never optimal
        "(255, 251)": 15.0,
        "UNCODED": 20.0
    }
    with open(json_path, 'w') as f:
        json.dump(thresholds, f)
    yield json_path
    
    # Teardown
    if os.path.exists(json_path):
        os.remove(json_path)

def test_escalation_trigger(mock_thresholds):
    controller = AdaptiveLinkController(thresholds_json=mock_thresholds)
    
    # Excellent SNR, but we manually trigger a high CRC failure streak
    channel_state = {
        'avg_snr_db': 25.0,
        'recent_fer': 0.0,
        'crc_failure_streak': 2
    }
    
    # Current profile is UNCODED (idx=4)
    profile, idx, trace = controller.select_rs_profile(channel_state, current_profile_idx=4)
    
    # Should ignore SNR and force escalation to maximum protection (idx=0)
    assert idx == 0
    assert "[ESCALATION]" in trace

def test_hysteresis_upgrade_downgrade(mock_thresholds):
    controller = AdaptiveLinkController(thresholds_json=mock_thresholds)
    
    # Current state: We are at (255, 251) which is index 3. Its threshold is 15.0.
    # To upgrade to UNCODED (threshold 20.0), we need 20.0 + 0.5 = 20.5 SNR
    
    # SNR = 20.2 -> Should MAINTAIN because it hasn't completely cleared the upper margin (20.5)
    state_maintain = {'avg_snr_db': 20.2, 'recent_fer': 0.0, 'crc_failure_streak': 0}
    prof, idx, trace = controller.select_rs_profile(state_maintain, current_profile_idx=3)
    assert idx == 3
    assert "[MAINTAIN]" in trace
    
    # SNR = 20.6 -> Should UPGRADE because it cleared 20.5
    state_upgrade = {'avg_snr_db': 20.6, 'recent_fer': 0.0, 'crc_failure_streak': 0}
    prof, idx, trace = controller.select_rs_profile(state_upgrade, current_profile_idx=3)
    assert idx == 4
    assert "[UPGRADE]" in trace
    
    # Current state: We are now at UNCODED (index 4). Its threshold is 20.0.
    # To downgrade to (255, 251), the SNR needs to drop below 20.0 - 0.5 = 19.5
    
    # SNR = 19.8 -> Should MAINTAIN (it dropped, but it's still within the safe margin)
    state_maintain_2 = {'avg_snr_db': 19.8, 'recent_fer': 0.0, 'crc_failure_streak': 0}
    prof, idx, trace = controller.select_rs_profile(state_maintain_2, current_profile_idx=4)
    assert idx == 4
    
    # SNR = 19.2 -> Should DOWNGRADE (it dropped fully below the safe margin)
    state_downgrade = {'avg_snr_db': 19.2, 'recent_fer': 0.0, 'crc_failure_streak': 0}
    prof, idx, trace = controller.select_rs_profile(state_downgrade, current_profile_idx=4)
    assert idx == 3
    assert "[DOWNGRADE]" in trace
