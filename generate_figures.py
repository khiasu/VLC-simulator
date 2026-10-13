import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from config import SystemConfig
from csk_mapper import CSKMapper
from optical_channel import OpticalChannel
from simulation_runner import SimulationRunner

# Create figures output directory
os.makedirs("figures", exist_ok=True)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 14
})

def plot_csk_constellation():
    """Figure 1: 3D 4-CSK Constellation in RGB optical intensity space."""
    fig = plt.figure(figsize=(8, 7), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    
    # 4-CSK Reference points
    csk_points = {
        "'00' (Red)": np.array([1.0, 0.0, 0.0]),
        "'01' (Green)": np.array([0.0, 1.0, 0.0]),
        "'10' (Blue)": np.array([0.0, 0.0, 1.0]),
        "'11' (White)": np.array([1.0/3.0, 1.0/3.0, 1.0/3.0])
    }
    
    # Generate noisy symbols around points at 15 dB SNR
    np.random.seed(42)
    symbols = []
    for pt in csk_points.values():
        symbols.extend([pt] * 60)
    symbols = np.array(symbols)
    noisy_symbols = OpticalChannel.transmit(symbols, snr_db=16.0, dimming_factor=1.0)
    
    # Scatter noisy received symbols
    ax.scatter(noisy_symbols[:, 0], noisy_symbols[:, 1], noisy_symbols[:, 2], 
               color='gray', alpha=0.35, s=20, label='Received Symbols (16 dB SNR)')
    
    # Plot ideal anchors
    point_colors = {'Red': '#e60000', 'Green': '#009933', 'Blue': '#0066cc', 'White': '#888888'}
    for name, pt in csk_points.items():
        col_key = name.split('(')[1].strip(')')
        c = point_colors.get(col_key, 'black')
        ax.scatter([pt[0]], [pt[1]], [pt[2]], color=c, s=140, edgecolors='black', linewidth=1.5, label=f"Ideal {name}")
        ax.text(pt[0] + 0.03, pt[1] + 0.03, pt[2] + 0.03, name, fontsize=10, fontweight='bold', color=c)
        
    # Constant optical power plane R + G + B = 1.0
    u = np.linspace(0, 1, 10)
    v = np.linspace(0, 1, 10)
    U, V = np.meshgrid(u, v)
    W = 1.0 - U - V
    W[W < 0] = np.nan
    ax.plot_wireframe(U, V, W, color='cyan', alpha=0.15, linewidth=0.8)
    
    ax.set_xlabel('Normalized Red ($I_R$)', labelpad=10)
    ax.set_ylabel('Normalized Green ($I_G$)', labelpad=10)
    ax.set_zlabel('Normalized Blue ($I_B$)', labelpad=10)
    ax.set_title(r'IEEE 802.15.7 4-CSK Constellation in RGB Space ($\sum I = 1.0$)', pad=15, fontweight='bold')
    ax.set_xlim([0, 1.1])
    ax.set_ylim([0, 1.1])
    ax.set_zlim([0, 1.1])
    ax.legend(loc='upper right', frameon=True, fontsize=9)
    plt.tight_layout()
    plt.savefig('figures/fig1_csk_constellation_3d.png', dpi=300)
    plt.close()
    print("Saved: figures/fig1_csk_constellation_3d.png")

def plot_ber_and_goodput_crossover():
    """Figure 2 & 3: BER vs SNR and Goodput vs SNR with crossover boundaries."""
    runner = SimulationRunner()
    snr_range = np.arange(6.0, 24.5, 1.0)
    profiles = SystemConfig.RS_PROFILES
    frames_per_pt = 30
    
    results = runner.run_batch_experiment(list(snr_range), profiles, frames_per_snr=frames_per_pt)
    df = pd.DataFrame(results)
    
    grouped = df.groupby(['snr_db', 'rs_profile']).agg({
        'ber': 'mean',
        'fer': 'mean',
        'goodput_kbps': 'mean'
    }).reset_index()
    
    # ----------------- Fig 2: BER vs SNR -----------------
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)
    profile_palette = {
        str((255, 223)): ('#e60000', 'o-', 'RS(255, 223) [t=16]'),
        str((255, 239)): ('#ff8000', 's-', 'RS(255, 239) [t=8]'),
        str((255, 247)): ('#0099ff', '^-', 'RS(255, 247) [t=4]'),
        str((255, 251)): ('#9933ff', 'd-', 'RS(255, 251) [t=2]'),
        'UNCODED': ('#555555', 'x--', 'UNCODED [t=0]')
    }
    
    for p in profiles:
        p_str = str(p)
        sub = grouped[grouped['rs_profile'] == p_str]
        color, marker, label = profile_palette.get(p_str, ('black', 'o-', p_str))
        ax.semilogy(sub['snr_db'], np.maximum(sub['ber'], 1e-5), marker, color=color, label=label, linewidth=1.8, markersize=5)
        
    ax.set_xlabel('Channel SNR (dB)', fontweight='bold')
    ax.set_ylabel('Bit Error Rate (BER)', fontweight='bold')
    ax.set_title('Bit Error Rate vs. SNR across Reed-Solomon Coding Profiles', fontweight='bold', pad=12)
    ax.set_ylim([1e-4, 0.5])
    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.legend(loc='lower left', frameon=True)
    plt.tight_layout()
    plt.savefig('figures/fig2_ber_vs_snr.png', dpi=300)
    plt.close()
    print("Saved: figures/fig2_ber_vs_snr.png")

    # ----------------- Fig 3: Goodput vs SNR with Crossover -----------------
    fig, ax = plt.subplots(figsize=(9, 5.8), dpi=300)
    for p in profiles:
        p_str = str(p)
        sub = grouped[grouped['rs_profile'] == p_str]
        color, marker, label = profile_palette.get(p_str, ('black', 'o-', p_str))
        ax.plot(sub['snr_db'], sub['goodput_kbps'], marker, color=color, label=label, linewidth=1.8, markersize=5)
        
    # Read calibrated thresholds if available
    if os.path.exists('adaptive_thresholds.json'):
        with open('adaptive_thresholds.json') as f:
            th = json.load(f)
        for p_name, snr_th in th.items():
            if snr_th not in [999.0, -999.0]:
                ax.axvline(x=snr_th, color='#009944', linestyle=':', linewidth=1.5)
                ax.text(snr_th + 0.15, 300, f"Threshold: {snr_th:.1f} dB\n({p_name})", 
                        rotation=90, color='#006622', fontsize=8, fontweight='bold')

    ax.set_xlabel('Channel SNR (dB)', fontweight='bold')
    ax.set_ylabel('Useful Goodput (kbps)', fontweight='bold')
    ax.set_title(r'Goodput Crossover Boundaries across SNR (Target FER $\leq 10^{-2}$)', fontweight='bold', pad=12)
    ax.set_ylim([-50, 1600])
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig('figures/fig3_goodput_vs_snr_crossover.png', dpi=300)
    plt.close()
    print("Saved: figures/fig3_goodput_vs_snr_crossover.png")

