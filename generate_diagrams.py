import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("figures", exist_ok=True)
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 10})

def generate_pipeline_diagram():
    """Generates clean system architecture block diagram."""
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis('off')
    
    # Transmitter blocks (Row 1, Top)
    tx_boxes = [
        ("Application Data\n(Byte Stream)", 0.6, 3.0, 1.8, 0.9, "#d9edf7", "#31708f"),
        ("Frame Manager\n(Header + CRC32)", 2.8, 3.0, 1.8, 0.9, "#d9edf7", "#31708f"),
        ("RS Encoder\n(GF(2^8) FEC)", 5.0, 3.0, 1.8, 0.9, "#dff0d8", "#3c763d"),
        ("4-CSK Mapper\n(IEEE 802.15.7)", 7.2, 3.0, 1.8, 0.9, "#fcf8e3", "#8a6d3b"),
    ]
    
    # Channel Block (Right)
    channel_box = ("Indoor Optical Channel\n(AWGN, Dimming, Crosstalk)", 9.3, 1.6, 1.5, 2.3, "#f2dede", "#a94442")
    
    # Receiver blocks (Row 2, Bottom)
    rx_boxes = [
        ("Recovered Payload\n& Output Metrics", 0.6, 0.5, 1.8, 0.9, "#d9edf7", "#31708f"),
        ("CRC32 Verification\n& Frame Parsing", 2.8, 0.5, 1.8, 0.9, "#d9edf7", "#31708f"),
        ("RS Decoder\n(Error Correction)", 5.0, 0.5, 1.8, 0.9, "#dff0d8", "#3c763d"),
        ("4-CSK Demapper\n(ML Euclidean)", 7.2, 0.5, 1.8, 0.9, "#fcf8e3", "#8a6d3b"),
    ]
    
    # Controller Feedback block (Center)
    ctrl_boxes = [
        ("Channel Quality Estimator\n(EVM to SNR, Sliding FER)", 6.1, 1.7, 2.6, 0.75, "#e8e8e8", "#555555"),
        ("Adaptive Link Controller\n(Hysteresis & Escalation)", 2.5, 1.7, 2.6, 0.75, "#fff2cc", "#d6b656")
    ]
    
    for text, x, y, w, h, bg, border in tx_boxes + [channel_box] + rx_boxes + ctrl_boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15", 
                                      facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=9, fontweight='bold', color=border)
        
    # Arrows Forward (TX)
    arrow_props = dict(arrowstyle="->", color="#333333", lw=1.5)
    ax.annotate("", xy=(2.8, 3.45), xytext=(2.4, 3.45), arrowprops=arrow_props)
    ax.annotate("", xy=(5.0, 3.45), xytext=(4.6, 3.45), arrowprops=arrow_props)
    ax.annotate("", xy=(7.2, 3.45), xytext=(6.8, 3.45), arrowprops=arrow_props)
    ax.annotate("", xy=(9.3, 3.45), xytext=(9.0, 3.45), arrowprops=arrow_props)
    
    # Channel to RX
    ax.annotate("", xy=(9.0, 0.95), xytext=(9.3, 1.6), arrowprops=dict(arrowstyle="->", color="#333333", lw=1.5, connectionstyle="angle,angleA=0,angleB=90,rad=10"))
    
    # Arrows Backward (RX)
    ax.annotate("", xy=(6.8, 0.95), xytext=(7.2, 0.95), arrowprops=arrow_props)
    ax.annotate("", xy=(4.6, 0.95), xytext=(5.0, 0.95), arrowprops=arrow_props)
    ax.annotate("", xy=(2.4, 0.95), xytext=(2.8, 0.95), arrowprops=arrow_props)
    
    # Feedback loop arrows
    ax.annotate("", xy=(7.4, 1.7), xytext=(7.4, 1.4), arrowprops=arrow_props) # Demapper to Estimator
    ax.annotate("", xy=(5.1, 2.07), xytext=(6.1, 2.07), arrowprops=arrow_props) # Estimator to Controller
    ax.annotate("", xy=(3.8, 3.0), xytext=(3.8, 2.45), arrowprops=dict(arrowstyle="->", color="#b27300", lw=1.8, linestyle="--")) # Controller to Framing/RS
    ax.text(3.9, 2.7, "Update RS Profile", fontsize=8, color="#b27300", fontweight='bold')

    plt.tight_layout()
    plt.savefig('figures/fig_pipeline_architecture.png', dpi=300)
    plt.close()
    print("Saved: figures/fig_pipeline_architecture.png")

