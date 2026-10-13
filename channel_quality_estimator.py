import numpy as np
from collections import deque
from typing import Dict

class ChannelQualityEstimator:
    """
    Estimates optical channel quality at the receiver by calculating SNR from EVM
    and maintaining a sliding window of historical link performance metrics.
    """
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        
        # Sliding windows for link history
        self.history_crc = deque(maxlen=window_size)
        self.history_corrections = deque(maxlen=window_size)
        self.history_snr = deque(maxlen=window_size)
        
        self.crc_failure_streak = 0
        self.latest_estimated_snr = 0.0

    @staticmethod
    def estimate_snr_from_symbols(received_rgb: np.ndarray, reference_constellation: dict) -> float:
        """
        Calculates Error Vector Magnitude (EVM) from received RGB vectors against 
        the reference constellation, and converts it to estimated SNR in dB.
        """
        ref_vectors = np.array(list(reference_constellation.values()))
        
        # Find the closest reference constellation point for each received symbol (Minimum Euclidean Distance)
        # Broadcasting: received_rgb is (M, 3), ref_vectors is (4, 3)
        diff = received_rgb[:, np.newaxis, :] - ref_vectors[np.newaxis, :, :]
        dist_sq = np.sum(diff ** 2, axis=2)
        closest_indices = np.argmin(dist_sq, axis=1)
        
        # Get the actual ideal vectors that the receiver mapped to
        ideal_vectors = ref_vectors[closest_indices]
        
        # Calculate Error Vectors (difference between received and ideal)
        error_vectors = received_rgb - ideal_vectors
        
        # Calculate Mean Square Error (noise power) and Mean Square Ideal (signal power)
        mean_square_error = np.mean(np.sum(error_vectors ** 2, axis=1))
        mean_square_ideal = np.mean(np.sum(ideal_vectors ** 2, axis=1))
        
        if mean_square_error == 0:
            return 100.0 # Arbitrary high SNR cap for a completely perfect, noise-free signal
            
        # EVM approximation to SNR: SNR ≈ Signal Power / Error Power
        snr_linear = mean_square_ideal / mean_square_error
        
        # Convert to Decibels (dB)
        snr_db = 10 * np.log10(snr_linear)
        return float(snr_db)

    def update_link_history(self, frame_id: int, crc_pass: bool, corrected_symbols: int, estimated_snr: float):
        """
        Updates the sliding windows with data from the most recently decoded frame.
        """
        self.history_crc.append(1 if crc_pass else 0)
        self.history_corrections.append(corrected_symbols)
        self.history_snr.append(estimated_snr)
        
        self.latest_estimated_snr = estimated_snr
        
        # Update consecutive failure streak
        if not crc_pass:
            self.crc_failure_streak += 1
        else:
            self.crc_failure_streak = 0

    def get_channel_state(self) -> Dict:
        """
        Returns the computed metrics based on the current sliding window history.
        """
        if not self.history_crc:
            return {
                'estimated_snr_db': 0.0,
                'avg_snr_db': 0.0,
                'recent_fer': 0.0,
                'avg_corrections': 0.0,
                'crc_failure_streak': 0
            }
            
        # FER is the percentage of failures (1.0 - pass rate)
        recent_fer = 1.0 - float(np.mean(self.history_crc))
        avg_corrections = float(np.mean(self.history_corrections))
        avg_snr_db = float(np.mean(self.history_snr))
        
        return {
            'estimated_snr_db': self.latest_estimated_snr,
            'avg_snr_db': avg_snr_db,
            'recent_fer': recent_fer,
            'avg_corrections': avg_corrections,
            'crc_failure_streak': self.crc_failure_streak
        }
