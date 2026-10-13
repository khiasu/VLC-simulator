import streamlit as st
import datetime
import uuid
import time
import json
import os
import io
import ast
import zipfile
import numpy as np
import pandas as pd

from config import SystemConfig

def build_experiment_metadata(seed: int, controller_type: str, thresholds_version: str) -> dict:
    """
    Captures exact provenance of the experiment for strict reproducibility.
    This will be saved as a separate JSON to avoid polluting the CSV structure.
    """
    return {
        "experiment_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now().isoformat(),
        "simulator_version": "1.0.0",
        "random_seed": seed,
        "controller_type": controller_type,
        "thresholds_version": thresholds_version,
        "channel_parameters": {
            "csk_constellation": "4-CSK",
            "payload_size_bytes": SystemConfig.DEFAULT_PAYLOAD_SIZE,
            "header_size_bytes": SystemConfig.HEADER_SIZE,
            "crc_size_bytes": 4
        },
        "rs_profiles": [str(p) for p in SystemConfig.RS_PROFILES]
    }

def render_dashboard():
    # ---------------------------------------------------------
    # Setup page configuration
    # ---------------------------------------------------------
    st.set_page_config(page_title="VLC Simulator Research Workbench", layout="wide")

    # ---------------------------------------------------------
    # Sidebar Controls
    # ---------------------------------------------------------
    st.sidebar.title("VLC Control Panel")

    # Ensure session state variables exist
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False

    mode = st.sidebar.selectbox(
        "Mode Selector",
        ['Live Simulation', 'Multi-Baseline Benchmark', 'Log-Driven Replay Mode']
    )

    st.sidebar.markdown("---")
    st.sidebar.header("Channel Parameters")
    base_snr = st.sidebar.slider("Base SNR (dB)", 0.0, 25.0, 15.0, 0.5)
    dimming = st.sidebar.slider("LED Dimming", 0.1, 1.0, 1.0, 0.1)
    crosstalk = st.sidebar.slider("Crosstalk", 0.0, 0.3, 0.0, 0.05)
    random_seed = st.sidebar.number_input("Random Seed", value=42, step=1)

    st.sidebar.markdown("---")
    st.sidebar.header("System Settings")
    controller_type = st.sidebar.selectbox(
        "Controller Selector",
        ['Adaptive RS', 'Static Strong (255, 223)', 'Static Medium (255, 239)', 'Static Weak (255, 251)', 'Uncoded']
    )
    render_throttle = st.sidebar.slider("Render Throttling Interval (frames)", 1, 50, 10, 1)

    # Control Buttons
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.is_running = True
    with col2:
        if st.button("⏹ Stop", use_container_width=True):
            st.session_state.is_running = False

    # ---------------------------------------------------------
    # Top KPI Metrics Row (Placeholders)
    # ---------------------------------------------------------
    st.title("VLC Simulator Research Workbench")

    # Experiment Status Banner
    status_col, progress_col = st.columns([1, 3])
    with status_col:
        status_text = st.empty()
        if st.session_state.is_running:
            status_text.info("Status: **Running**")
        else:
            status_text.success("Status: **Idle**")
            
    with progress_col:
        progress_bar = st.empty()
        # Initialize with 0%
        progress_bar.progress(0, text="Ready")

    st.markdown("### Real-Time Metrics")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

    # We use st.empty() placeholders so we can update them in a loop without re-rendering the whole page
    metric_snr = kpi1.empty()
    metric_profile = kpi2.empty()
    metric_fer = kpi3.empty()
    metric_ber = kpi4.empty()
    metric_goodput = kpi5.empty()
    metric_crc = kpi6.empty()

    def update_kpis(snr: float, profile: str, fer: float, ber: float, goodput: float, crc_pass: bool):
        """Updates the lightweight KPI metric cards."""
        metric_snr.metric("Current SNR (dB)", f"{snr:.1f}")
        metric_profile.metric("Active RS Profile", profile)
        metric_fer.metric("FER", f"{fer:.2f}")
        metric_ber.metric("BER", f"{ber:.2e}")
        metric_goodput.metric("Goodput (kbps)", f"{goodput:.0f}")
        
        # Custom colored HTML for CRC status
        crc_color = "#00cc44" if crc_pass else "#ff3333"
        crc_str = "PASS" if crc_pass else "FAIL"
        metric_crc.markdown(f"**CRC Status**<br/><span style='color:{crc_color}; font-size: 24px; font-weight: bold;'>{crc_str}</span>", unsafe_allow_html=True)

    # Initial empty state for the UI
    update_kpis(0.0, "N/A", 0.0, 0.0, 0.0, True)

    # ---------------------------------------------------------
    # Dynamic Plot Layout
    # ---------------------------------------------------------
    st.markdown("---")
    col_chart, col_side = st.columns([3, 1])

    with col_chart:
        st.markdown("### Performance Overview")
        main_chart_placeholder = st.empty()
        
    with col_side:
        st.markdown("### Adaptation Thresholds")
        threshold_gauge_placeholder = st.empty()
        
        st.markdown("### 4-CSK Constellation")
        constellation_plot_placeholder = st.empty()

    st.markdown("---")
    decision_console_placeholder = st.empty()

    # Initialize session state for rolling window data
    if 'df_history' not in st.session_state:
        st.session_state.df_history = pd.DataFrame(columns=[
            'frame_idx', 'strategy', 'true_snr', 'estimated_snr', 
            'fer', 'ber', 'goodput'
        ])
    if 'event_logs' not in st.session_state:
        st.session_state.event_logs = []

    # ---------------------------------------------------------
    # Live Simulation Loop
    # ---------------------------------------------------------
    if mode == 'Live Simulation':
        from plots import render_performance_charts, render_constellation_scatter, render_threshold_state
        from analytics import render_decision_console
        from simulation_runner import SimulationRunner
        from adaptive_controller import AdaptiveLinkController
        from channel_quality_estimator import ChannelQualityEstimator

        runner = SimulationRunner()
        adaptive_controller = AdaptiveLinkController()
        quality_estimator = ChannelQualityEstimator()
        
        try:
            with open("adaptive_thresholds.json", 'r') as f:
                thresholds = json.load(f)
        except FileNotFoundError:
            thresholds = {}

        current_profile_idx = 0
        frame_idx = 0
        last_tx_symbols = None
        last_rx_symbols = None
        
        # We use a while loop inside the script for real-time updates
        while st.session_state.is_running:
            frame_idx += 1
            
            # Add bounded random walk to the base SNR selected in sidebar
            noise = np.random.normal(0, 0.5)
            current_snr = base_snr + noise
            
            channel_state = quality_estimator.get_channel_state()
            active_profile, current_profile_idx, decision_trace = adaptive_controller.select_rs_profile(channel_state, current_profile_idx)
            
            # Run physical layer frame with debug data for constellation rendering
            res = runner.run_single_frame(snr_db=current_snr, rs_profile=active_profile, dimming=dimming, return_debug_data=True)
            last_tx_symbols = res.get('tx_symbols')
            last_rx_symbols = res.get('rx_symbols')
            
            crc_pass = (res['fer'] == 0)
            quality_estimator.update_link_history(frame_idx, crc_pass, res['corrected_symbols'], current_snr)
            
            # Check for adaptation events
            if "[UPGRADE]" in decision_trace or "[DOWNGRADE]" in decision_trace or "[ESCALATION]" in decision_trace:
                st.session_state.event_logs.append({
                    'frame_idx': frame_idx,
                    'type': decision_trace.split("]")[0].strip("["),
                    'trace': decision_trace
                })
                
            # Append to DataFrame
            new_row = {
                'frame_idx': frame_idx,
                'strategy': 'Adaptive_RS',
                'true_snr': current_snr,
                'estimated_snr': current_snr,
                'fer': res['fer'],
                'ber': res['ber'],
                'goodput': res['goodput_kbps']
            }
            st.session_state.df_history.loc[len(st.session_state.df_history)] = new_row
            
            # Enforce Rolling Window (Prevent Memory Leaks & Lag)
            if len(st.session_state.df_history) > 200:
                st.session_state.df_history = st.session_state.df_history.iloc[-200:]
                min_frame = st.session_state.df_history['frame_idx'].min()
                st.session_state.event_logs = [e for e in st.session_state.event_logs if e['frame_idx'] >= min_frame]
                
            # 1. Update lightweight KPIs EVERY frame
            update_kpis(current_snr, str(active_profile), res['fer'], res['ber'], res['goodput_kbps'], crc_pass)
            progress_bar.progress((frame_idx % 100) / 100, text=f"Live Simulating Frame {frame_idx}...")
            
            # 2. Render Throttling: Update heavy Plotly charts ONLY every N frames
            if frame_idx % render_throttle == 0:
                fig_main = render_performance_charts(st.session_state.df_history, st.session_state.event_logs)
                main_chart_placeholder.plotly_chart(fig_main, use_container_width=True, key=f"main_{frame_idx}")
                
                fig_gauge = render_threshold_state(current_snr, thresholds)
                threshold_gauge_placeholder.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{frame_idx}")
                
                # Constellation Scatter using real symbols
                if last_tx_symbols is not None and last_rx_symbols is not None:
                    fig_scatter = render_constellation_scatter(last_tx_symbols[:60], last_rx_symbols[:60])
                else:
                    ref_pts = np.array(list(SystemConfig.CSK_4_MAP.values()))
                    fig_scatter = render_constellation_scatter(ref_pts, ref_pts)
                constellation_plot_placeholder.plotly_chart(fig_scatter, use_container_width=True, key=f"scatter_{frame_idx}")
                
                # Decision Trace Console
                console_html = render_decision_console(st.session_state.event_logs)
                decision_console_placeholder.markdown(console_html, unsafe_allow_html=True)
                
            time.sleep(0.05) # Prevent UI thread lock

        # If the simulation is stopped, retain the graphs based on historical data
        if not st.session_state.is_running and not st.session_state.df_history.empty:
            fig_main = render_performance_charts(st.session_state.df_history, st.session_state.event_logs)
            main_chart_placeholder.plotly_chart(fig_main, use_container_width=True, key="main_stopped")
            
            last_snr = st.session_state.df_history.iloc[-1]['true_snr']
            fig_gauge = render_threshold_state(last_snr, thresholds)
            threshold_gauge_placeholder.plotly_chart(fig_gauge, use_container_width=True, key="gauge_stopped")
            
            ref_pts = np.array(list(SystemConfig.CSK_4_MAP.values()))
            fig_scatter = render_constellation_scatter(ref_pts, ref_pts)
            constellation_plot_placeholder.plotly_chart(fig_scatter, use_container_width=True, key="scatter_stopped")
            
            console_html = render_decision_console(st.session_state.event_logs)
            decision_console_placeholder.markdown(console_html, unsafe_allow_html=True)
            
            # Update KPIs to last known state
            last_row = st.session_state.df_history.iloc[-1]
            update_kpis(last_row['true_snr'], "Stopped", last_row['fer'], last_row['ber'], last_row['goodput'], last_row['fer']==0)

    # ---------------------------------------------------------
    # Multi-Baseline Benchmark Mode
    # ---------------------------------------------------------
    elif mode == 'Multi-Baseline Benchmark':
        from analytics import render_statistical_summary_page
        
        st.markdown("---")
        st.info("Run the `experiments.py` script in your terminal to generate the benchmark data, then click refresh.")
        
        if st.button("Refresh Benchmark Results"):
            pass # Streamlit reruns on button click
            
        if os.path.exists("statistical_summary.csv"):
            if os.path.exists("frame_level_logs.csv"):
                df_multi = pd.read_csv("frame_level_logs.csv")
                render_statistical_summary_page(df_multi)
            else:
                st.error("Missing frame_level_logs.csv")
        else:
            st.warning("No benchmark data found. Run experiments.py first.")

    # ---------------------------------------------------------
    # Log-Driven Replay Mode
    # ---------------------------------------------------------
    elif mode == 'Log-Driven Replay Mode':
        st.markdown("### ⏪ Log-Driven Replay Mode")
        st.info("Re-simulate and inspect exact frames from past experiments to guarantee 100% reproducibility.")
        
        # 1. File Loader & Export Engine
        col_up, col_down = st.columns(2)
        with col_up:
            uploaded_file = st.file_uploader("Upload frame_level_logs.csv", type=['csv'])
        
        with col_down:
            st.markdown("#### Export Current Workspace")
            
            if os.path.exists("frame_level_logs.csv") and os.path.exists("statistical_summary.csv"):
                # Bundle into a zip for the "Compact Benchmark Export" feature
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w") as z:
                    z.write("frame_level_logs.csv")
                    z.write("statistical_summary.csv")
                    if os.path.exists("adaptive_thresholds.json"):
                        z.write("adaptive_thresholds.json")
                
                st.download_button(
                    label="📥 Download Full Benchmark Bundle (ZIP)",
                    data=buf.getvalue(),
                    file_name="vlc_benchmark_export.zip",
                    mime="application/zip"
                )
            else:
                st.warning("No benchmark data available to export.")
                
        # 2. Frame Scrubbing Inspector
        if uploaded_file is not None:
            replay_df = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(replay_df)} frames from log file!")
            
            st.markdown("---")
            target_frame = st.slider(
                "Select Frame Index to Inspect", 
                min_value=int(replay_df['frame_idx'].min()), 
                max_value=int(replay_df['frame_idx'].max()), 
                value=int(replay_df['frame_idx'].min())
            )
            
            frame_data = replay_df[replay_df['frame_idx'] == target_frame].iloc[0]
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Frame ID", target_frame)
            k2.metric("True SNR", f"{frame_data['true_snr']} dB")
            k3.metric("Profile Selected", frame_data['profile'])
            k4.metric("CRC Status", "PASS" if frame_data['fer'] == 0 else "FAIL", 
                      delta="OK" if frame_data['fer'] == 0 else "ERROR", 
                      delta_color="normal" if frame_data['fer'] == 0 else "inverse")
            
            # 3. Symbol-Level Inspection (Re-simulation)
            st.markdown("#### Symbol & Byte Level Inspection")
            if st.button(f"Re-simulate Frame {target_frame} for Byte Extraction"):
                from simulation_runner import SimulationRunner
                
                # Perfectly re-simulate this exact frame to extract byte data
                trial_seed = int(frame_data['seed'])
                np.random.seed(trial_seed + int(target_frame))
                
                runner = SimulationRunner()
                try:
                    prof = ast.literal_eval(frame_data['profile'])
                except Exception:
                    prof = frame_data['profile']
                    
                res = runner.run_single_frame(
                    snr_db=float(frame_data['true_snr']), 
                    rs_profile=prof,
                    return_debug_data=True
                )
                
                st.success("Re-simulation completed perfectly using Seed offset.")
                
                # Show Byte Comparison Table
                tx_b = res['tx_bytes']
                rx_b = res.get('rx_bytes', bytearray())
                
                # Display first 20 bytes to prevent UI lag
                display_len = min(20, len(tx_b))
                byte_df = pd.DataFrame({
                    'Index': range(display_len),
                    'Original TX Byte (Hex)': [hex(b) for b in tx_b[:display_len]],
                    'Recovered RX Byte (Hex)': [hex(b) if i < len(rx_b) else "MISSING" for i, b in enumerate(tx_b[:display_len])]
                })
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Payload Byte Extraction (First 20 bytes)**")
                    st.dataframe(byte_df, use_container_width=True, hide_index=True)
                    
                with c2:
                    st.markdown("**Re-simulated Constellation Scatter**")
                    from plots import render_constellation_scatter
                    fig = render_constellation_scatter(res['tx_symbols'], res['rx_symbols'])
                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    render_dashboard()
