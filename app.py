import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# Set page layout to centered
st.set_page_config(page_title="PARTNERS CUP 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# Optimized CSS for glassmorphic design
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0b0f19; }
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(23, 29, 41, 0.92) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 24px !important;
        backdrop-filter: blur(15px);
        max-width: 480px !important;
        margin: 20px auto !important;
    }
    .branding-title { font-size: 28px; font-weight: 800; color: #ffffff; text-align: center; }
    div[data-testid="stCustomComponentV1"] {
        width: 100% !important;
        height: 290px !important;
        border-radius: 20px !important;
        border: 3px solid #10b981 !important;
        overflow: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="branding-title">PARTNERS CUP <span style="color:#facc15;">2026</span></div>', unsafe_allow_html=True)
st.markdown("---")

# CONFIGURATION
# IMPORTANT: Ensure this ID matches your specific Google Sheet URL characters
SPREADSHEET_ID = "1PUcUeTApYbCjYbkEn9BzItRjRArLKMVnIqz_7Mtd7-w" 
GAS_URL = "https://script.google.com/macros/s/AKfycby-xHIDB9hv5yaFWl99g4aq15__thpMQRj37NAYvJ0g1ogsiI-jnRGtHwYMfXdhFEkvCw/exec"

# State Management
if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False

# Logic
def fetch_sheet_data():
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
        df = pd.read_csv(csv_url, header=None)
        return df.values.tolist()
    except Exception:
        return []

# App Interface
if not st.session_state.active_scan_completed:
    st.markdown("<p style='text-align:center; color:#9ca3af;'>Align QR code in the window below:</p>", unsafe_allow_html=True)
    scanned_raw = qrcode_scanner(key='live_marshal_camera_engine')
    if scanned_raw:
        st.success(f"Detected: {scanned_raw}")
        st.session_state.active_scan_completed = True
        st.rerun()
else:
    if st.button("Scan Another Player"):
        st.session_state.active_scan_completed = False
        st.rerun()
