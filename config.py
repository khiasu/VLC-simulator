from dataclasses import dataclass
from typing import ClassVar, List, Tuple, Dict, Union

@dataclass
class SystemConfig:
    """
    Central configuration holding system-wide constants for the VLC Simulator.
    """
    # Generic (N, K) Reed-Solomon profiles over GF(2^8)
    RS_PROFILES: ClassVar[List[Union[Tuple[int, int], str]]] = [
        (255, 223),
        (255, 239),
        (255, 247),
        (255, 251),
        "UNCODED"
    ]
    
    # Default payload size per frame (in bytes)
    DEFAULT_PAYLOAD_SIZE: ClassVar[int] = 200
    
    # Size of the explicit frame header (in bytes)
    HEADER_SIZE: ClassVar[int] = 8
    
    # 4-CSK Constellation Mapping (IEEE 802.15.7 style)
    # Maps 2-bit strings to normalized RGB intensity vectors [R, G, B] such that R+G+B = 1.0
    CSK_4_MAP: ClassVar[Dict[str, List[float]]] = {
        '00': [1.0, 0.0, 0.0],       # Red
        '01': [0.0, 1.0, 0.0],       # Green
        '10': [0.0, 0.0, 1.0],       # Blue
        '11': [1/3, 1/3, 1/3]        # White/Neutral, equal power distribution
    }
    
    # Target Frame Error Rate (FER)
    TARGET_FER: ClassVar[float] = 1e-2
