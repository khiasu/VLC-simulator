# Project Review 2 - Table of Contents (TOC) Plan

## 1. Introduction
- 1.1 Project Aim: Adaptive Visible Light Communication (VLC) Simulator
- 1.2 Motivation: Demand for high-speed indoor communication and RF spectrum congestion
- 1.3 Problem Statement

## 2. Literature Survey
- 2.1 Existing VLC Channel Models
- 2.2 Limitations of Current Systems (Lack of adaptive end-to-end simulators)

## 3. Project Objectives
- 3.1 Implement FEC coding (Reed-Solomon) and Modulation (CSK)
- 3.2 Develop Realistic Indoor Optical Channel Model
- 3.3 Channel Quality Estimation
- 3.4 Adaptive Control for Dynamic Adjustment

## 4. Proposed Methodology (System Architecture)
- 4.1 Transmitter Design (Data generation, RS Encoder, Mapper)
- 4.2 Channel Modeling (LoS, dimming, crosstalk, noise)
- 4.3 Receiver Design (Demapper, RS Decoder)
- 4.4 Feedback Loop and Adaptive Control Logic

## 5. Description of Core Modules
- 5.1 `channel_quality_estimator.py`: SNR and state estimation
- 5.2 `adaptive_controller.py`: Dynamic adjustments based on feedback
- 5.3 `rs_codec.py`: Forward Error Correction
- 5.4 `csk_mapper.py`: Color Shift Keying Modulation
- 5.5 `optical_channel.py`: Channel noise and impairments
- 5.6 `simulation_runner.py` & `experiments.py`: Batch simulation and benchmarking
*(Note: Dashboard module is explicitly excluded from this review)*

## 6. Simulation Setup and Metrics
- 6.1 Configuration Parameters (SNR ranges, Packet Iterations, Target FER)
- 6.2 Evaluation Metrics: BER, FER, Goodput

## 7. Results and Expected Outcomes
- 7.1 BER vs. SNR Performance Graphs
- 7.2 Goodput and Throughput Analysis under varying conditions
- 7.3 Demonstration of Adaptive Control advantages over fixed profiles

## 8. Conclusion and Future Work
- 8.1 Summary of Deliverables
- 8.2 Future Scope (e.g., Deep Reinforcement Learning Agent integration)
