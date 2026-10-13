import csv
import time
import numpy as np
from typing import Union, Tuple, List, Dict

from config import SystemConfig
from bitstream import generate_random_bytes, bytes_to_bit_array, bit_array_to_bytes
from frame import FrameManager
from rs_codec import RSCodecManager
from csk_mapper import CSKMapper
from optical_channel import OpticalChannel

class SimulationRunner:
    """
    Unified execution and metrics engine for the VLC simulator.
    """
    def __init__(self):
        self.rs_manager = RSCodecManager()
        self.frame_counter = 0

    def run_single_frame(self, snr_db: float, rs_profile: Union[Tuple[int, int], str], dimming: float = 1.0, return_debug_data: bool = False) -> Dict:
        """
        Executes the full pipeline for a single frame.
        """
        self.frame_counter += 1
        frame_id = self.frame_counter
        
        # 1. Generate Data
        payload_bytes = generate_random_bytes(SystemConfig.DEFAULT_PAYLOAD_SIZE)
        
        # 2. Build Frame + CRC32
        frame_bytes = FrameManager.build_frame(frame_id, payload_bytes, rs_profile_idx=0)
        
        # 3. RS Encode
        encoded_bytes = self.rs_manager.encode_frame(frame_bytes, rs_profile)
        
        # 4. 4-CSK Map
        tx_bits = bytes_to_bit_array(encoded_bytes)
        tx_symbols = CSKMapper.map_bits_to_csk(tx_bits)
        
        # 5. Optical Channel
        SYMBOL_RATE = 1e6
        tx_duration_sec = len(tx_symbols) / SYMBOL_RATE
        
        rx_symbols = OpticalChannel.transmit(tx_symbols, snr_db, dimming)
        
        # 6. 4-CSK Demap
        rx_bits = CSKMapper.demap_csk_to_bits(rx_symbols)
        
        # Truncate rx_bits if padded
        rx_bits = rx_bits[:len(tx_bits)]
        
        # Calculate BER
        bit_errors = np.sum(tx_bits != rx_bits)
        ber = bit_errors / len(tx_bits) if len(tx_bits) > 0 else 0
        
        rx_encoded_bytes = bit_array_to_bytes(rx_bits)
        
        # 7. RS Decode
        recovered_frame_bytes, corrected_symbols, decode_success = self.rs_manager.decode_frame(rx_encoded_bytes, rs_profile)
        
        # 8. Header Unpack & CRC32 Verify
        fer = 1 # Default to error (fail)
        goodput_kbps = 0.0
        parsed_payload = bytearray()
        
        if decode_success:
            try:
                header, parsed_payload, is_crc_valid = FrameManager.parse_frame(recovered_frame_bytes)
                if is_crc_valid:
                    fer = 0
                    goodput_kbps = (len(parsed_payload) * 8) / tx_duration_sec / 1000.0
            except ValueError:
                pass
                
        throughput_kbps = (len(tx_bits)) / tx_duration_sec / 1000.0
        
        res = {
            'frame_id': frame_id,
            'snr_db': snr_db,
            'rs_profile': str(rs_profile),
            'ber': ber,
            'fer': fer,
            'goodput_kbps': goodput_kbps,
            'throughput_kbps': throughput_kbps,
            'corrected_symbols': corrected_symbols
        }
        
        if return_debug_data:
            res['tx_bytes'] = payload_bytes
            res['rx_bytes'] = parsed_payload
            res['tx_symbols'] = tx_symbols
            res['rx_symbols'] = rx_symbols
            
        return res

    def run_batch_experiment(self, snr_range: List[float], rs_profiles: List, frames_per_snr: int = 50) -> List[Dict]:
        """
        Iterates over SNR values and RS profiles to run batch simulations.
        """
        results = []
        total_runs = len(snr_range) * len(rs_profiles) * frames_per_snr
        current_run = 0
        
        for snr in snr_range:
            for profile in rs_profiles:
                for _ in range(frames_per_snr):
                    res = self.run_single_frame(snr, profile)
                    results.append(res)
                    
                    current_run += 1
                    if current_run % 100 == 0:
                        print(f"Progress: {current_run}/{total_runs} frames simulated...")
                        
        return results

if __name__ == '__main__':
    runner = SimulationRunner()
    
    # Test batch parameters
    snr_range = [5, 10, 15, 20]
    rs_profiles = SystemConfig.RS_PROFILES
    frames_per_snr = 20 # Using 20 for a quick but meaningful test batch
    
    print("Starting Batch Experiment Engine...")
    results = runner.run_batch_experiment(snr_range, rs_profiles, frames_per_snr)
    
    # Aggregate results for the ASCII table
    aggregated = {}
    for r in results:
        key = (r['snr_db'], r['rs_profile'])
        if key not in aggregated:
            aggregated[key] = {'ber': [], 'fer': [], 'goodput': []}
        aggregated[key]['ber'].append(r['ber'])
        aggregated[key]['fer'].append(r['fer'])
        aggregated[key]['goodput'].append(r['goodput_kbps'])
        
    print("\n" + "="*75)
    print(" "*25 + "SIMULATION RESULTS SUMMARY")
    print("="*75)
    print(f"{'SNR (dB)':<10} | {'RS Profile':<15} | {'Mean BER':<12} | {'Mean FER':<10} | {'Goodput (kbps)':<15}")
    print("-" * 75)
    
    for snr in snr_range:
        for profile in rs_profiles:
            key = (snr, str(profile))
            mean_ber = np.mean(aggregated[key]['ber'])
            mean_fer = np.mean(aggregated[key]['fer'])
            mean_gp = np.mean(aggregated[key]['goodput'])
            
            print(f"{snr:<10} | {str(profile):<15} | {mean_ber:<12.4e} | {mean_fer:<10.2f} | {mean_gp:<15.2f}")
            
    # Export to CSV
    csv_file = 'simulation_results.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print("="*75)
    print(f"Results successfully exported to {csv_file}")
