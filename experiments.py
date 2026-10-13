import csv
import numpy as np
from typing import Dict, Tuple, List

from config import SystemConfig
from simulation_runner import SimulationRunner
from channel_quality_estimator import ChannelQualityEstimator
from adaptive_controller import AdaptiveLinkController

class AdaptiveExperimentRunner:
    """
    Evaluates the Adaptive Controller against static RS baselines across 
    dynamic channel conditions and multiple random seeds.
    """
    def __init__(self):
        self.runner = SimulationRunner()
        
    def generate_snr_trace(self, num_frames: int, seed: int) -> np.ndarray:
        """
        Generates a dynamic SNR trace that fluctuates smoothly between 5 dB and 22 dB
        using a bounded random walk.
        """
        np.random.seed(seed)
        
        snr = np.random.uniform(5.0, 22.0)
        trace = []
        for _ in range(num_frames):
            step = np.random.normal(0, 1.5) # SNR step variance
            snr += step
            # Bounding limits to realistic ranges
            if snr > 22.0: snr = 22.0 - (snr - 22.0)
            if snr < 5.0: snr = 5.0 + (5.0 - snr)
            trace.append(snr)
            
        return np.array(trace)

    def run_multi_seed_trials(self, num_seeds: int = 5, frames_per_trial: int = 300, estimation_error_std: float = 1.0) -> Tuple[Dict, List[Dict]]:
        """
        Runs the benchmark comparing Adaptive RS against Static profiles.
        Adds estimation error to simulate imperfect receiver hardware.
        """
        strategies = {
            'Static_Strong': SystemConfig.RS_PROFILES[0], # (255, 223)
            'Static_Medium': SystemConfig.RS_PROFILES[2], # (255, 247)
            'Static_Weak': SystemConfig.RS_PROFILES[-1],  # UNCODED
            'Adaptive_RS': None # Dynamically controlled
        }
        
        all_frame_logs = []
        seed_summaries = {strat: {'ber': [], 'fer': [], 'goodput': []} for strat in strategies.keys()}
        
        for seed in range(num_seeds):
            print(f"Running Benchmark Seed {seed+1}/{num_seeds}...")
            
            # 1. Generate identical physical channel conditions for all strategies
            true_snr_trace = self.generate_snr_trace(frames_per_trial, seed)
            
            # Generate estimation errors (imperfect sensors)
            np.random.seed(seed + 1000)
            estimation_errors = np.random.normal(0, estimation_error_std, frames_per_trial)
            estimated_snr_trace = true_snr_trace + estimation_errors
            
            for strat_name, static_profile in strategies.items():
                
                # Initialize state for Adaptive logic
                if strat_name == 'Adaptive_RS':
                    adaptive_controller = AdaptiveLinkController()
                    quality_estimator = ChannelQualityEstimator()
                    current_profile_idx = 0 # Always start at max protection
                    active_profile = SystemConfig.RS_PROFILES[current_profile_idx]
                else:
                    active_profile = static_profile
                    
                trial_goodput = []
                trial_fer = []
                trial_ber = []
                
                for f_idx in range(frames_per_trial):
                    true_snr = true_snr_trace[f_idx]
                    est_snr = estimated_snr_trace[f_idx]
                    
                    # A. Adaptive Decision Phase
                    decision_trace = "[STATIC_BASELINE]"
                    if strat_name == 'Adaptive_RS':
                        channel_state = quality_estimator.get_channel_state()
                        active_profile, current_profile_idx, decision_trace = adaptive_controller.select_rs_profile(channel_state, current_profile_idx)
                        
                    # B. Execute Transmission over Physical Channel
                    res = self.runner.run_single_frame(snr_db=true_snr, rs_profile=active_profile)
                    
                    # C. Update Receiver State History
                    if strat_name == 'Adaptive_RS':
                        crc_pass = (res['fer'] == 0)
                        quality_estimator.update_link_history(
                            frame_id=res['frame_id'], 
                            crc_pass=crc_pass, 
                            corrected_symbols=res['corrected_symbols'], 
                            estimated_snr=est_snr # Using the imperfect estimate!
                        )
                        
                    # D. Metrics Logging
                    trial_ber.append(res['ber'])
                    trial_fer.append(res['fer'])
                    trial_goodput.append(res['goodput_kbps'])
                    
                    all_frame_logs.append({
                        'seed': seed,
                        'frame_idx': f_idx,
                        'strategy': strat_name,
                        'true_snr': true_snr,
                        'estimated_snr': est_snr,
                        'profile': str(active_profile),
                        'ber': res['ber'],
                        'fer': res['fer'],
                        'goodput': res['goodput_kbps'],
                        'decision_trace': decision_trace
                    })
                    
                # Save the trial's mean performance
                seed_summaries[strat_name]['ber'].append(np.mean(trial_ber))
                seed_summaries[strat_name]['fer'].append(np.mean(trial_fer))
                seed_summaries[strat_name]['goodput'].append(np.mean(trial_goodput))
                
        # 2. Compute cross-seed statistical summary (Mean +/- Std Dev)
        final_stats = {}
        for strat in strategies.keys():
            final_stats[strat] = {
                'ber_mean': np.mean(seed_summaries[strat]['ber']),
                'ber_std': np.std(seed_summaries[strat]['ber']),
                'fer_mean': np.mean(seed_summaries[strat]['fer']),
                'fer_std': np.std(seed_summaries[strat]['fer']),
                'gp_mean': np.mean(seed_summaries[strat]['goodput']),
                'gp_std': np.std(seed_summaries[strat]['goodput'])
            }
            
        return final_stats, all_frame_logs

