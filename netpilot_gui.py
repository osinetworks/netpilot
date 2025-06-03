import streamlit as st
import datetime
import csv
import yaml
import io
import os
from scripts import config_manager, backup_manager, inventory_manager, firmware_manager
from scripts.constants import DEVICES_FILE_PATH, BACKUP_FOLDER_PATH

st.set_page_config(page_title="Netpilot Automation Suite", layout="centered")

# --- Sidebar menü ile sayfa seçimi ---
page = st.sidebar.selectbox(
    "Select Page",
    ("Main", "Show Backup Files"),
    index=0
)

# --- Show Backup Files PAGE ---
def show_backup_files():
    st.header("Available Backup Files")
    files = []
    for fname in os.listdir(BACKUP_FOLDER_PATH):
        fpath = os.path.join(BACKUP_FOLDER_PATH, fname)
        if os.path.isfile(fpath):
            files.append((fname, fpath))
    if not files:
        st.info("No backup files found.")
        return
    for fname, fpath in sorted(files):
        with open(fpath, "rb") as f:
            file_bytes = f.read()
        st.write(f":floppy_disk: **{fname}**")
        st.download_button(
            label="Download",
            data=file_bytes,
            file_name=fname,
            mime="text/plain"
        )
        # Uncomment below to show file content:
        # with st.expander(f"Show content of {fname}"):
        #     st.code(file_bytes.decode(errors='replace'))

# --- Main PAGE ---
if page == "Main":
    st.title("Netpilot Automation Suite")
    st.markdown("A simple web-based automation panel for your network tasks and inventory upload.")

    log_panel = st.empty()

    def log(message, level="info"):
        colors = {"info": "🟦", "success": "🟩", "error": "🟥", "warn": "🟨"}
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state["log_lines"].append(
            f"{colors.get(level,'🟦')} `{ts}` {message}"
        )
        log_panel.markdown("\n".join(st.session_state["log_lines"]), unsafe_allow_html=True)

    if "log_lines" not in st.session_state:
        st.session_state["log_lines"] = []

    st.markdown("### Automation Tasks")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Run Config Task"):
            st.session_state["log_lines"] = []
            log("Starting config deployment...", "info")
            try:
                config_manager.main()
                log("Configuration deployed successfully!", "success")
            except Exception as e:
                log(f"Config Error: {e}", "error")

    with col2:
        if st.button("Backup Devices"):
            st.session_state["log_lines"] = []
            log("Starting device backup...", "info")
            try:
                backup_manager.main()
                log("Backup completed!", "success")
            except Exception as e:
                log(f"Backup Error: {e}", "error")

    with col3:
        if st.button("Inventory Collection"):
            st.session_state["log_lines"] = []
            log("Collecting inventory...", "info")
            try:
                inventory_manager.main()
                log("Inventory collection completed!", "success")
            except Exception as e:
                log(f"Inventory Error: {e}", "error")

    with col4:
        if st.button("Firmware Upgrade"):
            st.session_state["log_lines"] = []
            log("Firmware upgrade not implemented yet.", "warn")
            try:
                firmware_manager.main()
                log("Firmware upgrade completed!", "success")
            except Exception as e:
                log(f"Firmware Error: {e}", "error")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Clear Log"):
            st.session_state["log_lines"] = []
            log_panel.markdown("Log cleared.")

    # --- CSV TO YAML & COMMAND FILE UPLOAD PANEL ---
    st.markdown("---")
    st.header("Device Inventory & Backup Command Upload")

    st.markdown("#### Upload devices.csv (will be converted to devices.yaml)")
    uploaded_csv = st.file_uploader("Upload devices.csv", type=["csv"])
    if uploaded_csv is not None:
        reader = csv.DictReader(io.StringIO(uploaded_csv.getvalue().decode()))
        devices = []
        for row in reader:
            devices.append({
                "name": row.get("name") or row.get("Name"),
                "host": row.get("host") or row.get("Host") or row.get("ip") or row.get("IP"),
                "group": row.get("group") or row.get("Group") or row.get("vendor") or row.get("Vendor")
            })
        if devices:
            yaml_obj = {"devices": devices}
            st.write("devices.yaml preview:")
            st.code(yaml.dump(yaml_obj), language="yaml")
            save_path = DEVICES_FILE_PATH
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "w") as f:
                yaml.dump(yaml_obj, f)
            st.success(f"devices.yaml saved to: {save_path}")

    st.markdown("#### Upload arista_backup_commands.cfg")
    arista_cmd = st.file_uploader("Upload arista_backup_commands.cfg", type=["cfg"])
    if arista_cmd is not None:
        arista_path = os.path.join("config", "commands", "arista_backup_commands.cfg")
        os.makedirs(os.path.dirname(arista_path), exist_ok=True)
        with open(arista_path, "wb") as f:
            f.write(arista_cmd.getvalue())
        st.success(f"arista_backup_commands.cfg saved to: {arista_path}")

    st.markdown("#### Upload cisco_backup_commands.cfg")
    cisco_cmd = st.file_uploader("Upload cisco_backup_commands.cfg", type=["cfg"])
    if cisco_cmd is not None:
        cisco_path = os.path.join("config", "commands", "cisco_backup_commands.cfg")
        os.makedirs(os.path.dirname(cisco_path), exist_ok=True)
        with open(cisco_path, "wb") as f:
            f.write(cisco_cmd.getvalue())
        st.success(f"cisco_backup_commands.cfg saved to: {cisco_path}")

# --- Show Backup Files page ---
elif page == "Show Backup Files":
    show_backup_files()
