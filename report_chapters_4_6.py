import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_helpers import set_cell_margins, set_cell_shading, set_table_borders, make_equation_box

def add_chapters_4_to_6(doc, add_p, add_heading_1, add_heading_2, add_chapter_title, add_figure_with_caption):
    # =========================================================================
    # CHAPTER 4: DATA LINK LAYER PROTOCOL AND FEC DESIGN
    # =========================================================================
    add_chapter_title(4, "Data Link Layer Protocol and FEC Design")
    
    add_heading_1("4.1 Frame Structure and Framing Manager")
    add_p(
        "To establish reliable end-to-end data transmission across an imperfect optical channel, raw byte streams generated "
        "at the application layer are structured into distinct protocol data units (frames) by the FrameManager class. In physical "
        "optical networks, frames must contain sufficient metadata to enable receiver identification, length verification, "
        "and active codec parameter extraction without out-of-band signaling."
    )
    add_p(
        "Figure 4.1 illustrates the structural layout of the implemented Data Link Layer frame. Each transmitted frame comprises "
        "a standardized 8-byte structured header, a variable application payload (defaulting to 223 bytes to match the baseline "
        "RS(255, 223) message block size), and a 4-byte integrity checksum, resulting in a total frame overhead of 12 bytes."
    )
    add_figure_with_caption("figures/fig_frame_format.png", "Figure 4.1: Data Link Layer Frame Format with 8-Byte Structured Header and 32-Bit CRC", width_in=5.8)

    add_p("Table 4.1 details the field allocation, byte widths, data types, and protocol functions of the 8-byte header.")

    # Table 4.1
    hdr_data = [
        ("Field Name", "Byte Width", "Data Type", "Protocol Function"),
        ("Frame ID", "4 Bytes", "uint32 (Big Endian)", "Monotonically increasing sequence identifier for frame tracking"),
        ("Payload Length", "2 Bytes", "uint16 (Big Endian)", "Explicit payload byte count K to handle arbitrary payload sizing"),
        ("RS Profile ID", "1 Byte", "uint8", "Index of the active Reed-Solomon profile used for decoding selection"),
        ("Protocol Flags", "1 Byte", "uint8", "Control bits reserved for framing status, retransmissions, and signaling")
    ]
    t_hdr = doc.add_table(rows=len(hdr_data), cols=4)
    t_hdr.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_hdr.autofit = False
    set_table_borders(t_hdr, color="D0D0D0", sz="4")
    for r_i, row in enumerate(hdr_data):
        for c_i, val in enumerate(row):
            cell = t_hdr.rows[r_i].cells[c_i]
            cell.width = Inches(1.5) if c_i < 3 else Inches(2.3)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val); r.font.name = 'Times New Roman'; r.font.size = Pt(10)
            if r_i == 0:
                set_cell_shading(cell, "E8E8E8")
                r.font.bold = True

    add_heading_1("4.2 Error Detection Mechanism (Cyclic Redundancy Check CRC32)")
    add_p(
        "A critical challenge in forward error correction architectures is the occurrence of undetected decoder miscorrections. "
        "When channel noise introduces symbol errors that exceed the error-correction bound t = floor((N - K)/2), standard "
        "algebraic decoders may either raise an uncorrectable error exception or erroneously map the corrupted vector to an "
        "incorrect valid codeword. To guarantee that corrupted data is never silently accepted, a 32-bit Cyclic Redundancy "
        "Check (CRC32) is appended to each frame."
    )
    add_p(
        "The CRC32 checksum is calculated over the raw application payload bytes using the standard IEEE 802.3 generator polynomial:"
    )
    make_equation_box(doc, "G_{CRC}(x) = x^{32} + x^{26} + x^{23} + x^{22} + x^{16} + x^{12} + x^{11} + x^{10} + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1", "(4.1)")
    add_p(
        "At the receiver, after the Reed-Solomon decoder attempts symbol correction, the frame header is parsed and the CRC32 "
        "checksum is recomputed over the extracted payload. If the recomputed checksum matches the received 4-byte CRC field, "
        "the frame is flagged as successful (FER = 0) and forwarded to the application layer. If the checksum mismatches or the "
        "header is corrupt, the frame is marked as invalid (FER = 1) and its Goodput is recorded as 0 kbps."
    )

    add_heading_1("4.3 Dynamic Reed-Solomon Codec Architecture")
    add_p(
        "The FEC subsystem is managed by the RSCodecManager class. In conventional implementations, reconfiguring the Reed-Solomon "
        "code requires instantiating new mathematical field structures, introducing prohibitive runtime latency. In this simulator, "
        "the manager pre-instantiates dedicated Galois field codecs over GF(2^8) for each supported profile at initialization, "
        "enabling instantaneous zero-allocation profile switching on a frame-by-frame basis."
    )

    add_heading_2("4.3.1 Profile Definitions and Parity Overheads")
    add_p(
        "Table 4.2 lists the five standardized Reed-Solomon coding profiles implemented in the simulator. The profiles span "
        "from maximum protection (RS(255, 223) with t = 16 byte error correction) to high-throughput UNCODED transmission (t = 0)."
    )

    # Table 4.2
    rs_data = [
        ("Profile Index", "RS Profile (N, K)", "Parity Bytes (2t)", "Correction Capacity (t)", "Code Rate (K/N)", "Target Link Quality"),
        ("0", "RS(255, 223)", "32 Bytes", "t = 16 Bytes", "0.875", "Severe Noise / Dimming / Fading"),
        ("1", "RS(255, 239)", "16 Bytes", "t = 8 Bytes", "0.937", "Moderate Fading Link"),
        ("2", "RS(255, 247)", "8 Bytes", "t = 4 Bytes", "0.969", "Nominal Indoor Channel"),
        ("3", "RS(255, 251)", "4 Bytes", "t = 2 Bytes", "0.984", "High SNR Clean Link"),
        ("4", "UNCODED", "0 Bytes", "t = 0 Bytes", "1.000", "Near-Perfect LOS Alignment")
    ]
    t_rs = doc.add_table(rows=len(rs_data), cols=6)
    t_rs.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_rs.autofit = False
    set_table_borders(t_rs, color="D0D0D0", sz="4")
    for r_i, row in enumerate(rs_data):
        for c_i, val in enumerate(row):
            cell = t_rs.rows[r_i].cells[c_i]
            cell.width = Inches(1.1)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val); r.font.name = 'Times New Roman'; r.font.size = Pt(10)
            if r_i == 0:
                set_cell_shading(cell, "E8E8E8")
                r.font.bold = True

    add_heading_2("4.3.2 Block Chunking and Zero-Padding for Variable Payloads")
    add_p(
        "To support application payloads that exceed the single-block capacity K of an RS profile, the codec manager implements "
        "a block-chunking algorithm. If the incoming framed byte stream exceeds K bytes, it is partitioned into discrete chunks of "
        "size K. Each chunk is encoded independently, and the resulting N-byte blocks are concatenated for physical modulation. "
        "At the receiver, the sequence of chunks is decoded sequentially and reassembled into the original frame."
    )

    add_heading_2("4.3.3 Decoding Failure Detection and Corrupted Symbol Counting")
    add_p(
        "During decoding, if the number of corrupted bytes within any chunk exceeds the code's correction capacity t, the underlying "
        "Berlekamp-Massey algorithm cannot find a valid error locator polynomial and raises a ReedSolomonError exception. The codec "
        "catches this exception cleanly, records a decoding failure (decode_success = False), logs corrected_symbols = -1, and returns "
        "the raw uncorrected bytes to ensure downstream CRC verification properly catches the corruption."
    )

    # =========================================================================
    # CHAPTER 5: ADAPTIVE LINK CONTROLLER AND ESTIMATION ENGINE
    # =========================================================================
    add_chapter_title(5, "Adaptive Link Controller and Estimation Engine")
    
    add_heading_1("5.1 Real-Time Receiver Quality Estimation (EVM and SNR Calculation)")
    add_p(
        "The receiver channel quality estimator operates without requiring pilot preambles by extracting Error Vector Magnitude (EVM) "
        "directly from the received 4-CSK constellation symbols. For each received symbol vector I_{rx, i}, the demapper identifies "
        "the closest reference anchor s_{closest} in the 4-CSK constellation using minimum Euclidean distance. The error vector e_i "
        "is computed as:"
    )
    make_equation_box(doc, "e_i = I_{rx, i} - s_{closest}", "(5.1)")
    add_p(
        "Across a frame containing M optical symbols, the mean square error (representing channel noise power) and mean square ideal "
        "power (representing signal power) are calculated:"
    )
    make_equation_box(doc, "P_{noise} = (1/M) * sum_{i=1}^M || e_i ||^2,    P_{signal} = (1/M) * sum_{i=1}^M || s_{closest} ||^2", "(5.2)")
    add_p(
        "The linear Signal-to-Noise Ratio is approximated as SNR_{linear} = P_{signal} / P_{noise}, which is converted to decibels:"
    )
    make_equation_box(doc, "SNR_{est_dB} = 10 * log_{10}( P_{signal} / P_{noise} )", "(5.3)")
    add_p("If P_{noise} equals zero (perfect noise-free transmission), the estimator clips the result to an upper cap of 100.0 dB.")

    add_heading_1("5.2 Sliding-Window Link State Tracking")
    add_p(
        "Single-frame SNR estimates are susceptible to random noise spikes. To ensure reliable decision-making, the ChannelQualityEstimator "
        "maintains a rolling history of link metrics across a sliding window of length W = 10 frames. The tracked state includes:"
    )
    add_p("1. Moving Average SNR (avg_snr_db): The arithmetic mean of estimated SNRs across the last W frames.")
    add_p("2. Recent Frame Error Rate (recent_fer): The fraction of frames that failed CRC32 verification within the window:")
    make_equation_box(doc, "FER_{window} = 1.0 - (1/W) * sum_{j=1}^W CRC_pass_j", "(5.4)")
    add_p("3. CRC Failure Streak (crc_failure_streak): The number of consecutive uncorrected frames leading up to the current frame.")
    add_p("4. Average Corrected Symbols (avg_corrections): The mean number of byte errors corrected by the RS decoder per frame.")

    add_heading_1("5.3 Offline Crossover Calibration Sweep Engine")
    add_p(
        "To establish deterministic switching boundaries, an offline crossover calibration engine (threshold_finder.py) was developed. "
        "The calibrator runs batch simulations sweeping channel SNR from 5.0 dB to 25.0 dB in increments of 0.5 dB across all five RS "
        "profiles, simulating 100 frames per configuration (totalling 20,000+ simulated frames). For each SNR step, the engine determines "
        "which profiles satisfy the target reliability constraint (FER <= 10^-2) and selects the profile that achieves the highest Goodput."
    )
    add_p(
        "Table 5.1 presents the derived crossover boundaries. The strongest profile RS(255, 223) serves as the baseline fallback, requiring "
        "no minimum SNR (-infinity). RS(255, 239) becomes optimal at 16.0 dB, RS(255, 251) at 17.5 dB, and UNCODED transmission at 20.5 dB. "
        "The intermediate profile RS(255, 247) is subsumed because RS(255, 239) and RS(255, 251) provide superior Goodput within that range."
    )

    # Table 5.1
    th_data = [
        ("RS Profile", "Minimum SNR Activation Threshold", "Error Capacity (t)", "Operational Regime"),
        ("RS(255, 223)", "-infinity (Default Fallback)", "t = 16 Bytes", "Active when SNR < 16.0 dB or during channel fades"),
        ("RS(255, 239)", "16.0 dB", "t = 8 Bytes", "Optimal in range [16.0 dB, 17.5 dB)"),
        ("RS(255, 247)", "999.0 dB (Subsumed)", "t = 4 Bytes", "Subsumed by adjacent profiles in discrete sweep"),
        ("RS(255, 251)", "17.5 dB", "t = 2 Bytes", "Optimal in range [17.5 dB, 20.5 dB)"),
        ("UNCODED", "20.5 dB", "t = 0 Bytes", "Optimal when SNR >= 20.5 dB (Max Goodput: 1500+ kbps)")
    ]
    t_th = doc.add_table(rows=len(th_data), cols=4)
    t_th.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_th.autofit = False
    set_table_borders(t_th, color="D0D0D0", sz="4")
    for r_i, row in enumerate(th_data):
        for c_i, val in enumerate(row):
            cell = t_th.rows[r_i].cells[c_i]
            cell.width = Inches(1.5) if c_i < 3 else Inches(2.2)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val); r.font.name = 'Times New Roman'; r.font.size = Pt(10)
            if r_i == 0:
                set_cell_shading(cell, "E8E8E8")
                r.font.bold = True

    add_heading_1("5.4 Multi-Indicator Rule-Based Decision Logic")
    add_p(
        "The AdaptiveLinkController implements a prioritized, explainable decision engine. Figure 5.1 displays the state flowchart "
        "of the decision logic, and Table 5.2 defines the action matrix governing profile transitions."
    )
    add_figure_with_caption("figures/fig_controller_flowchart.png", "Figure 5.1: Adaptive Link Controller Multi-Indicator Decision Engine Flowchart", width_in=5.6)

    add_heading_2("5.4.1 Hysteresis Margin Formulation (0.5 dB)")
    add_p(
        "To eliminate ping-pong oscillations caused by instantaneous SNR noise around switching boundaries, the controller incorporates "
        "a symmetric hysteresis margin Delta = 0.5 dB:"
    )
    add_p(
        "1. Upgrade Rule: To upgrade from current profile i to a lighter profile j (where j > i), the moving average SNR must exceed "
        "the activation threshold by at least Delta:"
    )
    make_equation_box(doc, "SNR_{avg} >= Threshold(j) + Delta    (where Delta = 0.5 dB)", "(5.5)")
    add_p(
        "2. Maintain Rule: If the channel degrades slightly, the current profile i is maintained as long as the SNR remains within the "
        "hysteresis tolerance:"
    )
    make_equation_box(doc, "SNR_{avg} >= Threshold(i) - Delta", "(5.6)")
    add_p("3. Downgrade Rule: If the SNR drops below Threshold(i) - Delta, the controller steps down to the nearest safe profile.")

    add_heading_2("5.4.2 Fast Emergency Escalation Trigger")
    add_p(
        "Standard threshold checks operate on moving averages, which introduce a slight lag when severe channel degradation occurs "
        "(e.g., direct line-of-sight blockage). To protect link integrity, an emergency escalation trigger bypasses the hysteresis rules. "
        "If the receiver detects two consecutive CRC failures (crc_failure_streak >= 2) or the recent window error rate exceeds 10% "
        "(recent_fer > 0.1), the controller forces an immediate retreat to maximum protection RS(255, 223), preventing packet loss cascades."
    )

    add_heading_2("5.4.3 Auditable Decision Trace Generation")
    add_p(
        "Every decision made by the controller produces a structured string trace detailing the previous profile, selected profile, "
        "estimated SNR, crossover boundary, trigger reason, and current streak count. These traces provide complete auditability "
        "during live simulation and offline analysis."
    )

    # Table 5.2
    act_data = [
        ("Priority", "Trigger Condition", "Decision Action", "Selected Profile", "Rationale"),
        ("1 (Highest)", "crc_failure_streak >= 2 OR recent_fer > 0.1", "[ESCALATION]", "RS(255, 223)", "Immediate fallback on burst error"),
        ("2", "SNR_avg >= Threshold_new + 0.5 dB", "[UPGRADE]", "Lighter RS Code", "SNR cleared threshold + hysteresis"),
        ("3", "SNR_avg >= Threshold_curr - 0.5 dB", "[MAINTAIN]", "Current Profile", "Channel stable within hysteresis"),
        ("4", "SNR_avg < Threshold_curr - 0.5 dB", "[DOWNGRADE]", "Stronger RS Code", "SNR dropped below safe margin"),
        ("5 (Lowest)", "All threshold checks fail", "[FALLBACK]", "RS(255, 223)", "Catastrophic channel fallback")
    ]
    t_act = doc.add_table(rows=len(act_data), cols=5)
    t_act.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_act.autofit = False
    set_table_borders(t_act, color="D0D0D0", sz="4")
    for r_i, row in enumerate(act_data):
        for c_i, val in enumerate(row):
            cell = t_act.rows[r_i].cells[c_i]
            cell.width = Inches(1.3) if c_i < 4 else Inches(2.0)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val); r.font.name = 'Times New Roman'; r.font.size = Pt(10)
            if r_i == 0:
                set_cell_shading(cell, "E8E8E8")
                r.font.bold = True

    # =========================================================================
    # CHAPTER 6: SIMULATION ENGINE AND INTERACTIVE WORKBENCH
    # =========================================================================
    add_chapter_title(6, "Simulation Engine and Interactive Workbench")
    
    add_heading_1("6.1 End-to-End Simulation Runner and Batch Experimentation")
    add_p(
        "The core execution framework is implemented in SimulationRunner (simulation_runner.py). It provides two primary execution modes:"
    )
    add_p(
        "1. Single-Frame Execution: The run_single_frame() method executes a single frame through the full pipeline: payload creation, "
        "CRC32 packing, RS encoding, 4-CSK modulation, channel transmission (AWGN, dimming, crosstalk), ML demapping, RS decoding, and "
        "CRC verification. It records Bit Error Rate (BER), Frame Error Rate (FER), Goodput (kbps), and symbol correction metrics."
    )
    add_p(
        "2. Batch Experimentation: The run_batch_experiment() method sweeps SNR arrays across configured profiles, aggregating mean BER, "
        "FER, and Goodput for systematic performance comparisons."
    )

    add_heading_1("6.2 Streamlit-Based Interactive Research Dashboard")
    add_p(
        "To provide an intuitive experimental research workbench, an interactive web dashboard was constructed using Streamlit (dashboard.py). "
        "The interface incorporates custom CSS styling and Plotly visualization components across three operating modes:"
    )
    add_p(
        "1. Live Simulation Mode: Provides real-time sliders for Base SNR (0 to 25 dB), LED Dimming (0.1 to 1.0), and RGB Crosstalk (0 to 0.3). "
        "During live execution, lightweight KPI cards update frame-by-frame, while heavier Plotly figures (3-panel time-series, SNR gauge, "
        "and 3D constellation scatter) update periodically via configurable render throttling (every 10 frames) to maintain UI responsiveness."
    )
    add_p(
        "2. Multi-Baseline Benchmark Mode: Automatically loads multi-seed experiment logs, computing cross-seed statistical summaries (Mean "
        "+/- Std Dev) and 95% Confidence Intervals for Goodput across Adaptive RS and static baselines."
    )
    add_p(
        "3. Log-Driven Replay Mode: Features a frame-scrubbing inspector that loads exported CSV logs, displays exact channel metrics, and "
        "re-simulates specific frames using stored seed offsets to extract and display raw payload bytes in hexadecimal for forensic inspection."
    )

    add_heading_1("6.3 Test-Driven Development and Unit Test Verification (17 Pytest Suites)")
    add_p(
        "To guarantee numerical accuracy and code integrity, all modules were developed using Test-Driven Development (TDD). A comprehensive "
        "pytest test suite comprising 17 automated tests was implemented. Table 6.1 summarizes the unit test architecture and verification results."
    )

    # Table 6.1
    test_data = [
        ("Test Module", "Test Function Name", "Scope of Validation", "Result"),
        ("test_frame.py", "test_frame_build_and_parse_success", "Header packing, unpacking, and CRC32 verification", "PASSED"),
        ("test_frame.py", "test_crc_failure_detection", "Tampered payload detection and CRC failure trapping", "PASSED"),
        ("test_frame.py", "test_frame_short_payload", "Handling of variable-length payload boundaries", "PASSED"),
        ("test_rs_codec.py", "test_rs_codec_uncoded", "Pass-through integrity for UNCODED profile", "PASSED"),
        ("test_rs_codec.py", "test_rs_codec_error_correction", "Correction of 16 byte corruptions in RS(255, 223)", "PASSED"),
        ("test_rs_codec.py", "test_rs_codec_uncorrectable", "Exception trapping when byte errors exceed t", "PASSED"),
        ("test_csk_mapper.py", "test_csk_mapping_demapping_no_noise", "Exact bit-to-RGB-to-bit reconstruction without noise", "PASSED"),
        ("test_optical_channel.py", "test_dimming_reduces_power", "Photodiode optical power reduction before AGC", "PASSED"),
        ("test_optical_channel.py", "test_dimming_with_agc_increases_errors", "Noise amplification and error increase under dimming", "PASSED"),
        ("test_optical_channel.py", "test_noise_increases_errors", "Error scaling from 40 dB SNR to 0 dB SNR", "PASSED"),
        ("test_channel_quality_estimator.py", "test_sliding_window_metrics", "FER, streak, and SNR tracking in rolling window", "PASSED"),
        ("test_channel_quality_estimator.py", "test_estimate_snr_perfect_signal", "EVM cap verification (100 dB) on noise-free symbols", "PASSED"),
        ("test_channel_quality_estimator.py", "test_estimate_snr_noisy_signal", "SNR degradation under Gaussian noise injection", "PASSED"),
        ("test_adaptive_controller.py", "test_escalation_trigger", "Fast retreat to RS(255, 223) on streak >= 2", "PASSED"),
        ("test_adaptive_controller.py", "test_hysteresis_upgrade_downgrade", "0.5 dB hysteresis margin enforcement", "PASSED"),
        ("test_dashboard_replay.py", "test_build_experiment_metadata", "Provenance tracking JSON structure and keys", "PASSED"),
        ("test_dashboard_replay.py", "test_replay_dataframe_parsing", "CSV log loading and frame telemetry extraction", "PASSED")
    ]
    t_test = doc.add_table(rows=len(test_data), cols=4)
    t_test.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_test.autofit = False
    set_table_borders(t_test, color="D0D0D0", sz="4")
    for r_i, row in enumerate(test_data):
        for c_i, val in enumerate(row):
            cell = t_test.rows[r_i].cells[c_i]
            cell.width = Inches(1.8) if c_i < 3 else Inches(1.0)
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val); r.font.name = 'Times New Roman'; r.font.size = Pt(9.5)
            if r_i == 0:
                set_cell_shading(cell, "E8E8E8")
                r.font.bold = True
            elif c_i == 3:
                r.font.bold = True

    print("Chapters 4 to 6 written successfully.")