def generate_frame_format_diagram():
    """Generates Data Link Layer frame structure diagram."""
    fig, ax = plt.subplots(figsize=(10, 2.8), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis('off')
    
    # Total Frame Box
    ax.text(5.0, 2.6, "Data Link Layer Frame Structure (Overhead: 12 Bytes)", ha='center', fontsize=12, fontweight='bold')
    
    fields = [
        ("Frame ID\n(4 Bytes)", 0.5, 0.9, 1.5, 1.2, "#cfe2f3", "#3d85c6"),
        ("Payload Length\n(2 Bytes)", 2.0, 0.9, 1.4, 1.2, "#cfe2f3", "#3d85c6"),
        ("RS Profile ID\n(1 Byte)", 3.4, 0.9, 1.3, 1.2, "#cfe2f3", "#3d85c6"),
        ("Flags\n(1 Byte)", 4.7, 0.9, 1.0, 1.2, "#cfe2f3", "#3d85c6"),
        ("Application Payload\n(Variable K Bytes: Default 223 Bytes)", 5.7, 0.9, 2.8, 1.2, "#d9ead3", "#38761d"),
        ("CRC32 Checksum\n(4 Bytes)", 8.5, 0.9, 1.3, 1.2, "#f4cccc", "#cc0000"),
    ]
    
    for text, x, y, w, h, bg, border in fields:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", 
                                      facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=9, fontweight='bold', color=border)
        
    # Sub-bracket for Header
    ax.annotate("", xy=(0.5, 0.7), xytext=(5.7, 0.7), arrowprops=dict(arrowstyle="<->", color="#3d85c6", lw=1.5))
    ax.text(3.1, 0.4, "8-Byte Structured Frame Header", ha='center', fontsize=9, color="#3d85c6", fontweight='bold')
    
    # Total Frame Bracket
    ax.annotate("", xy=(0.5, 2.2), xytext=(9.8, 2.2), arrowprops=dict(arrowstyle="<->", color="#444444", lw=1.2))
    ax.text(5.15, 2.3, "Total Transmitted Frame (Encapsulated before RS Encoding)", ha='center', fontsize=9, color="#444444")
    
    plt.tight_layout()
    plt.savefig('figures/fig_frame_format.png', dpi=300)
    plt.close()
    print("Saved: figures/fig_frame_format.png")