if __name__ == '__main__':
    runner = AdaptiveExperimentRunner()
    print("Starting Multi-Seed Benchmark Engine...")
    
    # We use 150 frames per trial for the execution test to ensure it finishes quickly
    final_stats, all_frame_logs = runner.run_multi_seed_trials(num_seeds=5, frames_per_trial=150, estimation_error_std=1.0)
    
    # Export Detailed Frame Logs
    with open('frame_level_logs.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_frame_logs[0].keys())
        writer.writeheader()
        writer.writerows(all_frame_logs)
        
    # Export Summary Statistics
    with open('statistical_summary.csv', 'w', newline='') as f:
        fieldnames = ['strategy', 'ber_mean', 'ber_std', 'fer_mean', 'fer_std', 'goodput_mean', 'goodput_std']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for strat, stats in final_stats.items():
            writer.writerow({
                'strategy': strat,
                'ber_mean': stats['ber_mean'],
                'ber_std': stats['ber_std'],
                'fer_mean': stats['fer_mean'],
                'fer_std': stats['fer_std'],
                'goodput_mean': stats['gp_mean'],
                'goodput_std': stats['gp_std']
            })
            
    # Print the Final Summary Table
    print("\n" + "="*85)
    print(" "*25 + "MULTI-SEED BENCHMARK RESULTS (Mean +/- Std)")
    print("="*85)
    print(f"{'Strategy':<18} | {'BER (Mean +/- Std)':<20} | {'FER (Mean +/- Std)':<20} | {'Goodput (kbps)':<20}")
    print("-" * 85)
    
    for strat, stats in final_stats.items():
        ber_str = f"{stats['ber_mean']:.2e} +/- {stats['ber_std']:.2e}"
        fer_str = f"{stats['fer_mean']:.2f} +/- {stats['fer_std']:.2f}"
        gp_str = f"{stats['gp_mean']:.0f} +/- {stats['gp_std']:.0f}"
        print(f"{strat:<18} | {ber_str:<20} | {fer_str:<20} | {gp_str:<20}")
        
    print("="*85)
    print("Exported full logs to 'frame_level_logs.csv' and 'statistical_summary.csv'")
