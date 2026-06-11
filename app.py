import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# 1. Page Configuration
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# 2. Styling
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-image: url('https://lh3.googleusercontent.com/d/1Ta76TkvnUcNszyAPIsmob0oCMoMFzbTC'); background-size: cover; background-repeat: no-repeat; background-attachment: fixed; background-position: center; }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(23, 29, 41, 0.92) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 24px !important;
        backdrop-filter: blur(15px);
        max-width: 480px !important;
        margin: 20px auto !important;
    }
    .branding-container { text-align: center; margin-bottom: 20px; }
    .branding-title { font-family: sans-serif; font-size: 30px; font-weight: 800; color: #ffffff; }
    .branding-subtitle { font-size: 13px; font-weight: 700; color: #10b981; letter-spacing: 2px; text-transform: uppercase; }
    div[data-testid="stCustomComponentV1"] {
        width: 100% !important; height: 290px !important;
        border-radius: 20px !important; border: 3px solid #10b981 !important;
        overflow: hidden !important; background-color: #111827;
    }
    .badge-container { background: rgba(0, 0, 0, 0.4); padding: 20px; border-radius: 14px; border: 1px solid #10b981; text-align: center; margin-top: 10px; }
    .badge-number { font-size: 46px; font-weight: 800; color: #facc15; }
    </style>
""", unsafe_allow_html=True)

# 3. Configuration & State
GAS_URL = "https://script.google.com/macros/s/AKfycby-xHIDB9hv5yaFWl99g4aq15__thpMQRj37NAYvJ0g1ogsiI-jnRGtHwYMfXdhFEkvCw/exec"
SPREADSHEET_ID = "1PUcUeTApYbCjYbkEn9BzItRjRArLKMVnIqz_7Mtd7-w"

if "active_scan_completed" not in st.session_state: st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state: st.session_state.display_payload = {}

# 4. Data Engine (With "Fail-Safe" Loading)
@st.cache_data(ttl=60)
def fetch_sheet_data():
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
        # Increase timeout to prevent "hanging"
        df = pd.read_csv(csv_url, header=None, on_bad_lines='skip') 
        return df.values.tolist()
    except Exception as e:
        return [f"ERROR: {str(e)}"]

# 5. UI Rendering
st.markdown("""<div class="branding-container"><div class="branding-title">FDG CUP 2026</div><div class="branding-subtitle">Gate Marshal Portal</div></div>""", unsafe_allow_html=True)

# Main Flow
all_records = fetch_sheet_data()

if len(all_records) > 0 and isinstance(all_records[0], str) and "ERROR" in all_records[0]:
    st.error("⚠️ Connection Error. Please check Google Sheet ID.")
    st.write(all_records[0])
    st.stop() # Prevents app from baking if data fails

if st.session_state.active_scan_completed:
    payload = st.session_state.display_payload
    if payload.get("status") == "SUCCESS":
        st.success("✓ Access Authorized")
        st.markdown(f'<div class="badge-container"><div class="badge-number">BAG #{payload["bag"]}</div><p>{payload["name"]}</p></div>', unsafe_allow_html=True)
    else:
        st.error("⚠️ Already Checked In")
    if st.button("📷 Scan Next Player"):
        st.session_state.active_scan_completed = False
        st.rerun()
else:
    scanned_raw = qrcode_scanner(key='live_marshal_camera_engine')
    if scanned_raw:
        try:
            parts = scanned_raw.split("-")
            row_id = int(parts[1])
            if 0 <= row_id < len(all_records):
                player_row = all_records[row_id]
                player_name = f"{player_row[1]} {player_row[0]}"
                attendance_status = str(player_row[6]).strip()

                if attendance_status == "Checked-In":
                    st.session_state.display_payload = {"status": "DUPLICATE", "name": player_name}
                else:
                    try:
                        requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": row_id}, timeout=5)
                    except:
                        pass # Continue even if gas is slow
                    st.session_state.display_payload = {"status": "SUCCESS", "name": player_name, "bag": player_row[5]}
                
                st.session_state.active_scan_completed = True
                st.rerun()
            else:
                st.error("Invalid QR Code ID.")
        except Exception as e:
            st.error(f"Scan Parsing Error: {e}")
