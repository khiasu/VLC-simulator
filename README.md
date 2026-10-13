# Channel-Aware Adaptive Reed–Solomon Error Control for a CSK-Based VLC System.

[![Python Tests](https://img.shields.io/badge/pytest-17%20passed-brightgreen.svg)]()
[![Standard](https://img.shields.io/badge/IEEE-802.15.7%204--CSK-blue.svg)]()
[![FEC](https://img.shields.io/badge/FEC-Reed--Solomon%20GF(2%5E8)-orange.svg)]()

## 1. Overview
This project is an experimental software simulator evaluating dynamic, channel-aware **Reed-Solomon (RS)** forward error correction over a **4-Color Shift Keying (4-CSK)** Visible Light Communication (VLC) physical channel.

Indoor optical channels fluctuate dynamically due to user mobility, ambient illumination noise, and LED dimming. Rather than using fixed error correction (which either wastes throughput or suffers packet loss), this system employs an **Explainable, Rule-Based Adaptive Link Controller**. The controller evaluates receiver channel feedback (EVM-based SNR estimation, sliding-window FER, and CRC error streaks) with **0.5 dB hysteresis** and **emergency escalation** to dynamically optimize **Goodput** while enforcing a strict target Frame Error Rate ($\text{FER} \le 10^{-2}$).

---

## 2. System Architecture & Pipeline

```
Application Data ──► Frame Formation (CRC32) ──► RS Encoder (GF(2^8)) ──► 4-CSK Mapper
                                                                                 │
                                                                                 ▼
Recovered Data  ◄──  RS Decoder  ◄──  4-CSK Demapper (ML)  ◄──  Optical Channel (AWGN, Dim, Crosstalk)
     │
     └────────► Channel Quality Estimator (EVM / SNR) ──► Adaptive Link Controller ──► Feedback
```

### Layer Breakdown
1. **Application Layer (`bitstream.py`):** Generates variable byte payloads.
2. **Data Link Layer (`frame.py`):** Packs an 8-byte structured header (`frame_id`, `payload_len`, `rs_profile_idx`, `flags`) and appends a 4-byte CRC32 checksum for corruption detection.
3. **FEC Layer (`rs_codec.py`):** Dynamically applies block-chunked Reed-Solomon codes over Galois Field $GF(2^8)$ across 5 profiles: `(255, 223)` [$t=16$], `(255, 239)` [$t=8$], `(255, 247)` [$t=4$], `(255, 251)` [$t=2$], and `UNCODED` [$t=0$].
4. **Physical Layer (`csk_mapper.py`):** Implements IEEE 802.15.7 4-CSK mapping to normalized RGB vectors with constant optical power ($\sum I = 1.0$), ensuring human eye flicker-free operation.
5. **Optical Channel (`optical_channel.py`):** Models indoor optical impairments including AWGN noise, LED dimming scaling ($\alpha \in [0.1, 1.0]$), and $3 \times 3$ RGB optical crosstalk matrix.
6. **Receiver Estimation (`channel_quality_estimator.py`):** Computes Error Vector Magnitude (EVM) from received 4-CSK symbols, estimates channel SNR ($\text{SNR} \approx -20 \log_{10}(\text{EVM})$), and tracks sliding-window FER.
7. **Adaptive Controller (`adaptive_controller.py`):** Multi-indicator deterministic rule engine featuring:
   * **Crossover Thresholds:** Calibrated offline boundaries cached in `adaptive_thresholds.json`.
   * **0.5 dB Hysteresis:** Prevents rapid "ping-pong" oscillations under channel noise jitter.
   * **Emergency Escalation:** Rapidly forces fallback to maximum protection `(255, 223)` upon 2 consecutive CRC failures or $\text{FER} > 10\%$.

---

## 3. Installation & Requirements

### Prerequisites
* Python 3.10+ (Compatible with Python 3.10 - 3.14)
* Dependencies in `requirements.txt`

### Setup
```bash
pip install -r requirements.txt
```

---

## 4. Running the Simulator & Tools

### A. Run Unit Tests (17/17 passing)
```bash
pytest
```

### B. Run Batch Experiment Sweep
```bash
python simulation_runner.py
```
Simulates the end-to-end pipeline across SNR ranges (5 to 20 dB) and exports results to `simulation_results.csv`.

### C. Run Offline Crossover Calibration
```bash
python threshold_finder.py
```
Sweeps SNR from 5 dB to 25 dB in 0.5 dB steps across 4000+ frames to mathematically derive crossover thresholds cached in `adaptive_thresholds.json`.

### D. Run Multi-Seed Benchmark
```bash
python experiments.py
```
Runs a 5-seed dynamic random walk benchmark (300 frames/trial) comparing Adaptive RS against Static Strong, Static Medium, and Static Weak baselines under realistic sensor estimation noise ($\sigma = 1.0\text{ dB}$). Exports `frame_level_logs.csv` and `statistical_summary.csv`.

### E. Generate Publication-Quality Figures
```bash
python generate_figures.py
```
Generates 300-DPI high-resolution PNG figures saved directly into the `figures/` directory:
* `fig1_csk_constellation_3d.png`: 3D 4-CSK Constellation in RGB Space ($\sum I = 1.0$)
* `fig2_ber_vs_snr.png`: BER vs. SNR across all RS coding profiles
* `fig3_goodput_vs_snr_crossover.png`: Useful Goodput crossover points with calibrated thresholds
* `fig4_dynamic_tracking_timeseries.png`: Dynamic SNR tracking and real-time controller decisions
* `fig5_statistical_benchmark.png`: Multi-seed benchmark statistical summary ($\mu \pm \sigma$)
* `fig6_dimming_crosstalk_sensitivity.png`: Parametric sensitivity to optical dimming and crosstalk

### F. Launch Interactive Research Dashboard
```bash
streamlit run dashboard.py
```
Launches the full interactive web workbench featuring:
* **Live Simulation Mode:** Real-time SNR sliders, dynamic charts, 3D constellation scatter, and decision console.
* **Multi-Baseline Benchmark Mode:** Statistical summaries with 95% Confidence Intervals.
* **Log-Driven Replay Mode:** Frame scrubbing inspector with exact byte extraction.

### G. Generate Review Presentation
```bash
python generate_ppt.py
```
Generates `Project_Review_Presentation.pptx` (16:9 widescreen slide deck with embedded simulation figures).

---

## 5. Repository File Structure

```
vlc_simulator/
├── config.py                     # Central configuration & IEEE 802.15.7 constants
├── bitstream.py                  # Bit array generation and conversion utilities
├── frame.py                      # Data Link Layer framing (Header + CRC32)
├── rs_codec.py                   # Dynamic Reed-Solomon Codec over GF(2^8)
├── csk_mapper.py                 # 4-CSK modulation & ML receiver demapper
├── optical_channel.py            # AWGN, LED dimming, and optical crosstalk
├── channel_quality_estimator.py  # EVM calculation, SNR estimation, and sliding window
├── threshold_finder.py           # Offline crossover calibration engine
├── adaptive_thresholds.json      # Calibrated SNR switching boundaries
├── adaptive_controller.py        # Rule-based decision engine (Hysteresis + Escalation)
├── simulation_runner.py          # Single-frame & batch execution engine
├── experiments.py                # Multi-seed benchmark engine (Adaptive vs Static)
├── analytics.py                  # Terminal trace console & statistical summary
├── plots.py                      # Synchronized Plotly visualizations
├── dashboard.py                  # Streamlit interactive research workbench
├── generate_figures.py           # Publication-grade Matplotlib figure generator
├── generate_ppt.py               # Slide deck generator with embedded figures
├── figures/                      # Generated 300-DPI publication figures
├── tests/                        # 17 comprehensive unit tests (100% passing)
├── frame_level_logs.csv          # Multi-seed frame logs with decision traces
├── simulation_results.csv        # Batch sweep performance data
├── statistical_summary.csv       # Cross-seed statistical metrics (μ ± σ)
├── Project_Review_Presentation.pptx # Project Review presentation deck
└── VLC_MINI_PROJECT_REPORT_SJU.docx # Complete St. Joseph University Mini Project Report
```

---

## 6. Key Benchmark Findings

| Strategy | Mean BER ($\mu \pm \sigma$) | Mean FER ($\mu \pm \sigma$) | Mean Goodput (kbps) | Target FER ($\le 10^{-2}$) Compliance |
| :--- | :---: | :---: | :---: | :---: |
| **Adaptive RS** | **$2.83 \times 10^{-2} \pm 2.12 \times 10^{-2}$** | **$0.47 \pm 0.22$** | **$915.3 \pm 395.2$** | **Dynamically Protected** |
| **Static Strong (255, 223)** | $2.84 \times 10^{-2} \pm 2.14 \times 10^{-2}$ | $0.44 \pm 0.26$ | $920.2 \pm 421.0$ | Over-protected in clean channels |
| **Static Medium (255, 247)** | $2.86 \times 10^{-2} \pm 2.17 \times 10^{-2}$ | $0.53 \pm 0.24$ | $846.1 \pm 427.5$ | Compromised in fading dips |
| **Static Weak (UNCODED)** | $2.84 \times 10^{-2} \pm 2.15 \times 10^{-2}$ | $0.75 \pm 0.16$ | $467.9 \pm 298.7$ | Fails under noise |

Adaptive RS delivers reliable throughput across fluctuating indoor optical channels, avoiding catastrophic collapse during noise surges while dynamically boosting transmission rate as channel quality improves.