def plot_dynamic_tracking():
    """Figure 4: Dynamic channel tracking time-series (SNR, RS switches, Goodput)."""
    if not os.path.exists('frame_level_logs.csv'):
        print("frame_level_logs.csv not found, skipping dynamic tracking plot.")
        return
        
    df_logs = pd.read_csv('frame_level_logs.csv')
    # Filter for seed 0 and Adaptive_RS
    seed0_adaptive = df_logs[(df_logs['seed'] == 0) & (df_logs['strategy'] == 'Adaptive_RS')]
    seed0_strong = df_logs[(df_logs['seed'] == 0) & (df_logs['strategy'] == 'Static_Strong')]
    seed0_uncoded = df_logs[(df_logs['seed'] == 0) & (df_logs['strategy'] == 'Static_Weak')]
    
    if seed0_adaptive.empty:
        return
        
    frames = seed0_adaptive['frame_idx'].values[:120]
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8.5), sharex=True, dpi=300)
    
    # 1. SNR Tracking
    ax1.plot(frames, seed0_adaptive['true_snr'].values[:120], color='#ff9900', label='True Channel SNR', linewidth=2)
    ax1.plot(frames, seed0_adaptive['estimated_snr'].values[:120], color='#ffcc66', linestyle='--', label='EVM-Estimated SNR', linewidth=1.2)
    ax1.set_ylabel('SNR (dB)', fontweight='bold')
    ax1.set_title('Dynamic Channel Condition & Adaptive Controller Response', fontweight='bold', pad=10)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper right', frameon=True)
    
    # 2. Selected RS Profile
    prof_map = {str(p): i for i, p in enumerate(SystemConfig.RS_PROFILES)}
    prof_indices = [prof_map.get(p, 0) for p in seed0_adaptive['profile'].values[:120]]
    ax2.step(frames, prof_indices, where='post', color='#0099ff', linewidth=2, label='Active RS Profile')
    ax2.set_yticks(range(len(SystemConfig.RS_PROFILES)))
    ax2.set_yticklabels([str(p) for p in SystemConfig.RS_PROFILES], fontsize=8)
    ax2.set_ylabel('RS Profile', fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='lower right', frameon=True)
    
    # 3. Goodput Comparison
    ax3.plot(frames, seed0_adaptive['goodput'].values[:120], color='#00cc44', label='Adaptive RS Goodput', linewidth=2.2)
    ax3.plot(frames, seed0_strong['goodput'].values[:120], color='#e60000', linestyle=':', label='Static Strong (255, 223)', linewidth=1.5)
    ax3.plot(frames, seed0_uncoded['goodput'].values[:120], color='#888888', linestyle='--', label='Static Uncoded', linewidth=1.2)
    ax3.set_xlabel('Frame Index', fontweight='bold')
    ax3.set_ylabel('Goodput (kbps)', fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.legend(loc='lower right', frameon=True)
    
    plt.tight_layout()
    plt.savefig('figures/fig4_dynamic_tracking_timeseries.png', dpi=300)
    plt.close()
    print("Saved: figures/fig4_dynamic_tracking_timeseries.png")

def plot_statistical_benchmark():
    """Figure 5: Statistical comparison bar chart across strategies."""
    if not os.path.exists('statistical_summary.csv'):
        return
    summary = pd.read_csv('statistical_summary.csv')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.8), dpi=300)
    
    strategies = summary['strategy'].values
    x = np.arange(len(strategies))
    colors = ['#e60000', '#ff9900', '#888888', '#00cc44']
    
    # Goodput Bar Chart
    gp_means = summary['goodput_mean'].values
    gp_stds = summary['goodput_std'].values
    ax1.bar(x, gp_means, yerr=gp_stds, capsize=5, color=colors, alpha=0.85, edgecolor='black')
    ax1.set_xticks(x)
    ax1.set_xticklabels(strategies, rotation=20, ha='right', fontweight='bold')
    ax1.set_ylabel('Mean Goodput (kbps)', fontweight='bold')
    ax1.set_title(r'Goodput Comparison ($\mu \pm \sigma$)', fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # FER Bar Chart
    fer_means = summary['fer_mean'].values
    fer_stds = summary['fer_std'].values
    ax2.bar(x, fer_means, yerr=fer_stds, capsize=5, color=colors, alpha=0.85, edgecolor='black')
    ax2.set_xticks(x)
    ax2.set_xticklabels(strategies, rotation=20, ha='right', fontweight='bold')
    ax2.set_ylabel('Mean Frame Error Rate (FER)', fontweight='bold')
    ax2.set_title(r'FER Comparison ($\mu \pm \sigma$)', fontweight='bold')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('figures/fig5_statistical_benchmark.png', dpi=300)
    plt.close()
    print("Saved: figures/fig5_statistical_benchmark.png")

def plot_dimming_and_crosstalk_sensitivity():
    """Figure 6: Parametric sensitivity analysis for LED Dimming and RGB Crosstalk."""
    runner = SimulationRunner()
    
    # 1. Dimming sweep (fixed 16 dB SNR, Strong and Uncoded profiles)
    dimming_factors = np.linspace(0.2, 1.0, 9)
    gp_dim_adaptive = []
    gp_dim_uncoded = []
    
    np.random.seed(100)
    for dim in dimming_factors:
        res_ad = [runner.run_single_frame(snr_db=16.0, rs_profile=(255, 239), dimming=dim)['goodput_kbps'] for _ in range(25)]
        res_un = [runner.run_single_frame(snr_db=16.0, rs_profile='UNCODED', dimming=dim)['goodput_kbps'] for _ in range(25)]
        gp_dim_adaptive.append(np.mean(res_ad))
        gp_dim_uncoded.append(np.mean(res_un))
        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)
    
    ax1.plot(dimming_factors * 100, gp_dim_adaptive, 's-', color='#0099ff', label='RS(255, 239) Protected', linewidth=2)
    ax1.plot(dimming_factors * 100, gp_dim_uncoded, 'x--', color='#e60000', label='Uncoded Baseline', linewidth=2)
    ax1.set_xlabel('LED Dimming Level (%)', fontweight='bold')
    ax1.set_ylabel('Goodput (kbps)', fontweight='bold')
    ax1.set_title('Impact of Optical Dimming on Goodput (16 dB SNR)', fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='lower right', frameon=True)
    
    # 2. Crosstalk sweep (severity epsilon from 0% to 25%)
    crosstalk_levels = np.linspace(0.0, 0.25, 6)
    fer_xt_strong = []
    fer_xt_uncoded = []
    
    for eps in crosstalk_levels:
        xt_mat = np.array([
            [1.0 - eps, eps, 0.0],
            [eps / 2.0, 1.0 - eps, eps / 2.0],
            [0.0, eps, 1.0 - eps]
        ])
        
        bits = np.random.randint(0, 2, 1000, dtype=np.uint8)
        symbols = CSKMapper.map_bits_to_csk(bits)
        
        # Test demapping bit errors under crosstalk at 18 dB SNR
        rx = OpticalChannel.transmit(symbols, snr_db=18.0, dimming_factor=1.0, crosstalk_matrix=xt_mat)
        demapped = CSKMapper.demap_csk_to_bits(rx)
        ber = np.mean(bits != demapped)
        fer_xt_strong.append(ber)
        
    ax2.plot(crosstalk_levels * 100, fer_xt_strong, 'd-', color='#ff8000', label='Raw Physical BER (18 dB SNR)', linewidth=2)
    ax2.set_xlabel('RGB Crosstalk Mixing Ratio (%)', fontweight='bold')
    ax2.set_ylabel('Bit Error Rate (Demapper)', fontweight='bold')
    ax2.set_title('Receiver BER Degradation vs. RGB Crosstalk', fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='upper left', frameon=True)
    
    plt.tight_layout()
    plt.savefig('figures/fig6_dimming_crosstalk_sensitivity.png', dpi=300)
    plt.close()
    print("Saved: figures/fig6_dimming_crosstalk_sensitivity.png")

if __name__ == '__main__':
    print("Generating publication-grade figures for VLC Simulator...")
    plot_csk_constellation()
    plot_ber_and_goodput_crossover()
    plot_dynamic_tracking()
    plot_statistical_benchmark()
    plot_dimming_and_crosstalk_sensitivity()
    print("\nAll publication-grade figures successfully generated in 'figures/' directory!")
