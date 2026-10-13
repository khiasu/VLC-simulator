import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from config import SystemConfig

def render_performance_charts(df_history: pd.DataFrame, event_logs: list):
    """
    Renders synchronized Plotly line charts for SNR, Goodput, and FER/BER.
    Includes vertical event markers for Adaptive RS profile switches.
    """
    if df_history is None or df_history.empty:
        return go.Figure()
        
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Channel Condition (SNR)", "Goodput Performance", "Error Rates (FER / BER)")
    )
    
    # ----------------------------------------------------
    # Chart 1: Real-time SNR (dB)
    # ----------------------------------------------------
    if 'true_snr' in df_history.columns:
        fig.add_trace(
            go.Scatter(x=df_history['frame_idx'], y=df_history['true_snr'], name="True SNR", line=dict(color='#ff9900', width=2)),
            row=1, col=1
        )
    if 'estimated_snr' in df_history.columns:
        fig.add_trace(
            go.Scatter(x=df_history['frame_idx'], y=df_history['estimated_snr'], name="EVM-Estimated SNR", line=dict(color='#ffcc66', width=1, dash='dot')),
            row=1, col=1
        )
        
    # ----------------------------------------------------
    # Chart 2: Goodput (Overlays baselines if they exist)
    # ----------------------------------------------------
    if 'strategy' in df_history.columns:
        strategies = df_history['strategy'].unique()
        colors = {
            'Adaptive_RS': '#00cc44', 
            'Static_Strong': '#e60000', 
            'Static_Medium': '#ff9900', 
            'Static_Weak': '#3399ff', 
            'Uncoded': '#999999'
        }
        
        for strat in strategies:
            strat_df = df_history[df_history['strategy'] == strat]
            color = colors.get(strat, '#ffffff')
            width = 3 if strat == 'Adaptive_RS' else 1.5
            dash = 'solid' if strat == 'Adaptive_RS' else 'dash'
            
            fig.add_trace(
                go.Scatter(x=strat_df['frame_idx'], y=strat_df['goodput'], name=f"GP: {strat}", line=dict(color=color, width=width, dash=dash)),
                row=2, col=1
            )

    # ----------------------------------------------------
    # Chart 3: FER and BER (Log Scale)
    # ----------------------------------------------------
    # Filter for Adaptive (or just plot whatever is available if it's a single run)
    target_df = df_history[df_history['strategy'] == 'Adaptive_RS'] if 'Adaptive_RS' in df_history['strategy'].values else df_history
    
    if not target_df.empty:
        fig.add_trace(
            go.Scatter(x=target_df['frame_idx'], y=target_df['fer'], name="Frame Error Rate", line=dict(color='#ff3333', width=2)),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=target_df['frame_idx'], y=target_df['ber'], name="Bit Error Rate", line=dict(color='#33ccff', width=1, dash='dot')),
            row=3, col=1
        )
        
    # Reference Line for TARGET_FER
    fig.add_hline(y=SystemConfig.TARGET_FER, line_dash="dash", line_color="#ff0000", annotation_text="Target FER (1%)", row=3, col=1)

    # ----------------------------------------------------
    # Event Markers (Vertical Lines for Code Switches)
    # ----------------------------------------------------
    for event in event_logs:
        frame_idx = event.get('frame_idx')
        switch_type = event.get('type', 'SWITCH') 
        
        if "UPGRADE" in switch_type:
            color = "#00cc44"  # Green for going to faster code
        elif "DOWNGRADE" in switch_type or "ESCALATION" in switch_type:
            color = "#ff3333"  # Red for retreating to safer code
        else:
            color = "#ffff00"  # Yellow fallback
            
        for row in [1, 2, 3]:
            fig.add_vline(x=frame_idx, line_width=1.5, line_dash="dash", line_color=color, opacity=0.7, row=row, col=1)
            
    # Layout adjustments
    fig.update_layout(
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Configure axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    
    fig.update_yaxes(title_text="SNR (dB)", row=1, col=1)
    fig.update_yaxes(title_text="Goodput (kbps)", row=2, col=1)
    
    # Log scale for error rates because they span 1.0 to 1e-6
    fig.update_yaxes(title_text="Error Rate", type="log", row=3, col=1, range=[-5, 0]) 
    
    return fig

def render_constellation_scatter(tx_symbols: np.ndarray, rx_symbols: np.ndarray):
    """
    Renders 3D Scatter plot of Ideal RGB vectors vs Received Noisy RGB vectors.
    """
    if tx_symbols is None or rx_symbols is None:
        return go.Figure()
        
    fig = go.Figure()
    
    # Draw received symbols (noisy scatter cloud)
    fig.add_trace(go.Scatter3d(
        x=rx_symbols[:, 0], y=rx_symbols[:, 1], z=rx_symbols[:, 2],
        mode='markers',
        marker=dict(size=2, color='rgba(200, 200, 200, 0.4)'),
        name='Received (Noisy)'
    ))
    
    # Draw transmitted symbols (Ideal anchors) and color them by their actual RGB value!
    colors = [f'rgb({int(r*255)},{int(g*255)},{int(b*255)})' for r, g, b in tx_symbols]
    fig.add_trace(go.Scatter3d(
        x=tx_symbols[:, 0], y=tx_symbols[:, 1], z=tx_symbols[:, 2],
        mode='markers',
        marker=dict(size=8, color=colors, symbol='diamond', line=dict(width=2, color='white')),
        name='Ideal Constellation'
    ))
    
    fig.update_layout(
        title="4-CSK RGB Vector Space",
        scene=dict(
            xaxis_title="Red", yaxis_title="Green", zaxis_title="Blue",
            xaxis=dict(range=[0, 1]), yaxis=dict(range=[0, 1]), zaxis=dict(range=[0, 1])
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def render_threshold_state(current_snr: float, thresholds: dict):
    """
    Visualizes the current SNR on a gauge chart with dynamically colored threshold zones.
    """
    # Extract valid thresholds (ignore infinities)
    valid_thresholds = {k: v for k, v in thresholds.items() if v not in [999.0, -999.0]}
    sorted_items = sorted(valid_thresholds.items(), key=lambda x: x[1])
    
    steps = []
    if not sorted_items:
        steps = [{'range': [0, 25], 'color': 'gray'}]
    else:
        last_val = 0
        # Color gradient: Dark Red (Strong Code) -> Green (Uncoded)
        colors = ['#800000', '#cc0000', '#ff9900', '#99cc00', '#009933']
        c_idx = 0
        
        # From 0 to first threshold
        steps.append({'range': [0, sorted_items[0][1]], 'color': colors[0]})
        last_val = sorted_items[0][1]
        
        # Intermediate thresholds
        for k, v in sorted_items[1:]:
            c_idx = min(c_idx + 1, len(colors) - 1)
            steps.append({'range': [last_val, v], 'color': colors[c_idx]})
            last_val = v
            
        # Final threshold to 25dB
        c_idx = min(c_idx + 1, len(colors) - 1)
        steps.append({'range': [last_val, 25], 'color': colors[c_idx]})
        
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_snr,
        title={'text': "Current Estimated SNR (dB)", 'font': {'size': 16}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 25], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "white", 'thickness': 0.1},
            'steps': steps,
            'threshold': {
                'line': {'color': "cyan", 'width': 4},
                'thickness': 0.75,
                'value': current_snr
            }
        }
    ))
    
    fig.update_layout(
        height=250, 
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig
