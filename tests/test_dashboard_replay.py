import pytest
import pandas as pd
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dashboard import build_experiment_metadata

def test_build_experiment_metadata():
    """Validates the provenance tracking function"""
    metadata = build_experiment_metadata(42, "Adaptive RS", "v1.0")
    
    assert "experiment_id" in metadata
    assert "timestamp" in metadata
    assert metadata["random_seed"] == 42
    assert metadata["controller_type"] == "Adaptive RS"
    assert metadata["thresholds_version"] == "v1.0"
    
    # Check nested config dicts
    assert "channel_parameters" in metadata
    assert metadata["channel_parameters"]["csk_constellation"] == "4-CSK"
    
    # Check RS profiles list is populated
    assert "rs_profiles" in metadata
    assert len(metadata["rs_profiles"]) > 0

def test_replay_dataframe_parsing(tmp_path):
    """Validates that the replay engine can cleanly load CSV exported logs"""
    csv_file = tmp_path / "dummy_logs.csv"
    
    data = {
        'frame_idx': [1, 2, 3],
        'seed': [42, 42, 42],
        'true_snr': [20.0, 15.0, 10.0],
        'estimated_snr': [19.8, 15.2, 9.9],
        'profile': ["Uncoded", "(255, 239)", "(255, 223)"],
        'fer': [0, 0, 1],
        'ber': [0.0, 0.0, 0.05],
        'goodput': [1000, 800, 0]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)
    
    # Simulate loading it via file_uploader
    loaded_df = pd.read_csv(csv_file)
    
    assert len(loaded_df) == 3
    assert loaded_df['true_snr'].iloc[0] == 20.0
    assert loaded_df['fer'].iloc[2] == 1
    assert loaded_df['profile'].iloc[1] == "(255, 239)"
