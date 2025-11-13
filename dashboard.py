import streamlit as st
import pandas as pd
import json
from pathlib import Path
import time
import matplotlib.pyplot as plt
import numpy as np
import random  

# --- Page Configuration ---
st.set_page_config(
    page_title="Healthcare Asset Tracker",
    page_icon="♿",
    layout="wide"
)

DATA_FILE = "asset_data.json"

# --- 🎯 CALIBRATION & ZONE DEFINITIONS ---
# Enhanced colors and solid lines
ZONE_DEFINITIONS = [
    # {name, rssi_threshold, plot_radius, color, border_color}
    {"name": "0m - 3m Zone", "rssi_threshold": -55, "radius": 1, "color": "#76D7C4", "border_color": "#28B463"}, # Light Teal / Emerald
    {"name": "3m - 7m Zone", "rssi_threshold": -70, "radius": 3, "color": "#F7DC6F", "border_color": "#F39C12"}, # Light Yellow / Orange
    {"name": "7m - 10m Zone", "rssi_threshold": -85, "radius": 4, "color": "#F1948A", "border_color": "#CB4335"}, # Light Red / Dark Red
    {"name": ">10m Zone", "rssi_threshold": -100, "radius": 5, "color": "#C6D2DE99", "border_color": "#AAB7B8"}  # Light Gray / Medium Gray
]

# --- Function to load data ---
def load_data():
    """Loads the latest asset data from our JSON file."""
    data_path = Path(DATA_FILE)
    if data_path.is_file():
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError:
            return {}
    return {}

# --- Function to process asset data ---
def get_asset_zone_info(rssi):
    """
    Takes a raw RSSI value and returns the correct zone info
    by checking against the ZONE_DEFINITIONS.
    """
    for zone in ZONE_DEFINITIONS:
        if rssi > zone["rssi_threshold"]:
            return zone
    # If RSSI is very weak or unknown, return the last zone
    return ZONE_DEFINITIONS[-1] 

# --- Function to create the Zone Map diagram ---
def create_zone_map_diagram(asset_data):
    """
    Uses Matplotlib to draw a concentric circle diagram of asset zones.
    """
    
    # --- Create the Plot ---
    # Set figure and axes background to transparent
    fig, ax = plt.subplots(figsize=(9, 9), facecolor='none') 
    ax.set_aspect('equal')
    ax.set_facecolor('none')
    
    # Draw circles from largest to smallest
    for zone in reversed(ZONE_DEFINITIONS): # Reversed() draws largest first
        r = zone["radius"]
        fill_color = zone["color"]
        edge_color = zone["border_color"] # Use the new border_color
        
        ax.add_patch(plt.Circle((0, 0), r, color=fill_color, alpha=0.8, ec=edge_color, lw=1)) # Solid line, thicker
        
        # Add a text label for the distance, positioned slightly off-center
        distance_label = zone["name"].split(' ')[0] 
        ax.text(r - 0.2, 0.2, f"{distance_label}", ha='right', fontsize=9, fontweight='bold', rotation=90, color='darkslategray') # Darker text for contrast


    # Draw the center "Receiver"
    ax.add_patch(plt.Circle((0, 0), 0.2, color="#2A2CBC", alpha=0.8, ec='white', lw=1.5)) # Brighter blue, white border
    ax.text(0, 0, "R", ha='center', va='center', fontsize=9, color='white', fontweight='bold')

    # --- Plot the Assets in their zones ---
    assets_with_plot_info = []
    for asset_id, data in asset_data.items():
        rssi = data.get("rssi", -100) # Default to weakest
        zone_info = get_asset_zone_info(rssi)
        assets_with_plot_info.append({"id": asset_id, "zone": zone_info})

    # Plot assets, staggering them to avoid overlap
    assets_by_radius = {}
    for asset in assets_with_plot_info:
        r = asset["zone"]["radius"]
        if r not in assets_by_radius:
            assets_by_radius[r] = []
        assets_by_radius[r].append(asset["id"])

    # This logic places assets in their rings
    for r, asset_ids in assets_by_radius.items():
        # Find the inner radius of this ring
        inner_r = 0
        for zone in ZONE_DEFINITIONS:
            if zone["radius"] == r:
                break
            inner_r = zone["radius"]
        
        # Position assets vertically within their ring
        y_pos_start = (r + inner_r) / 2.0
        num_assets = len(asset_ids)
        y_positions = np.linspace(y_pos_start, y_pos_start - (num_assets * 0.5) + 0.5, num_assets)
        
        for i, asset_id in enumerate(asset_ids):
            y = y_positions[i]
            if num_assets > 1 : # slight horizontal jitter to avoid overlap
                 x = random.uniform(-0.5, 0.5) 
            else:
                 x = 0
            # Use a dark background for asset labels for better contrast
            ax.text(x, y, f"♿ {asset_id}", ha='center', va='center', fontsize=9, 
                    bbox=dict(boxstyle="round,pad=0.3", fc="#34495E00", ec="white", lw=1.0, alpha=0.2), # Darker background, white border
                    color='white', fontweight='bold') # White text

    # Set plot limits
    max_radius = ZONE_DEFINITIONS[-1]["radius"]
    ax.set_xlim(-max_radius - 1, max_radius + 1)
    ax.set_ylim(-max_radius - 2.0, max_radius + 0.0)
    
    # Hide the axes
    ax.axis('off')
    
    return fig

# --- The Dashboard App ---

st.title("IoT in Healthcare: Real-Time Asset Tracker")
# Load the data
asset_data = load_data()

if not asset_data:
    st.warning("No asset data found. Is the `dummy_data_generator.py` script running?")
else:
    # --- Create the two-column layout ---
    col1, col2 = st.columns([1, 2]) # 1/3 width for metrics, 2/3 for map

    # --- Column 1: Status Metrics ---
    with col1:
        st.subheader("Asset Status")
        
        # Process data to get zone info for metrics
        assets_with_zone_info = []
        for asset_id, data in asset_data.items():
            rssi = data.get("rssi", -100)
            zone_info = get_asset_zone_info(rssi)
            assets_with_zone_info.append({
                "id": asset_id,
                "zone_name": zone_info["name"],
                "rssi": rssi,
                "last_seen": data.get("last_seen", "Never")
            })

        for asset in assets_with_zone_info:
            st.metric(
                label=f"Asset: {asset['id']}",
                value=asset['zone_name'], # e.g., "< 3m Zone"
                delta=f"RSSI: {asset['rssi']} dBm"
            )
            st.caption(f"Last Seen: {asset['last_seen']}")
            st.divider()

    # --- Column 2: The Visual Zone Map ---
    with col2:
        st.subheader("Live Asset Location Diagram")
        
        # Generate and display the Matplotlib figure
        map_diagram = create_zone_map_diagram(asset_data)
        st.pyplot(map_diagram)

# --- Auto-refresh the page ---
time.sleep(5)
st.rerun()