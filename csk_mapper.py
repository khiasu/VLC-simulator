import numpy as np
from config import SystemConfig

class CSKMapper:
    """
    Handles modulation (mapping) and demodulation (demapping) for 4-CSK (Color Shift Keying).
    """
    
    # Pre-compute constellation values for faster demapping
    _CONSTELLATION_KEYS = ['00', '01', '10', '11']
    # Matrix of shape (4, 3) where each row is the RGB vector for a 2-bit symbol
    _CONSTELLATION_VECTORS = np.array([SystemConfig.CSK_4_MAP[k] for k in _CONSTELLATION_KEYS])
    
    @classmethod
    def map_bits_to_csk(cls, bit_array: np.ndarray) -> np.ndarray:
        """
        Maps a 1D array of bits into an M x 3 array of RGB intensity vectors.
        Assumes the length of bit_array is even. If odd, pads with one zero.
        """
        if len(bit_array) % 2 != 0:
            bit_array = np.append(bit_array, 0)
            
        # Reshape into pairs of bits: (M, 2)
        bit_pairs = bit_array.reshape(-1, 2)
        
        # Convert pairs to integer indices (0 to 3)
        # e.g. [1, 0] -> 2, [0, 1] -> 1
        indices = bit_pairs[:, 0] * 2 + bit_pairs[:, 1]
        
        # Map to RGB vectors
        mapped_rgb = cls._CONSTELLATION_VECTORS[indices]
        
        return mapped_rgb
        
    @classmethod
    def demap_csk_to_bits(cls, received_rgb: np.ndarray) -> np.ndarray:
        """
        Demaps an M x 3 array of received RGB vectors back into a 1D bit array 
        using Minimum Euclidean Distance (nearest-neighbor).
        """
        # received_rgb is shape (M, 3)
        # _CONSTELLATION_VECTORS is shape (4, 3)
        
        # Use broadcasting to compute distances efficiently.
        # diff shape becomes (M, 4, 3)
        diff = received_rgb[:, np.newaxis, :] - cls._CONSTELLATION_VECTORS[np.newaxis, :, :]
        
        # Compute squared euclidean distance: sum of squared differences along the RGB axis
        # dist_sq shape becomes (M, 4)
        dist_sq = np.sum(diff ** 2, axis=2)
        
        # Find the index of the minimum distance for each received symbol
        # closest_indices shape becomes (M,)
        closest_indices = np.argmin(dist_sq, axis=1)
        
        # Convert indices back to bit pairs
        # index 0 -> [0, 0], index 1 -> [0, 1], index 2 -> [1, 0], index 3 -> [1, 1]
        bit_0 = (closest_indices // 2).reshape(-1, 1)
        bit_1 = (closest_indices % 2).reshape(-1, 1)
        
        bit_pairs = np.hstack((bit_0, bit_1))
        
        # Flatten back to 1D bit array
        return bit_pairs.flatten().astype(np.uint8)
