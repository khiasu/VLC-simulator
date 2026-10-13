import os
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_helpers import (
    add_body_p,
    add_bullet_p,
    add_chapter_title,
    add_heading_1,
    add_heading_2,
    add_figure_with_caption,
    add_table_with_caption,
    make_equation_box
)

def build_chapters_1_2(doc):
    """
    Builds Chapter 1 and Chapter 2 with deep academic rigor, exact formatting,
    detailed mathematical formulations, tables, and figures.
    """
    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    add_chapter_title(doc, "1", "INTRODUCTION")

    add_heading_1(doc, "1.1 Background of Visible Light Communication (VLC)")
    add_body_p(doc, "Over the past two decades, wireless data traffic has grown at an exponential pace driven by the ubiquitous deployment of high-density mobile computing, industrial Internet of Things (IoT) sensors, cloud computing telemetry, and immersive multimedia streaming. This surge in data consumption has placed unprecedented strain on conventional radio frequency (RF) bands, which span from hundreds of megahertz to approximately six gigahertz. As commercial wireless carriers densify cellular base stations and deploy multi-carrier Wi-Fi access points, the unlicensed RF spectrum suffers from acute electromagnetic saturation, severe co-channel interference, regulatory power caps, and stringent bandwidth constraints. In response to this looming spectrum crunch, researchers and standardization bodies have turned their attention toward optical wireless communication (OWC), specifically Visible Light Communication (VLC).")

    add_body_p(doc, "Visible Light Communication utilizes the unregulated, unlicensed electromagnetic spectrum between 380 nm and 780 nm—a spectral expanse comprising approximately 400 terahertz of optical bandwidth, which is more than ten thousand times larger than the entire allocated radio-frequency spectrum. Rather than requiring dedicated high-power radio transmitters, VLC repurposes ubiquitous solid-state Light Emitting Diodes (LEDs) installed throughout modern indoor infrastructure (such as offices, hospitals, aircraft cabins, hazardous industrial facilities, and smart homes) to perform dual functions: high-quality spatial illumination and simultaneous broadband wireless data transmission.")

    add_body_p(doc, "Unlike RF signals, optical radiation cannot penetrate opaque solid walls or physical partitions. While this characteristic limits transmission ranges strictly to localized room dimensions, it provides exceptional physical-layer spatial security: wireless data transmission cannot be intercepted or eavesdropped outside the illuminated optical boundary. Furthermore, visible light generates zero electromagnetic interference (EMI), permitting uninterrupted broadband wireless deployment in EMI-sensitive healthcare intensive care units, petrochemical manufacturing plants, nuclear power generation facilities, and commercial aviation cabins where conventional RF emissions are strictly prohibited.")

    add_heading_1(doc, "1.2 The Spectrum Bottleneck and Optical Wireless Solutions")
    add_body_p(doc, "The radio spectrum crisis represents a structural bottleneck in wireless network engineering. Traditional remedies have sought to push carrier frequencies into the millimeter-wave (mmWave) and sub-terahertz regimes (28 GHz to 300 GHz). However, mmWave propagation in indoor environments suffers from acute atmospheric attenuation, severe oxygen absorption resonance, high penetration loss through lightweight building materials, and costly radio-frequency transceivers plagued by phase noise and thermal dissipation constraints. VLC sidesteps these physical drawbacks by deploying cost-effective silicon photodiodes and semiconductor LEDs operating entirely in the optical domain.")

    add_body_p(doc, "To formalize the indoor optical channel geometry, consider a typical line-of-sight (LOS) link between a ceiling-mounted LED luminaire and a desktop-level photodiode receiver. The direct optical path loss is governed by the generalized Lambertian radiant intensity distribution. The optical line-of-sight channel direct-current (DC) gain, denoted as H_LOS(0), is rigorously expressed as:")

    make_equation_box(doc, "H_{LOS}(0) = \\frac{(m+1) A_{det}}{2 \\pi d^2} \\cos^m(\\phi) T_s(\\psi) g(\\psi) \\cos(\\psi), \\quad 0 \\le \\psi \\le \\Psi_c", "1.1")

    add_body_p(doc, "where m represents the Lambertian emission order determined by the semi-angle at half illuminance Phi_{1/2}, A_{det} represents the active physical surface area of the receiving photodetector, d is the direct Euclidean distance separating the optical transmitter and receiver, phi is the angle of irradiance relative to the luminaire normal vector, psi is the angle of incidence relative to the receiver surface normal, T_s(psi) is the transmission characteristic of the optical bandpass filter, g(psi) is the internal refractive optical concentrator gain, and Psi_c is the semi-angle field-of-view (FOV) of the photodetector.")

    add_body_p(doc, "Because the received optical power scales inversely with the square of Euclidean distance (d^2) and attenuates sharply as the receiver moves away from the primary luminaire axis (cos^m(phi) cos(psi)), indoor mobile receivers experience severe spatial power gradients. A receiver traversing across an ordinary office room experiences received optical power fluctuations spanning 15 dB to 30 dB over a span of merely two meters, demanding robust transmission protocols.")

    add_heading_1(doc, "1.3 Motivation: Static Coding Inefficiencies in Dynamic VLC")
    add_body_p(doc, "In traditional digital communication architectures, reliable data delivery across impaired channels is achieved through Forward Error Correction (FEC). The IEEE 802.15.7 standard for optical wireless communications recommends Reed-Solomon (RS) algebraic block codes implemented over Galois Field GF(2^8). However, standard implementations enforce static, unvarying error correction parameters. For instance, a system might be configured permanently with a high-redundancy code such as RS(255, 191), or permanently with a low-redundancy code such as RS(255, 247).")

    add_body_p(doc, "This static design paradigm imposes a severe operational dilemma in dynamic indoor VLC environments:")
    add_bullet_p(doc, "Under benign channel conditions (e.g., when the mobile receiver sits directly beneath the luminaire at high SNR), conservative error correction wastes valuable channel bandwidth by transmitting unnecessary parity symbols. This imposes an unrecoverable 25.1% goodput penalty.", "Excessive Redundancy Overhead:")
    add_bullet_p(doc, "Conversely, under aggressive coding (e.g., RS(255, 247)), if an optical path is temporarily obstructed by a walking occupant, dimmed for energy conservation, or misaligned due to device tilting, channel SNR plummets below the decodability threshold. The uncorrectable symbol errors cause immediate CRC32 checksum failures, catastrophic frame drops, and severe goodput collapse.", "Catastrophic Frame Loss:")
    add_bullet_p(doc, "Because illumination is the primary function of indoor lighting, luminaire drivers frequently adjust LED drive currents to satisfy user dimming preferences (e.g., dimming down to 20% illuminance). Furthermore, tri-chromatic RGB emitters suffer from temperature-dependent optical crosstalk across red, green, and blue spectral bands. A static channel code cannot cope with these coupled physical-layer variations.", "Coupled Physical Impairments:")

    add_body_p(doc, "These fundamental inefficiencies establish the compelling engineering necessity for Channel-Aware Adaptive Reed-Solomon Error Control: an intelligent, closed-loop mechanism capable of dynamically estimating physical channel quality and tuning code rates in real time.")

    add_heading_1(doc, "1.4 Problem Formulation and Mathematical Framework")
    add_body_p(doc, "The fundamental objective of an adaptive error control framework is to maximize the link effective Goodput, denoted as G_{eff}, while strictly enforcing an upper bound on the receiver Frame Error Rate (FER), denoted as FER_{target}. Let N denote the fixed Reed-Solomon block length in bytes (N = 255 for standard GF(2^8) codes), and let K denote the variable payload length in bytes, where K in {191, 207, 223, 239, 247, 255}. The error correction capability t of an RS(N, K) code satisfies t = floor((N - K) / 2) symbol errors per block.")

    add_body_p(doc, "Let R_s denote the physical symbol transmission rate in symbols per second, let M denote the modulation constellation cardinality (M = 4 for 4-CSK, corresponding to log_2(4) = 2 bits per optical symbol), and let L_{data} represent the unencoded application payload size in bytes. The effective Goodput of the optical link is rigorously formulated as:")

    make_equation_box(doc, "G_{eff}(K, \\text{SNR}) = \\frac{L_{data}}{T_{frame}(K)} \\cdot \\left[ 1 - \\text{FER}(K, \\text{SNR}) \\right] \\quad [\\text{Bytes/second}]", "1.2")

    add_body_p(doc, "where T_{frame}(K) represents the total transmission duration of the physical frame including preamble, frame header, variable Reed-Solomon parity blocks, and CRC32 tail. The optimization problem is mathematically stated as:")

    make_equation_box(doc, "K^*(t) = \\arg\\max_{K_i \\in \\mathcal{S}_{RS}} G_{eff}(K_i, \\widehat{\\text{SNR}}(t)) \\quad \\text{subject to} \\quad \\text{FER}(K_i, \\widehat{\\text{SNR}}(t)) \\le 10^{-3}", "1.3")

    add_body_p(doc, "where S_{RS} = {255, 247, 239, 223, 207, 191} represents the set of discrete permissible Reed-Solomon payload capacities, and hat{SNR}(t) represents the estimated channel quality derived from sliding-window Error Vector Magnitude (EVM) feedback.")

    # Insert Architecture Figure
    fig1_path = os.path.join(os.path.dirname(__file__), "figures", "fig_pipeline_architecture.png")
    add_figure_with_caption(doc, fig1_path, "End-to-End Channel-Aware Adaptive VLC System Architecture and Dataflow", "1.1", width_inches=5.8)

    add_heading_1(doc, "1.5 Objectives of the Mini Project")
    add_body_p(doc, "To resolve the aforementioned problem within the scope of the Mini Project, the following specific engineering objectives are established:")
    add_bullet_p(doc, "Design and implement a complete software simulation pipeline covering application data generation, 12-byte framed packetization, CRC32 error detection, variable Reed-Solomon codec over Galois Field GF(2^8), and IEEE 802.15.7 4-CSK modulation.", "Objective 1: End-to-End Protocol Pipeline:")
    add_bullet_p(doc, "Develop a realistic indoor optical channel simulator incorporating line-of-sight path loss, variable additive Gaussian receiver noise, photodiode optical crosstalk across RGB channels, and variable LED dimming attenuation.", "Objective 2: Physical Optical Channel Modeling:")
    add_bullet_p(doc, "Formulate a fast, sliding-window Channel Quality Estimator at the optical receiver that evaluates Error Vector Magnitude (EVM) from recovered CSK constellation coordinates to derive continuous SNR estimates.", "Objective 3: Receiver Quality Estimation:")
    add_bullet_p(doc, "Conduct extensive offline Monte Carlo crossover calibration sweeps to identify exact mathematical SNR switching boundaries where neighboring Reed-Solomon code profiles intersect in effective goodput.", "Objective 4: Crossover Boundary Calibration:")
    add_bullet_p(doc, "Engineer an explainable, deterministic, rule-based adaptive controller incorporating dual-threshold hysteresis to eliminate ping-pong oscillations and multi-indicator escalation triggers for burst recovery.", "Objective 5: Explainable Adaptive Controller:")
    add_bullet_p(doc, "Construct an interactive research workbench (Streamlit dashboard) and validate the complete architecture through multi-seed statistical benchmarks and comprehensive automated unit test suites.", "Objective 6: Workbench & Empirical Validation:")

    add_heading_1(doc, "1.6 Scope and Delimitations of the Work")
    add_body_p(doc, "It is crucial to define the formal boundaries and scope of this Mini Project:")
    add_bullet_p(doc, "This Mini Project deliberately restricts its focus to a fully explainable, deterministic, rule-based adaptive controller. Complex machine learning or Deep Reinforcement Learning (DRL) algorithms are strictly reserved for the upcoming Major Project phase. The mini project provides the foundational, verified simulation engine.", "Rule-Based Scope (No AI/ML in Core):")
    add_bullet_p(doc, "Modulation is anchored strictly to IEEE 802.15.7 Color Shift Keying with cardinality M=4 (4-CSK) over tri-chromatic red, green, and blue LEDs. Higher-order constellations (8-CSK, 16-CSK) and single-color OOK/VPPM are delimited.", "Modulation Boundary:")
    add_bullet_p(doc, "The physical optical channel assumes a direct Line-of-Sight (LOS) link with additive white Gaussian noise (thermal noise plus ambient optical shot noise) and memoryless inter-channel crosstalk. Multi-path diffuse non-line-of-sight reflections with temporal dispersion are omitted due to typical indoor symbol rates remaining below the channel delay spread.", "Channel Assumptions:")
    add_bullet_p(doc, "All experiments are conducted via high-fidelity, bit-level and symbol-level Python simulation, backed by mathematical models validated in IEEE OWC literature.", "Software Implementation:")

    # Insert Work Package Table
    table_1_headers = ["Work Package", "Technical Focus", "Core Mechanism", "Empirical Deliverable"]
    table_1_data = [
        ["WP1: Central Config", "System Parameters", "Static & dynamic constant definitions in config.py", "Validated parameter dictionary"],
        ["WP2: Framing & Codec", "Data Link Layer", "CRC32 packing & dynamic RS(255,K) GF(2^8) codec", "100% bit-accurate decode test suite"],
        ["WP3: Optical PHY", "Physical Layer", "IEEE 802.15.7 4-CSK mapper & noisy optical channel", "3D constellation scatter & AGC validation"],
        ["WP4: Calibration", "Crossover Analysis", "4000-frame Monte Carlo sweep across SNR 0-25 dB", "Calibrated switching threshold JSON"],
        ["WP5: Controller", "Adaptation Logic", "Sliding-window EVM, 0.8 dB hysteresis, escalation", "Deterministic profile decision engine"],
        ["WP6: Benchmarking", "Empirical Validation", "Multi-seed comparative simulation & Streamlit UI", "Statistical summary CSV & 9 PNG figures"],
    ]
    add_table_with_caption(doc, "1.1", "Project Work Packages, Methodological Premises, and Engineering Targets", table_1_headers, table_1_data, [1.4, 1.4, 2.3, 1.5])

    add_heading_1(doc, "1.7 Organization of the Project Report")
    add_body_p(doc, "The remainder of this Mini Project Report is organized into seven subsequent chapters:")
    add_bullet_p(doc, "Reviews the historical evolution of optical wireless networking, IEEE 802.15.7 standards, Galois Field arithmetic, Reed-Solomon decoding theory, and channel estimation literature.", "Chapter 2 (Literature Review):")
    add_bullet_p(doc, "Formulates the indoor Lambertian optical channel physics, photodiode electrical properties, IEEE 802.15.7 4-CSK constellation mapping, optical crosstalk leakage, and dimming invariance.", "Chapter 3 (Optical Channel & 4-CSK):")
    add_bullet_p(doc, "Details the 12-byte framed packet structure, CRC32 generation, payload chunking, and the dynamic Reed-Solomon encoder/decoder implementation over GF(2^8).", "Chapter 4 (Framing & RS Codec):")
    add_bullet_p(doc, "Presents the architectural mechanics of the explainable adaptive controller, including sliding-window EVM-SNR estimation, crossover calibration, and dual-threshold hysteresis.", "Chapter 5 (Adaptive Controller):")
    add_bullet_p(doc, "Details the object-oriented software architecture, the interactive research workbench (Streamlit), and the automated Pytest unit test harness.", "Chapter 6 (Simulation Engine):")
    add_bullet_p(doc, "Presents extensive experimental evaluations, including BER waterfall curves, goodput envelopes, dynamic time-series tracking, multi-seed statistical benchmarks, and sensitivity curves.", "Chapter 7 (Experimental Results):")
    add_bullet_p(doc, "Discusses engineering challenges, analyzes heuristic limitations, and formally specifies the Gymnasium-compliant RL interface for the Major Project continuation.", "Chapter 8 (Conclusion & Future Scope):")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 2: LITERATURE REVIEW AND THEORETICAL FOUNDATIONS
    # =========================================================================
    add_chapter_title(doc, "2", "LITERATURE REVIEW AND THEORETICAL FOUNDATIONS")

    add_heading_1(doc, "2.1 Evolution of Optical Wireless and Li-Fi Technologies")
    add_body_p(doc, "Optical wireless communication traces its conceptual origins to Alexander Graham Bell's 1880 Photophone, which modulated sunlight reflected from a vibrating mirror to transmit human voice over atmospheric air. However, modern solid-state optical wireless communication emerged in the late 1990s and early 2000s following the invention of high-brightness gallium nitride (GaN) blue Light Emitting Diodes by Shuji Nakamura, which catalyzed the global transition from incandescent and fluorescent lighting to energy-efficient solid-state LED illumination.")

    add_body_p(doc, "In 2004, Tanaka, Komine, and Nakagawa at Keio University published seminal foundational papers establishing the feasibility of using domestic white LEDs for simultaneous room lighting and high-speed data communications. They formulated the fundamental optical path loss equations, multi-path reflection models, and signal-to-noise ratio distributions across typical indoor environments. In 2011, Professor Harald Haas coined the term 'Li-Fi' (Light Fidelity) during an internationally acclaimed TED demonstration, highlighting optical wireless networking as an essential 5G/6G complementary technology capable of transforming every overhead light bulb into an ultra-broadband wireless access point.")

    add_body_p(doc, "In recent years, VLC has expanded across diverse operational domains: intelligent transportation systems (vehicle-to-vehicle optical links using LED headlights), underwater wireless telemetry where radio waves suffer severe conductive attenuation, and hospital environments where RF transmission risks disrupting sensitive patient telemetry.")

    add_heading_1(doc, "2.2 IEEE 802.15.7 Physical Layer Standards and Modulation Schemes")
    add_body_p(doc, "To unify disparate industrial and academic optical wireless developments, the IEEE 802.15 working group established the IEEE 802.15.7-2011 standard for Short-Range Optical Wireless Communications Using Visible Light. The standard classifies optical physical layers into three distinct operational profiles:")
    add_bullet_p(doc, "Intended for low-data-rate outdoor applications (11.67 kbps to 266.6 kbps) utilizing On-Off Keying (OOK) and Variable Pulse Position Modulation (VPPM) with mandatory convolutional coding.", "PHY I:")
    add_bullet_p(doc, "Designed for moderate indoor data rates (1.25 Mbps to 96 Mbps) utilizing OOK or VPPM with run-length limited (RLL) line codes and Reed-Solomon Forward Error Correction.", "PHY II:")
    add_bullet_p(doc, "Engineered specifically for multi-color optical sources (such as tri-chromatic RGB LED arrays) utilizing Color Shift Keying (CSK). PHY III achieves high spectral efficiency (12 Mbps to 96 Mbps) by modulating information into the instantaneous color chromaticity of the transmitted light while maintaining strictly constant overall luminous intensity.", "PHY III:")

    add_body_p(doc, "Table 2.1 presents a comparative taxonomy of modulation techniques formalized under IEEE 802.15.7, highlighting the distinct advantages of Color Shift Keying in maintaining human-perceptible illumination stability.")

    table_2_headers = ["Modulation Scheme", "Optical Mechanism", "Bandwidth Efficiency", "Flicker Mitigation", "Primary Implementation Domain"]
    table_2_data = [
        ["On-Off Keying (OOK)", "Direct LED intensity pulsing", "1.0 bps/Hz", "Requires Manchester / 8B10B line coding", "Outdoor / Low-cost links"],
        ["Variable PPM (VPPM)", "Pulse position with pulse width duty cycle", "0.5 - 1.0 bps/Hz", "Inherently integrated into pulse duty cycle", "Dimming-centric applications"],
        ["Color Shift Keying (CSK)", "Instantaneous RGB color coordinates", "2.0 - 4.0 bps/Hz", "Absolute constant optical power invariant", "High-speed multi-color indoor Li-Fi"],
        ["Optical OFDM (DCO/ACO)", "Multi-carrier subcarrier intensity", "3.0 - 6.0 bps/Hz", "Complex analog clipping required", "Advanced multi-user indoor research"],
    ]
    add_table_with_caption(doc, "2.1", "Comparative Taxonomy of Optical Modulation Techniques in IEEE 802.15.7", table_2_headers, table_2_data, [1.4, 1.5, 1.2, 1.3, 1.2])

    add_heading_1(doc, "2.3 Error Control Coding Fundamentals")
    add_body_p(doc, "In optical wireless links, signal propagation is non-coherent: detectors measure instantaneous optical irradiance rather than optical field phase. Consequently, optical channels are vulnerable to intensity variations, ambient solar and fluorescent shot noise, and optical path occlusions. Forward Error Correction (FEC) is the fundamental line of defense ensuring that transmitted frames can be accurately decoded at the receiver without requiring excessive retransmission requests.")

    add_heading_2(doc, "2.3.1 Galois Field GF(2^8) Arithmetic")
    add_body_p(doc, "Reed-Solomon codes operate over finite fields, universally denoted as Galois Fields GF(q). In byte-oriented communication systems, the field order is selected as q = 2^b = 2^8 = 256. Every element in GF(2^8) is uniquely represented either as an 8-bit binary vector (b_7, b_6, ..., b_0) or as a degree-7 polynomial over the binary field GF(2):")

    make_equation_box(doc, "a(x) = a_7 x^7 + a_6 x^6 + a_5 x^5 + a_4 x^4 + a_3 x^3 + a_2 x^2 + a_1 x + a_0, \\quad a_i \\in \\{0, 1\\}", "2.1")

    add_body_p(doc, "Field addition and subtraction in GF(2^8) are mathematically identical and correspond to bitwise exclusive-OR (XOR) operations. However, field multiplication requires polynomial multiplication followed by polynomial division modulo an irreducible, primitive field generator polynomial p(x). In accordance with standard IEEE communication specifications, the primitive polynomial is chosen as:")

    make_equation_box(doc, "p(x) = x^8 + x^4 + x^3 + x^2 + 1 \\quad (\\text{Binary: } 100011101_2 = 0\\text{x}11D)", "2.2")

    table_22_headers = ["Galois Field Property", "Mathematical Value", "Binary / Hex Representation", "Engineering Role in Codec"]
    table_22_data = [
        ["Field Characteristic", "p = 2", "Modulo 2 arithmetic", "Ensures addition equals bitwise XOR"],
        ["Field Order (Cardinality)", "q = 2^8 = 256", "Byte-sized symbols (0 to 255)", "Direct mapping to standard byte memory"],
        ["Primitive Polynomial p(x)", "x^8 + x^4 + x^3 + x^2 + 1", "0x11D (285 decimal)", "Defines non-zero cyclic group multiplication"],
        ["Primitive Element alpha", "Root of p(x) (x = 2)", "0x02", "Generates all 255 non-zero field elements"],
        ["Multiplication Mechanics", "alpha^i . alpha^j = alpha^{(i+j) mod 255}", "Log / Anti-Log LUTs", "Accelerates hardware/software multiplication"],
    ]
    add_table_with_caption(doc, "2.2", "Galois Field GF(2^8) Primitive Polynomial and Characteristic Properties", table_22_headers, table_22_data, [1.5, 1.4, 1.4, 2.3])

    add_heading_2(doc, "2.3.2 Reed-Solomon Algebraic Structure and Generator Polynomials")
    add_body_p(doc, "A Reed-Solomon code, designated as RS(N, K), takes an input message vector consisting of K information symbols in GF(2^8) and appends 2t parity symbols to construct a codeword of length N = 255 symbols. The error correction capability t is strictly bounded by the Singleton bound, establishing RS codes as Maximum Distance Separable (MDS) codes: d_{min} = N - K + 1 = 2t + 1. The code can correct up to t arbitrary symbol errors occurring anywhere within the 255-byte block.")

    add_body_p(doc, "The encoding process is defined by the generator polynomial g(x), whose roots are consecutive powers of the primitive element alpha in GF(2^8):")

    make_equation_box(doc, "g(x) = \\prod_{j=0}^{2t-1} (x - \\alpha^j) = (x - 1)(x - \\alpha)(x - \\alpha^2) \\cdots (x - \\alpha^{2t-1})", "2.3")

    add_body_p(doc, "In systematic encoding, the message polynomial m(x) is shifted by multiplying by x^{2t}, and divided by g(x). The remainder polynomial b(x) = (m(x) x^{2t}) mod g(x) forms the parity block:")

    make_equation_box(doc, "c(x) = m(x) x^{2t} + b(x) = m(x) x^{2t} + \\left[ m(x) x^{2t} \\pmod{g(x)} \\right]", "2.4")

    add_heading_2(doc, "2.3.3 Syndrome Computation and Berlekamp-Massey Decoding")
    add_body_p(doc, "When the transmitted codeword c(x) traverses the impaired optical channel, it is corrupted by an error polynomial e(x), resulting in the received polynomial r(x) = c(x) + e(x). At the optical receiver, the Reed-Solomon decoder executes a four-stage algebraic decoding algorithm:")
    add_bullet_p(doc, "The decoder computes 2t syndrome values by evaluating r(x) at the 2t roots of g(x): S_i = r(alpha^i) = e(alpha^i) for i in {0, 1, ..., 2t-1}. If all syndromes are zero, the received block contains zero errors and passes immediately.", "1. Syndrome Evaluation:")
    add_bullet_p(doc, "If non-zero syndromes exist, the decoder determines the error locator polynomial Lambda(x) = prod_{l=1}^v (1 - X_l x) using the Berlekamp-Massey iterative shift-register synthesis algorithm.", "2. Error Locator Synthesis:")
    add_bullet_p(doc, "The Chien search algorithm evaluates Lambda(x) across all elements alpha^{-j} for j in {0, 1, ..., N-1}. A zero evaluation Lambda(alpha^{-j}) = 0 identifies an error at symbol index j.", "3. Chien Search:")
    add_bullet_p(doc, "Forney's algebraic formula evaluates the error evaluator polynomial Omega(x) to compute the exact error magnitude Y_l at each identified error location, correcting the corrupted symbols.", "4. Forney Algorithm:")

    table_23_headers = ["Decoding Stage", "Core Algorithm", "Computational Complexity", "Software Execution Bottleneck"]
    table_23_data = [
        ["Syndrome Calculation", "Direct polynomial evaluation", "O(2t . N)", "Inner loop field multiplications"],
        ["Key Equation Solver", "Berlekamp-Massey Algorithm", "O(t^2)", "Iterative discrepancy calculations"],
        ["Root Finding", "Chien Exhaustive Search", "O(t . N)", "Evaluation across all 255 field elements"],
        ["Magnitude Calculation", "Forney Algebraic Formula", "O(t^2)", "Polynomial derivative divisions in GF(2^8)"],
    ]
    add_table_with_caption(doc, "2.3", "Algorithmic Complexity of Reed-Solomon Decoding Architectures", table_23_headers, table_23_data, [1.4, 1.5, 1.4, 2.3])

    add_heading_1(doc, "2.4 Channel Estimation and Error Vector Magnitude (EVM) Metrics")
    add_body_p(doc, "Dynamic adaptation requires real-time knowledge of channel quality. In coherent radio systems, pilot subcarriers and channel state information (CSI) estimators are universally employed. However, in low-complexity optical wireless links, dedicated pilot transmissions consume valuable throughput. A highly effective metric for blind channel quality estimation in constellation-based optical communications is the Error Vector Magnitude (EVM).")

    add_body_p(doc, "Let s_k = [r_k, g_k, b_k]^T denote the ideal, transmitted 4-CSK reference constellation vector, and let hat{s}_k = [hat{r}_k, hat{g}_k, hat{b}_k]^T denote the noisy constellation vector recovered at the receiver. The root-mean-square (RMS) Error Vector Magnitude computed over a block of N_s symbols is defined as:")

    make_equation_box(doc, "\\text{EVM}_{RMS} = \\sqrt{ \\frac{\\frac{1}{N_s} \\sum_{k=1}^{N_s} \\| \\widehat{\\mathbf{s}}_k - \\mathbf{s}_k \\|^2}{\\frac{1}{N_s} \\sum_{k=1}^{N_s} \\| \\mathbf{s}_k \\|^2} }", "2.5")

    add_body_p(doc, "Under the assumption of additive white Gaussian noise (AWGN) and memoryless receiver demapping, the instantaneous Signal-to-Noise Ratio (SNR) in decibels is inversely related to EVM via the theoretical formulation:")

    make_equation_box(doc, "\\widehat{\\text{SNR}}_{dB} \\approx -20 \\log_{10}\\left( \\text{EVM}_{RMS} \\right) - \\Delta_{cal} \\quad [\\text{dB}]", "2.6")

    add_body_p(doc, "where Delta_{cal} is a small empirical calibration offset accounting for optical photodiode responsivity scaling and non-linearities. This mathematical formulation allows the receiver to estimate link SNR directly from constellation scatter without requiring dedicated training sequences.")

    add_heading_1(doc, "2.5 Adaptive Modulation and Coding (AMC) in Optical Networks")
    add_body_p(doc, "Adaptive Modulation and Coding (AMC) has been extensively explored in cellular LTE/5G and satellite communications. In optical wireless networks, early AMC research focused on rate-adaptive On-Off Keying and adaptive optical OFDM subcarrier bit loading. However, bit-loaded optical OFDM incurs severe Peak-to-Average Power Ratios (PAPR), requiring high-precision digital-to-analog converters and suffering from LED non-linear distortion. In contrast, adaptive Reed-Solomon coding over Color Shift Keying preserves constant optical emitter current while adapting error protection exclusively at the data-link layer.")

    add_heading_1(doc, "2.6 Gap Analysis and Summary of Identified Research Opportunities")
    add_body_p(doc, "A comprehensive review of existing optical wireless literature reveals significant gaps in current approaches:")
    add_bullet_p(doc, "Most published literature evaluates static Reed-Solomon coding under idealized, time-invariant AWGN channels, ignoring dynamic human blockage and LED dimming.", "Gap 1: Absence of Dynamic AMC in IEEE 802.15.7 CSK:")
    add_bullet_p(doc, "Prior adaptive schemes rely purely on instantaneous SNR, resulting in frequent, unstable profile oscillations ('ping-pong effect') near switching thresholds.", "Gap 2: Vulnerability to Channel Oscillation:")
    add_bullet_p(doc, "Existing adaptive systems frequently assume perfect Channel State Information (CSI) at the transmitter, overlooking realistic receiver estimation latency and noise.", "Gap 3: Unrealistic Channel Estimation Assumptions:")

    add_body_p(doc, "This Mini Project directly addresses these identified research gaps by developing a robust, multi-indicator adaptive controller that integrates sliding-window EVM estimation, dual-threshold hysteresis stabilization, and explainable multi-metric escalation triggers.")

    print("Chapters 1 & 2 built successfully.")
