import os
import json
import numpy as np
from typing import Dict

from config import SystemConfig
from simulation_runner import SimulationRunner

class ThresholdFinder:
    """
    Offline calibration tool to mathematically derive data-driven Reed-Solomon 
    crossover points based on empirical simulation data.
    """
    def __init__(self):
        self.runner = SimulationRunner()
        self.profiles = SystemConfig.RS_PROFILES

    def run_calibration_sweep(self, snr_min: float = 0.0, snr_max: float = 25.0, step: float = 0.5, frames_per_step: int = 100) -> Dict:
        """
        Runs batch simulations across the full SNR sweep to collect performance data.
        """
        # Create array of SNR values to test (inclusive of max)
        snr_range = np.arange(snr_min, snr_max + step, step)
        
        print(f"Starting Calibration Sweep from {snr_min} dB to {snr_max} dB (step {step} dB)...")
        print(f"This will simulate thousands of frames to find the exact crossover points.")
        
        # We reuse the Phase 4 batch runner!
        results = self.runner.run_batch_experiment(list(snr_range), self.profiles, frames_per_snr=frames_per_step)
        
        # Aggregate results
        aggregated = {}
        for snr in snr_range:
            aggregated[snr] = {}
            for profile in self.profiles:
                aggregated[snr][str(profile)] = {'fer': [], 'goodput': []}
                
        for r in results:
            snr = r['snr_db']
            profile_str = r['rs_profile']
            aggregated[snr][profile_str]['fer'].append(r['fer'])
            aggregated[snr][profile_str]['goodput'].append(r['goodput_kbps'])
            
        # Calculate mean metrics for each SNR and Profile combination
        sweep_data = {}
        for snr in snr_range:
            sweep_data[snr] = {}
            for profile in self.profiles:
                p_str = str(profile)
                sweep_data[snr][p_str] = {
                    'mean_fer': float(np.mean(aggregated[snr][p_str]['fer'])),
                    'mean_goodput': float(np.mean(aggregated[snr][p_str]['goodput']))
                }
                
        return sweep_data

    def derive_and_cache_policy(self, sweep_data: Dict, target_fer: float = 1e-2, output_json: str = "adaptive_thresholds.json"):
        """
        Scans simulation data to locate exact SNR crossover boundaries where a lighter RS code 
        first yields higher Goodput while satisfying FER <= target_fer.
        """
        optimal_profiles = {}
        sorted_snrs = sorted(list(sweep_data.keys()))
        
        # Step 1: Find the absolute best profile for every single SNR step
        for snr in sorted_snrs:
            data = sweep_data[snr]
            valid_profiles = []
            
            # Which profiles satisfy the FER constraint?
            for p_str, metrics in data.items():
                if metrics['mean_fer'] <= target_fer:
                    valid_profiles.append((p_str, metrics['mean_goodput']))
                    
            if not valid_profiles:
                # If it's so noisy that NONE satisfy the FER target, default to the strongest protection
                best_profile = str(self.profiles[0]) # Assumes first in list is (255, 223)
            else:
                # Of the ones that passed, pick the one with the highest Goodput
                valid_profiles.sort(key=lambda x: x[1], reverse=True)
                best_profile = valid_profiles[0][0]
                
            optimal_profiles[snr] = best_profile

        # Step 2: Derive the Minimum SNR threshold required to activate each profile
        thresholds = {}
        for p in self.profiles:
            thresholds[str(p)] = float('inf') # Default to infinity (unreachable)
            
        # The strongest profile is our fallback, so it requires no minimum SNR (-infinity)
        strongest = str(self.profiles[0])
        thresholds[strongest] = float('-inf')
        
        # Scan through SNRs and log the lowest SNR where a profile became the optimal choice
        for snr in sorted_snrs:
            best_p = optimal_profiles[snr]
            if snr < thresholds[best_p]:
                thresholds[best_p] = snr
                
        # Clean up output for JSON serialization (infinity to a string or very high number)
        # We will use 999.0 for infinity so the JSON is valid and easily parsed by the controller
        for p_str in thresholds:
            if thresholds[p_str] == float('inf'):
                thresholds[p_str] = 999.0
            elif thresholds[p_str] == float('-inf'):
                thresholds[p_str] = -999.0
                
        print("\n=== Derived Data-Driven Crossover Boundaries ===")
        for p_str, min_snr in thresholds.items():
            if min_snr == 999.0:
                print(f"{p_str:<15} : Never optimal in this SNR range")
            elif min_snr == -999.0:
                print(f"{p_str:<15} : Fallback profile (Always active if others fail)")
            else:
                print(f"{p_str:<15} : Becomes optimal at SNR >= {min_snr:.1f} dB")
            
        # Export to JSON
        with open(output_json, 'w') as f:
            json.dump(thresholds, f, indent=4)
            
        print(f"\nPolicy successfully cached to {output_json}")


if __name__ == '__main__':
    json_path = "adaptive_thresholds.json"
    
    if not os.path.exists(json_path):
        finder = ThresholdFinder()
        # For standard execution, we sweep from 5 dB to 25 dB
        # We use 20 frames per step to balance statistical validity with execution time (takes ~2 minutes)
        sweep_data = finder.run_calibration_sweep(snr_min=5.0, snr_max=25.0, step=0.5, frames_per_step=20)
        
        finder.derive_and_cache_policy(sweep_data, target_fer=SystemConfig.TARGET_FER, output_json=json_path)
    else:
        print(f"[{json_path}] already exists. Calibration bypassed. Delete the file to recalibrate.")
