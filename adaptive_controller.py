import json
from typing import Tuple, Union, Dict
from config import SystemConfig

class AdaptiveLinkController:
    """
    Rule-based decision engine that dynamically selects the optimal 
    Reed-Solomon profile based on estimated channel conditions and data-driven thresholds.
    """
    def __init__(self, thresholds_json: str = "adaptive_thresholds.json"):
        with open(thresholds_json, 'r') as f:
            self.thresholds = json.load(f)
            
        self.profiles = SystemConfig.RS_PROFILES
        self.HYSTERESIS = 0.5 # +/- 0.5 dB margin to prevent "ping-ponging" between codes

    def select_rs_profile(self, channel_state: Dict, current_profile_idx: int) -> Tuple[Union[Tuple[int, int], str], int, str]:
        """
        Evaluates the channel state and decides whether to maintain, upgrade, or downgrade the RS profile.
        Returns: (selected_profile, profile_idx, decision_trace_string)
        """
        avg_snr_db = channel_state.get('avg_snr_db', 0.0)
        recent_fer = channel_state.get('recent_fer', 0.0)
        avg_corrections = channel_state.get('avg_corrections', 0.0)
        crc_failure_streak = channel_state.get('crc_failure_streak', 0)
        
        current_profile = self.profiles[current_profile_idx]
        current_p_str = str(current_profile)
        
        strongest_idx = 0
        strongest_profile = self.profiles[strongest_idx]

        # Formatting helper for rich decision trace
        def build_trace(action, reason, new_prof, boundary, margin):
            lines = [
                f"{action} Previous RS: {current_p_str} -> New RS: {str(new_prof)}",
                f"Est. SNR: {avg_snr_db:.2f} dB | Crossover Boundary: {boundary} dB",
                f"Reason: {reason}",
                f"Hysteresis Check: SATISFIED (Margin: {margin}) | CRC Streak: {crc_failure_streak} | Avg Corrections: {avg_corrections:.1f}"
            ]
            return "\n".join(lines)

        # 1. Escalation Trigger (Emergency Fallback)
        if crc_failure_streak >= 2 or recent_fer > 0.1:
            if current_profile_idx != strongest_idx:
                trace = build_trace("[ESCALATION]", f"High error rate (fer={recent_fer:.2f}, streak={crc_failure_streak})", strongest_profile, "N/A", "N/A (Bypassed)")
                return strongest_profile, strongest_idx, trace
            else:
                return strongest_profile, strongest_idx, "[MAINTAIN] Already at maximum protection despite poor channel."

        # 2. Can we UPGRADE?
        for idx in range(len(self.profiles) - 1, current_profile_idx, -1):
            p_str = str(self.profiles[idx])
            threshold = self.thresholds.get(p_str, 999.0)
            if threshold != 999.0 and avg_snr_db >= threshold + self.HYSTERESIS:
                trace = build_trace("[UPGRADE]", "SNR safely cleared threshold + hysteresis margin", p_str, threshold, f"+{self.HYSTERESIS} dB")
                return self.profiles[idx], idx, trace

        # 3. Can we MAINTAIN?
        current_threshold = self.thresholds.get(current_p_str, 999.0)
        if current_threshold != 999.0 and avg_snr_db >= current_threshold - self.HYSTERESIS:
            return current_profile, current_profile_idx, "[MAINTAIN] Channel conditions stable within hysteresis margins."

        # 4. We must DOWNGRADE
        for idx in range(current_profile_idx - 1, -1, -1):
            p_str = str(self.profiles[idx])
            threshold = self.thresholds.get(p_str, 999.0)
            if threshold != 999.0 and avg_snr_db >= threshold:
                trace = build_trace("[DOWNGRADE]", "SNR dropped below safe operating margin", p_str, threshold, f"-{self.HYSTERESIS} dB")
                return self.profiles[idx], idx, trace
                
        # 5. Ultimate Fallback
        trace = build_trace("[FALLBACK]", "Catastrophic channel failure", strongest_profile, "N/A", "N/A")
        return strongest_profile, strongest_idx, trace
