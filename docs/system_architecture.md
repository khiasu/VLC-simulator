# System Architecture and Theory of Operation

## 1. Introduction
This documentation details the internal workings of the Channel-Aware Adaptive Reed-Solomon Error Control VLC Simulator. The system is designed to act as an experimental research platform to evaluate the trade-offs between static Forward Error Correction (FEC) and dynamic, adaptive FEC in optical wireless communication.

## 2. The Data Link Layer

### 2.1 Frame Assembly and Integrity Check
Data generation begins at the application layer by creating randomized sequences of bytes (representing payloads like images or text). To ensure reliable transport across the network, these bytes are encapsulated into **Frames** by the `FrameManager`.
*   **Header (8 bytes):** An explicit metadata header identifies the Frame ID, Payload Length, and the active Reed-Solomon Profile Index. This ensures the receiver knows exactly how to decode the incoming data.
*   **CRC32 Checksum (4 bytes):** A Cyclic Redundancy Check is calculated over the payload and appended to the frame. If the optical channel corrupts the data beyond the correction capacity of the Reed-Solomon decoder, the CRC32 check will fail during the parsing phase. This is critical: it ensures bad data is never silently accepted, maintaining the integrity of our Frame Error Rate (FER) calculations.

### 2.2 Dynamic Reed-Solomon (RS) Coding
Reed-Solomon is a block-based error correction code. The simulator defines multiple $(N, K)$ generic profiles over $GF(2^8)$ in the central configuration. For example, a profile of $(255, 223)$ means 223 bytes of payload are protected by 32 bytes of parity.
The `RSCodecManager` is built to dynamically switch these profiles. In a highly degraded channel, it selects a profile with a high parity ratio. In a clean channel, it switches to a weaker code (or "UNCODED") to maximize data throughput (Goodput).

## 3. The Physical Layer

### 3.1 Color Shift Keying (CSK) Modulation
CSK is a modulation scheme defined in the IEEE 802.15.7 standard specifically for visible light communication using multi-color LEDs.
*   The `CSKMapper` translates 2-bit symbols (`00`, `01`, `10`, `11`) into 3D vectors representing normalized Red, Green, and Blue light intensities.
*   A key physical property of CSK is that the total optical power remains constant ($R + G + B = 1.0$), ensuring that the high-speed data transmission does not cause visible flickering to the human eye.

### 3.2 Indoor Optical Channel Impairments
The optical channel model introduces three primary real-world sources of degradation:
1.  **AWGN (Additive White Gaussian Noise):** Simulates ambient light interference (e.g., sunlight, fluorescent bulbs) and photodiode thermal noise based on a defined Signal-to-Noise Ratio (SNR).
2.  **LED Dimming:** Users dim lights for comfort. Dimming scales the amplitude of the RGB signal vector, directly lowering the effective SNR at the receiver and increasing the likelihood of symbol errors.
3.  **RGB Crosstalk:** Photodiodes are imperfect; a receiver's "Red" sensor might erroneously pick up some "Green" light due to overlapping spectral sensitivities. This is modeled mathematically via a $3 \times 3$ crosstalk matrix applied to the transmitted vectors.

## 4. The Adaptive Link Controller (The Research Contribution)
The core research objective of this simulator is the Adaptive Link Controller. It operates as a cross-layer optimizer:
1.  **Observe:** It gathers real-time physical layer metrics (estimated SNR, dimming levels, crosstalk severity) and data link layer metrics (recent CRC failures, number of corrected RS symbols).
2.  **Decide:** It applies a heuristic switching policy (derived experimentally) to determine the absolute optimal $(N, K)$ Reed-Solomon profile for the next frame.
3.  **Act:** It instructs the `RSCodecManager` to update the active profile for subsequent transmissions.

*Note: In the Minor Project phase, this decision-making process is Rule-Based. In the Major Project phase, this module will be completely replaced by a Deep Reinforcement Learning (DRL) agent that learns the optimal policy autonomously.*

## 5. Metrics and Evaluation
The system evaluates performance using three primary networking metrics:
*   **Bit Error Rate (BER):** The ratio of incorrectly received bits to the total transmitted bits, measured immediately after 4-CSK demapping (before any error correction is applied). This measures raw channel quality.
*   **Frame Error Rate (FER):** The percentage of frames that fail the CRC32 check *after* Reed-Solomon decoding. The adaptive system is tightly constrained to keep this below $10^{-2}$.
*   **Goodput:** The rate of error-free, useful payload bits successfully delivered to the application layer. This is the primary optimization target; the adaptive controller aims to maximize Goodput without violating the target FER.
