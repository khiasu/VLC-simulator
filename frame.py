import struct
import zlib
from typing import Tuple, Dict

class FrameManager:
    """
    Manages the construction and parsing of data frames.
    A frame consists of: Header (8 bytes) + Payload (N bytes) + CRC32 (4 bytes).
    """
    
    # Format for struct pack/unpack: Big-endian (>), Unsigned Int (I - 4 bytes), Unsigned Short (H - 2 bytes), Unsigned Short (H - 2 bytes)
    # Total = 4 + 2 + 2 = 8 bytes
    HEADER_FORMAT = '>IHH'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    CRC_SIZE = 4
    
    @classmethod
    def build_frame(cls, frame_id: int, payload: bytes, rs_profile_idx: int) -> bytes:
        """
        Constructs a complete frame with a header, the payload, and a CRC32 checksum.
        """
        # Calculate CRC32 of the payload
        # bitwise AND with 0xFFFFFFFF ensures it is a 32-bit unsigned integer across all python versions
        crc32_val = zlib.crc32(payload) & 0xFFFFFFFF
        crc32_bytes = struct.pack('>I', crc32_val)
        
        # Create Header
        header = struct.pack(cls.HEADER_FORMAT, frame_id, len(payload), rs_profile_idx)
        
        # Combine Header, Payload, and CRC32
        return header + payload + crc32_bytes
        
    @classmethod
    def parse_frame(cls, raw_frame: bytes) -> Tuple[Dict[str, int], bytes, bool]:
        """
        Parses a raw frame back into its components and validates the CRC32 checksum.
        """
        if len(raw_frame) < cls.HEADER_SIZE + cls.CRC_SIZE:
            raise ValueError("Frame is too short to contain a valid header and CRC.")
            
        # Extract Header
        header_bytes = raw_frame[:cls.HEADER_SIZE]
        frame_id, payload_len, rs_profile_idx = struct.unpack(cls.HEADER_FORMAT, header_bytes)
        
        header_dict = {
            'frame_id': frame_id,
            'payload_len': payload_len,
            'rs_profile_idx': rs_profile_idx
        }
        
        # Extract Payload and CRC32
        payload = raw_frame[cls.HEADER_SIZE : cls.HEADER_SIZE + payload_len]
        received_crc_bytes = raw_frame[cls.HEADER_SIZE + payload_len : cls.HEADER_SIZE + payload_len + cls.CRC_SIZE]
        
        if len(received_crc_bytes) != cls.CRC_SIZE:
            return header_dict, b"", False
            
        received_crc_val = struct.unpack('>I', received_crc_bytes)[0]
        
        # Re-calculate CRC32
        calculated_crc_val = zlib.crc32(payload) & 0xFFFFFFFF
        is_crc_valid = (received_crc_val == calculated_crc_val)
        
        return header_dict, payload, is_crc_valid
