import numpy as np
from typing import Optional

class OpticalChannel:
    """
    Simulates the indoor optical channel impairments for VLC.
    Includes LED Dimming, RGB Crosstalk, and Additive White Gaussian Noise (AWGN).
    """
    
    @staticmethod
    def transmit(rgb_symbols: np.ndarray, snr_db: float, dimming_factor: float = 1.0, crosstalk_matrix: Optional[np.ndarray] = None, apply_agc: bool = True) -> np.ndarray:
        """
        Passes the RGB symbols through the simulated optical channel.
        """
        # 1. LED Dimming
        # Clip dimming factor to realistic bounds (10% to 100%)
        dimming_factor = np.clip(dimming_factor, 0.1, 1.0)
        signal = rgb_symbols * dimming_factor
        
        # 2. RGB Crosstalk
        if crosstalk_matrix is None:
            # Default: ~10% overlap with adjacent color channels
            crosstalk_matrix = np.array([
                [0.9, 0.1, 0.0],  # R mixes slightly into G
                [0.1, 0.8, 0.1],  # G mixes into R and B
                [0.0, 0.1, 0.9]   # B mixes slightly into G
            ])
            
        # Matrix multiply: signal (M x 3) @ crosstalk (3 x 3)
        signal = signal @ crosstalk_matrix
        
        # 3. Additive White Gaussian Noise (AWGN)
        # Calculate nominal signal power (average power per symbol across all channels)
        # Noise floor should be based on the UNDIMMED signal power, so dimming reduces SNR.
        nominal_signal_power = np.mean(rgb_symbols ** 2)
        
        # Convert SNR from dB to linear scale
        snr_linear = 10 ** (snr_db / 10.0)
        
        # Calculate noise variance based on nominal SNR
        noise_variance = nominal_signal_power / snr_linear if snr_linear > 0 else 0
        noise_std_dev = np.sqrt(noise_variance)
        
        # Generate Gaussian noise and add it
        noise = np.random.normal(0, noise_std_dev, signal.shape)
        noisy_signal = signal + noise
        
        # If AGC is disabled, return raw optical intensity incident on the photodiode
        if not apply_agc:
            return np.clip(noisy_signal, 0.0, None)
        
        # 4. Receiver Automatic Gain Control (AGC) & Clipping
        # The receiver's AGC amplifies the signal to restore its nominal scale for demapping.
        # This amplifies the noise proportionally, correctly modeling SNR degradation.
        agc_signal = noisy_signal / dimming_factor
        
        # Light intensity registered by photodiodes cannot be mathematically negative
        received_signal = np.clip(agc_signal, 0.0, None)
        
        return received_signal