def generate_flowchart_diagram():
    """Generates Adaptive Controller Decision Flowchart."""
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)
    ax.axis('off')
    
    box_style = dict(boxstyle="round,pad=0.1,rounding_size=0.15", linewidth=1.5)
    
    # Start Block
    rect1 = patches.FancyBboxPatch((3.0, 8.0), 3.0, 0.7, **box_style, facecolor="#e1d5e7", edgecolor="#9673a6")
    ax.add_patch(rect1)
    ax.text(4.5, 8.35, "Receive Channel Feedback\n(EVM-SNR, FER, Streak)", ha='center', va='center', fontsize=9, fontweight='bold', color="#5b3970")
    
    # Decision 1: Escalation
    diamond1 = patches.Polygon([[4.5, 7.5], [6.2, 6.7], [4.5, 5.9], [2.8, 6.7]], closed=True, facecolor="#f8cecc", edgecolor="#b85450", linewidth=1.5)
    ax.add_patch(diamond1)
    ax.text(4.5, 6.7, "Streak >= 2 OR\nRecent FER > 0.1?", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#701815")
    
    # Escalation Action
    rect_esc = patches.FancyBboxPatch((7.0, 6.35), 1.8, 0.7, **box_style, facecolor="#f8cecc", edgecolor="#b85450")
    ax.add_patch(rect_esc)
    ax.text(7.9, 6.7, "ESCALATION\nSet RS(255, 223)", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#701815")
    
    # Decision 2: Upgrade
    diamond2 = patches.Polygon([[4.5, 5.4], [6.2, 4.6], [4.5, 3.8], [2.8, 4.6]], closed=True, facecolor="#d5e8d4", edgecolor="#82b366", linewidth=1.5)
    ax.add_patch(diamond2)
    ax.text(4.5, 4.6, "SNR >= Threshold\n+ 0.5 dB Hysteresis?", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#274e13")
    
    # Upgrade Action
    rect_up = patches.FancyBboxPatch((7.0, 4.25), 1.8, 0.7, **box_style, facecolor="#d5e8d4", edgecolor="#82b366")
    ax.add_patch(rect_up)
    ax.text(7.9, 4.6, "UPGRADE\nSelect Lighter RS", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#274e13")
    
    # Decision 3: Maintain
    diamond3 = patches.Polygon([[4.5, 3.3], [6.2, 2.5], [4.5, 1.7], [2.8, 2.5]], closed=True, facecolor="#fff2cc", edgecolor="#d6b656", linewidth=1.5)
    ax.add_patch(diamond3)
    ax.text(4.5, 2.5, "SNR >= Threshold\n- 0.5 dB Hysteresis?", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#7f6000")
    
    # Maintain Action
    rect_maint = patches.FancyBboxPatch((7.0, 2.15), 1.8, 0.7, **box_style, facecolor="#fff2cc", edgecolor="#d6b656")
    ax.add_patch(rect_maint)
    ax.text(7.9, 2.5, "MAINTAIN\nKeep Active RS", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#7f6000")
    
    # Downgrade Action
    rect_down = patches.FancyBboxPatch((3.5, 0.5), 2.0, 0.7, **box_style, facecolor="#ffe6cc", edgecolor="#d79b00")
    ax.add_patch(rect_down)
    ax.text(4.5, 0.85, "DOWNGRADE\nSelect Stronger RS", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#8c5000")
    
    # Connecting Arrows
    arrow_props = dict(arrowstyle="->", color="#333333", lw=1.5)
    ax.annotate("", xy=(4.5, 7.5), xytext=(4.5, 8.0), arrowprops=arrow_props)
    
    # From Diamond 1: Yes -> Escalate, No -> Diamond 2
    ax.annotate("", xy=(7.0, 6.7), xytext=(6.2, 6.7), arrowprops=arrow_props)
    ax.text(6.5, 6.85, "Yes", fontsize=8.5, fontweight='bold', color="#cc0000")
    ax.annotate("", xy=(4.5, 5.4), xytext=(4.5, 5.9), arrowprops=arrow_props)
    ax.text(4.65, 5.65, "No", fontsize=8.5, fontweight='bold', color="#444444")
    
    # From Diamond 2: Yes -> Upgrade, No -> Diamond 3
    ax.annotate("", xy=(7.0, 4.6), xytext=(6.2, 4.6), arrowprops=arrow_props)
    ax.text(6.5, 4.75, "Yes", fontsize=8.5, fontweight='bold', color="#274e13")
    ax.annotate("", xy=(4.5, 3.3), xytext=(4.5, 3.8), arrowprops=arrow_props)
    ax.text(4.65, 3.55, "No", fontsize=8.5, fontweight='bold', color="#444444")
    
    # From Diamond 3: Yes -> Maintain, No -> Downgrade
    ax.annotate("", xy=(7.0, 2.5), xytext=(6.2, 2.5), arrowprops=arrow_props)
    ax.text(6.5, 2.65, "Yes", fontsize=8.5, fontweight='bold', color="#7f6000")
    ax.annotate("", xy=(4.5, 1.2), xytext=(4.5, 1.7), arrowprops=arrow_props)
    ax.text(4.65, 1.45, "No", fontsize=8.5, fontweight='bold', color="#8c5000")
    
    plt.tight_layout()
    plt.savefig('figures/fig_controller_flowchart.png', dpi=300)
    plt.close()
    print("Saved: figures/fig_controller_flowchart.png")

if __name__ == '__main__':
    generate_pipeline_diagram()
    generate_frame_format_diagram()
    generate_flowchart_diagram()
