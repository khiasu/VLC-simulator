import reedsolo
from typing import Union, Tuple
from config import SystemConfig

class RSCodecManager:
    """
    Manages Reed-Solomon (RS) encoding and decoding based on dynamic profiles.
    """
    def __init__(self):
        self.codecs = {}
        # Initialize reedsolo codecs for all configured profiles
        for profile in SystemConfig.RS_PROFILES:
            if profile != "UNCODED":
                n, k = profile
                # reedsolo takes the number of error correction symbols (nsym = n - k)
                nsym = n - k
                self.codecs[profile] = reedsolo.RSCodec(nsym)
                
    def encode_frame(self, frame_bytes: bytes, profile: Union[Tuple[int, int], str]) -> bytes:
        """
        Encodes the frame bytes using the specified Reed-Solomon profile.
        Chunks data if necessary.
        """
        if profile == "UNCODED":
            return frame_bytes
            
        n, k = profile
        codec = self.codecs[profile]
        
        # Chunking: split the frame into chunks of maximum size K
        encoded_chunks = bytearray()
        for i in range(0, len(frame_bytes), k):
            chunk = frame_bytes[i:i+k]
            encoded_chunk = codec.encode(chunk)
            encoded_chunks.extend(encoded_chunk)
            
        return bytes(encoded_chunks)
        
    def decode_frame(self, encoded_bytes: bytes, profile: Union[Tuple[int, int], str]) -> Tuple[bytes, int, bool]:
        """
        Decodes the frame bytes using the specified Reed-Solomon profile.
        Returns: (recovered_frame_bytes, total_corrected_symbols, decoding_success)
        """
        if profile == "UNCODED":
            return encoded_bytes, 0, True
            
        n, k = profile
        codec = self.codecs[profile]
        
        recovered_frame = bytearray()
        total_corrected = 0
        
        # Decode chunk by chunk
        for i in range(0, len(encoded_bytes), n):
            chunk = encoded_bytes[i:i+n]
            if not chunk:
                break
            try:
                # codec.decode returns (decoded_data, decoded_data_with_ecc, error_locations)
                decoded_data, _, err_locs = codec.decode(chunk)
                recovered_frame.extend(decoded_data)
                
                if err_locs is not None:
                     total_corrected += len(err_locs) if isinstance(err_locs, (list, bytearray)) else 0
                
            except reedsolo.ReedSolomonError:
                # Uncorrectable error encountered
                return encoded_bytes, -1, False
                
        return bytes(recovered_frame), total_corrected, True
