# VLC Simulator — Interactive Research Dashboard Guide

> **Launch Command:** `streamlit run dashboard.py`
>
> The dashboard opens at `http://localhost:8501` in your default browser.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Launching the Dashboard](#2-launching-the-dashboard)
3. [Sidebar Control Panel](#3-sidebar-control-panel)
4. [Mode 1 — Live Simulation](#4-mode-1--live-simulation)
   - [KPI Metrics Row](#41-kpi-metrics-row)
   - [Performance Overview Charts](#42-performance-overview-charts)
   - [Adaptation Threshold Gauge](#43-adaptation-threshold-gauge)
   - [4-CSK Constellation Scatter](#44-4-csk-constellation-scatter)
   - [Adaptive Decision Trace Console](#45-adaptive-decision-trace-console)
5. [Mode 2 — Multi-Baseline Benchmark](#5-mode-2--multi-baseline-benchmark)
6. [Mode 3 — Log-Driven Replay](#6-mode-3--log-driven-replay)
   - [Frame Scrubbing Inspector](#61-frame-scrubbing-inspector)
   - [Symbol-Level Re-simulation](#62-symbol-level-re-simulation)
   - [Workspace Export](#63-workspace-export)
7. [Architecture and Data Flow](#7-architecture-and-data-flow)
8. [Source Files Reference](#8-source-files-reference)
9. [Tips and Troubleshooting](#9-tips-and-troubleshooting)

---

## 1. Overview

The **VLC Simulator Research Workbench** is a Streamlit-based interactive web application that provides real-time visualization, statistical benchmarking, and forensic replay capabilities for the Channel-Aware Adaptive Reed-Solomon VLC simulator.

It is split into **three operational modes**, each designed for a different stage of research:

| Mode | Purpose | When to Use |
|:-----|:--------|:------------|
| **Live Simulation** | Watch the adaptive controller react frame-by-frame to changing channel conditions in real time | Demonstrating how the controller switches RS profiles as SNR fluctuates |
| **Multi-Baseline Benchmark** | Compare Adaptive RS against fixed baselines across multiple random seeds with confidence intervals | Generating publication-grade statistical summaries |
| **Log-Driven Replay** | Scrub through past experiment logs frame-by-frame, re-simulate individual frames, and export data bundles | Debugging specific frames, verifying reproducibility, extracting byte-level data |

---

## 2. Launching the Dashboard

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Launch
streamlit run dashboard.py
```

The browser opens to `http://localhost:8501`. The full UI loads with the sidebar on the left and the main workspace on the right.

> **Prerequisite for Benchmark Mode:** Run `python experiments.py` first to generate `frame_level_logs.csv` and `statistical_summary.csv`.

---

## 3. Sidebar Control Panel

The left sidebar is the central control hub for all three modes.

### Mode Selector

A dropdown at the top of the sidebar lets you switch between the three modes:
- `Live Simulation`
- `Multi-Baseline Benchmark`
- `Log-Driven Replay Mode`

### Channel Parameters

These sliders configure the physical channel conditions for Live Simulation:

| Control | Range | Default | What It Controls |
|:--------|:------|:--------|:-----------------|
| **Base SNR (dB)** | 0.0 — 25.0 | 15.0 | The mean Signal-to-Noise Ratio of the optical channel. A Gaussian random walk (σ = 0.5 dB) is added on top of this at each frame, simulating realistic indoor fluctuations. |
| **LED Dimming** | 0.1 — 1.0 | 1.0 | Scales the transmitted optical power. At 0.3 (30% brightness), the effective SNR drops by approximately 10.5 dB, stressing the adaptive controller. |
| **Crosstalk** | 0.0 — 0.3 | 0.0 | Controls the off-diagonal coupling in the 3×3 RGB optical crosstalk matrix. Higher values degrade constellation separation. |
| **Random Seed** | Integer | 42 | Fixes the numpy random state for exact reproducibility of the random walk and noise patterns. |

### Controller Selector

Selects which error correction strategy to use during Live Simulation:

- **Adaptive RS** — The full multi-indicator controller with hysteresis and escalation
- **Static Strong (255, 223)** — Fixed high-redundancy coding (t = 16 correctable symbols)
- **Static Medium (255, 239)** — Fixed moderate coding (t = 8)
- **Static Weak (255, 251)** — Fixed minimal coding (t = 2)
- **Uncoded** — No Reed-Solomon protection at all

### Render Throttling Interval

Controls how frequently the heavyweight Plotly charts are redrawn (every N frames). The lightweight KPI numbers update every single frame regardless. Default is 10.

- Lower values (1–5): Smoother chart animations, higher CPU usage
- Higher values (20–50): Snappier UI, charts update less frequently

### Start / Stop Buttons

- **▶️ Start** — Begins the live simulation loop. Frames are generated continuously until stopped.
- **⏹ Stop** — Halts the loop. All charts freeze at their current state and remain visible for inspection.

---

## 4. Mode 1 — Live Simulation

This is the primary mode for demonstrations and real-time experimentation. When you press **Start**, the system generates one frame at a time in a continuous loop, running it through the full pipeline:

```
Generate Payload → Frame (CRC32) → RS Encode → 4-CSK Map → Optical Channel → Demapper → RS Decode → Metrics
```

### 4.1 KPI Metrics Row

Six metric cards are displayed across the top of the workspace. These update **every single frame** (no throttling):

| Metric | Description |
|:-------|:------------|
| **Current SNR (dB)** | The instantaneous channel SNR for this frame (base + random walk noise) |
| **Active RS Profile** | Which Reed-Solomon code is currently selected (e.g., `(255, 223)` or `UNCODED`) |
| **FER** | Frame Error Rate for the current frame (0.0 = clean, 1.0 = corrupted) |
| **BER** | Bit Error Rate — fraction of incorrect bits after RS decoding |
| **Goodput (kbps)** | Effective application-layer throughput excluding overhead and failed frames |
| **CRC Status** | Shows **PASS** (green) or **FAIL** (red) — whether the CRC32 checksum matched after RS decoding |

### 4.2 Performance Overview Charts

A stacked panel of three synchronized Plotly line charts occupying the left 75% of the workspace. They share a common x-axis (Frame Index) and scroll together:

#### Chart 1 — Channel Condition (SNR)
- **Orange solid line:** True instantaneous SNR (dB) per frame
- **Yellow dotted line:** EVM-estimated SNR (what the receiver sees)
- Shows the random walk fluctuation around the base SNR you set in the sidebar

#### Chart 2 — Goodput Performance
- **Green solid line (thick):** Adaptive RS goodput — the main performance metric
- Overlaid dashed lines for static baselines if running a benchmark comparison
- Crossover behavior is directly visible when SNR changes

#### Chart 3 — Error Rates (FER / BER)
- **Red solid line:** Frame Error Rate
- **Cyan dotted line:** Bit Error Rate
- Y-axis is **logarithmic** (range 10⁻⁵ to 10⁰) to capture the massive dynamic range of error rates
- A **red dashed horizontal reference line** marks the Target FER threshold (1%)

#### Event Markers
Whenever the adaptive controller switches RS profiles, a **vertical dashed line** appears across all three charts:
- **Green** — Profile upgraded (moving to faster, less protected code because channel improved)
- **Red** — Profile downgraded or emergency escalation (moving to stronger protection because channel degraded)

### 4.3 Adaptation Threshold Gauge

A circular **gauge meter** on the right sidebar panel showing where the current SNR sits relative to the calibrated crossover switching boundaries:

- Color zones from left to right:
  - **Dark Red (0–~8 dB):** RS_ROBUST territory — maximum protection needed
  - **Red (~8–~12 dB):** RS_HIGH zone
  - **Orange (~12–~16 dB):** RS_MEDIUM zone
  - **Yellow-Green (~16–~20 dB):** RS_LIGHT zone
  - **Green (~20–25 dB):** Uncoded zone — channel is clean enough for no FEC
- A **white needle** indicates the current estimated SNR
- A **cyan threshold marker** shows the exact operating point

The boundaries are loaded from `adaptive_thresholds.json` (generated by `threshold_finder.py`).

### 4.4 4-CSK Constellation Scatter

A live **3D interactive scatter plot** (rotatable, zoomable) showing:

- **Small grey dots:** Received (noisy) constellation points in RGB space — these scatter around the ideal positions due to channel noise
- **Large diamond markers (colored by actual RGB value):** Ideal transmitted constellation points

At low SNR, you will see the grey scatter cloud expand significantly, making it harder for the demapper to distinguish symbols. At high SNR, the dots cluster tightly around the diamonds.

### 4.5 Adaptive Decision Trace Console

A **terminal-style dark console** at the bottom of the page, styled like a command-line interface with green-on-black monospace text. It streams the adaptive controller's reasoning in real time:

```
[FRAME 142] [DOWNGRADE] SNR dropped below lower hysteresis boundary (12.3 dB < 12.8 dB)
            Previous: RS(255, 239) → New: RS(255, 223)
            Trigger: EVM_SNR_LOW | FER_window: 0.08 | CRC_streak: 0

[FRAME 87]  [UPGRADE] SNR exceeded upper hysteresis boundary (18.7 dB > 18.2 dB)
            Previous: RS(255, 223) → New: RS(255, 239)
            Trigger: EVM_SNR_HIGH | FER_window: 0.00 | CRC_streak: 0
```

Color coding:
- **Green `[UPGRADE]`** — Controller is upgrading to a faster code
- **Red `[DOWNGRADE]`** — Controller is retreating to a safer code
- **Orange `[ESCALATION]`** — Emergency fallback triggered by burst CRC failures

When no events have occurred yet, the console shows: *"Waiting for adaptive events... (Change base SNR to trigger switches)"*

### How to Trigger Interesting Behavior

1. **Set Base SNR to 20 dB, press Start** — System runs uncoded or lightly coded, high goodput
2. **While running, drag Base SNR slider down to 8 dB** — Watch the controller rapidly escalate through RS profiles, the goodput line drops, the gauge needle swings left, constellation scatter explodes outward, and red downgrade markers appear on the charts
3. **Drag SNR back up to 18 dB** — Controller cautiously upgrades (note the hysteresis delay — it waits until SNR is firmly above the threshold before upgrading)
4. **Set Dimming to 0.3** — Even at 20 dB base SNR, the effective SNR drops to ~10 dB, triggering adaptation

---

## 5. Mode 2 — Multi-Baseline Benchmark

This mode displays pre-computed statistical results from the multi-seed benchmark engine (`experiments.py`).

### Prerequisites

Run the benchmark first:

```bash
python experiments.py
```

This generates:
- `frame_level_logs.csv` — Per-frame metrics across all seeds and strategies
- `statistical_summary.csv` — Aggregated statistics

### What It Shows

A comprehensive **statistical summary table** with the following columns for each strategy (Adaptive RS, Static Strong, Static Medium, Static Weak, Uncoded):

| Column | Meaning |
|:-------|:--------|
| **Goodput (kbps) [μ ± σ]** | Mean goodput ± standard deviation across all seeds |
| **Goodput 95% CI** | 95% confidence interval computed via Student's t-distribution |
| **FER [μ ± σ]** | Mean Frame Error Rate ± standard deviation |
| **BER [μ ± σ]** | Mean Bit Error Rate ± standard deviation |
| **Avg Switches / Trial** | How many times the controller switched RS profiles per trial (0 for static strategies) |
| **Stability (% Frames w/o Switch)** | Percentage of frames where no profile change occurred — proves the hysteresis prevents ping-ponging |

An **examiner note** at the bottom highlights that a high stability percentage for Adaptive RS demonstrates effective hysteresis.

### Refresh Button

Click **"Refresh Benchmark Results"** to reload the CSV files after re-running `experiments.py`.

---

## 6. Mode 3 — Log-Driven Replay

This mode enables forensic, frame-by-frame inspection of past experiments for guaranteed 100% reproducibility.

### 6.1 Frame Scrubbing Inspector

1. **Upload** a `frame_level_logs.csv` file (or it auto-detects the local file)
2. A **slider** appears spanning all frame indices in the log
3. Drag the slider to any frame index — four KPI cards instantly show:
   - **Frame ID** — The exact frame number
   - **True SNR** — The channel SNR at that exact frame
   - **Profile Selected** — Which RS code was active
   - **CRC Status** — PASS/FAIL with green/red delta indicator

### 6.2 Symbol-Level Re-simulation

Click the **"Re-simulate Frame N for Byte Extraction"** button to:

1. Re-seed numpy with the exact `seed + frame_idx` offset from the original experiment
2. Re-run the full physical pipeline for that single frame
3. Display a **byte comparison table** showing the first 20 bytes:
   - Original TX Byte (Hex)
   - Recovered RX Byte (Hex)
4. Display a **re-simulated 3D constellation scatter** showing the exact transmitted vs. received symbols for that specific frame

This guarantees bit-exact reproducibility — the same seed and frame index always produce identical noise patterns and identical results.

### 6.3 Workspace Export

A **"📥 Download Full Benchmark Bundle (ZIP)"** button packages the following files into a single downloadable archive:

- `frame_level_logs.csv`
- `statistical_summary.csv`
- `adaptive_thresholds.json`

This enables sharing complete experiment workspaces with colleagues or reviewers.

---

## 7. Architecture and Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         dashboard.py (Streamlit)                        │
│                                                                         │
│  ┌──────────────┐  ┌────────────────────┐  ┌────────────────────────┐  │
│  │   Sidebar     │  │   Main Workspace    │  │   Right Panel          │  │
│  │              │  │                    │  │                        │  │
│  │ Mode Select  │  │  KPI Metrics Row   │  │  Threshold Gauge       │  │
│  │ SNR Slider   │  │  (6 cards, live)   │  │  (Plotly Indicator)    │  │
│  │ Dimming      │  │                    │  │                        │  │
│  │ Crosstalk    │  │  Performance Charts │  │  Constellation Scatter │  │
│  │ Seed         │  │  (3 synced plots)  │  │  (Plotly 3D Scatter)   │  │
│  │ Controller   │  │                    │  │                        │  │
│  │ Throttle     │  │  Decision Console  │  │                        │  │
│  │ Start/Stop   │  │  (HTML terminal)   │  │                        │  │
│  └──────────────┘  └────────────────────┘  └────────────────────────┘  │
│                                                                         │
│  Data Sources:                                                          │
│  ├── simulation_runner.py  → run_single_frame() per loop iteration     │
│  ├── adaptive_controller.py → select_rs_profile() decision engine      │
│  ├── channel_quality_estimator.py → EVM/SNR sliding window             │
│  ├── plots.py → Plotly chart rendering functions                       │
│  ├── analytics.py → Decision console HTML + statistical summary        │
│  └── adaptive_thresholds.json → Calibrated SNR switching boundaries    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Render Throttling Strategy

To maintain a responsive UI, the dashboard uses a two-tier update strategy:

- **Every frame:** Lightweight KPI metric cards and progress bar (near-zero render cost)
- **Every N frames (configurable):** Heavy Plotly charts, 3D scatter, gauge, and decision console

A rolling window of 200 frames prevents memory leaks and keeps chart rendering fast.

---

## 8. Source Files Reference

| File | Role |
|:-----|:-----|
| [`dashboard.py`](dashboard.py) | Main Streamlit application — mode routing, session state, simulation loop, replay logic |
| [`plots.py`](plots.py) | Three Plotly rendering functions: `render_performance_charts()`, `render_constellation_scatter()`, `render_threshold_state()` |
| [`analytics.py`](analytics.py) | `render_decision_console()` (HTML terminal) and `render_statistical_summary_page()` (benchmark table) |
| [`simulation_runner.py`](simulation_runner.py) | `SimulationRunner.run_single_frame()` — the end-to-end pipeline called once per loop iteration |
| [`adaptive_controller.py`](adaptive_controller.py) | `AdaptiveLinkController.select_rs_profile()` — hysteresis + escalation decision engine |
| [`channel_quality_estimator.py`](channel_quality_estimator.py) | `ChannelQualityEstimator` — EVM computation, SNR estimation, sliding-window FER/streak tracking |
| [`adaptive_thresholds.json`](adaptive_thresholds.json) | Calibrated SNR crossover boundaries loaded by the gauge chart and controller |
| [`config.py`](config.py) | `SystemConfig` — central constants (RS profiles, CSK constellation map, target FER) |

---

## 9. Tips and Troubleshooting

### The charts are laggy
Increase the **Render Throttling Interval** slider to 20 or 30. The KPI numbers will still update every frame.

### I see "No benchmark data found"
Run `python experiments.py` in your terminal first. This generates the CSV files that the Multi-Baseline Benchmark mode reads.

### The constellation scatter looks flat
The 3D scatter is interactive — click and drag to rotate it. You can also scroll to zoom.

### I want to compare Adaptive RS against a specific static baseline in Live mode
The Live Simulation mode currently runs one controller at a time. For side-by-side comparison, use the **Multi-Baseline Benchmark** mode which runs all strategies across multiple seeds automatically.

### The decision console is empty
The console only shows events when the controller actually switches profiles. Set the base SNR near a crossover boundary (around 12–14 dB) or drag the slider while the simulation is running to trigger switches.

### How do I re-run the threshold calibration?
```bash
python threshold_finder.py
```
This regenerates `adaptive_thresholds.json` with fresh Monte Carlo sweep data.
