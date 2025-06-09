# netpilot_gui.py

import streamlit as st
import datetime
import csv
import yaml
import io
import os
from scripts import config_manager, backup_manager, inventory_manager, firmware_manager
from scripts.constants import (
    DEVICES_FILE_PATH, 
    BACKUP_FOLDER_PATH, 
    ERROR_LOG_PATH, 
    CONFIG_RESULT_FILE_PATH, 
    COMMANDS_PATHS,
    BACKUP_COMMANDS_PATHS
)

st.set_page_config(page_title="Netpilot Automation Suite", layout="centered")

# Sidebar page selector
page = st.sidebar.selectbox(
    "Select Page",
    ("Main", "Show Backup Files", "Show Error Log"),
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
        with st.expander(f"Show content of {fname}"):
            st.code(file_bytes.decode(errors='replace'))


#--- Show Error Log PAGE ---
def show_error_log():
    st.header("Error Log Viewer")
    log_path = ERROR_LOG_PATH
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log_content = f.read()
        if not log_content:
            st.info("No errors found in error.log.")
        else:
            # Satırları tersten sırala (en yeni yukarıda)
            reversed_log = "\n".join(log_content.strip().splitlines()[::-1])
            st.markdown(
                """
                <style>
                .stTextArea, .stTextArea textarea, .stCodeBlock {
                    width: 100% !important;
                    min-width: 100% !important;
                    max-width: 100% !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.text_area(
                label="Error Log",
                value=reversed_log,
                height=600,
                label_visibility="hidden"
            )
            st.download_button("Download error.log", log_content, file_name=ERROR_LOG_PATH, mime="text/plain")
    else:
        st.warning("Error log file not found.")


# --- Main PAGE ---
if page == "Main":
    st.title("Netpilot Automation Suite")
    st.markdown("A simple web-based automation panel for your network tasks.")

    log_panel = st.empty()

    def log(message, level="info"):
        """Log message to the UI panel."""
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
                # After running, check if any device had a failure and inform user accordingly
                try:
                    if os.path.exists(CONFIG_RESULT_FILE_PATH):
                        with open(CONFIG_RESULT_FILE_PATH, "r") as f:
                            results = yaml.safe_load(f)
                        failed = [r for r in results if r.get("status") != "SUCCESS"]
                        if failed:
                            log("Some devices failed! Please check the error log in the 'Show Error Log' section button/tab for details.", "error")
                        else:
                            log("Configuration deployed successfully!", "success")
                    else:
                        log("Result file not found! Check logs.", "error")
                except Exception as e:
                    log(f"Could not verify results: {e}", "warn")
            except Exception as e:
                log(f"Config Error: {e}", "error")

    with col2:
        if st.button("Run Backup Task"):
            st.session_state["log_lines"] = []
            log("Starting backup...", "info")
            try:
                results, any_failed = backup_manager.main()
                log("Backup collection completed!", "success")
                if any_failed:
                    log("Some devices failed! Please check the error log in the 'Show Error Log' section button/tab for details.", "error")
                    st.error("Some devices failed backup! Please check the error log in the 'Show Error Log' tab.")
                else:
                    log("Backup completed successfully!", "success")
                    st.success("Backup completed successfully!")
            except Exception as e:
                log(f"Backup Error: {e}", "error")

    with col3:
        if st.button("Inventory Collection"):
            st.session_state["log_lines"] = []
            log("Collecting inventory...", "info")
            try:
                results, any_failed = inventory_manager.main()
                log("Inventory collection completed!", "success")
                if any_failed:
                    log("Some devices failed! Please check the error log in the 'Show Error Log' section button/tab for details.", "error")
                    st.error("Some devices failed inventory collection! Please check the error log in the 'Show Error Log' tab.")
                else:
                    log("Inventory collection completed successfully!", "success")
                    st.success("Inventory collection completed successfully!")
            except Exception as e:
                log(f"Inventory Error: {e}", "error")

    with col4:
        if st.button("Firmware Upgrade"):
            st.session_state["log_lines"] = []
            log("Starting firmware upgrade.", "info")
            try:
                results, any_failed = firmware_manager.main()
                log("Firmware upgrade completed!", "success")
                if any_failed:
                    log("Some devices failed! Please check the error log in the 'Show Error Log' section button/tab for details.", "error")
                    st.error("Some devices failed firmware upgrade! Please check the error log in the 'Show Error Log' tab.")
                else:
                    log("Firmware upgrade completed successfully!", "success")
                    st.success("Firmware upgrade completed successfully!")
            except Exception as e:
                log(f"Firmware Error: {e}", "error")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns([2, 10, 1, 1])

    with col1:
        if st.button("Clear Log"):
            st.session_state["log_lines"] = []
            log_panel.markdown("Log cleared.")

    with col2:
        if st.button("Show Error Log"):
            show_error_log()

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

    # Unified file uploader for config/backup commands

    st.markdown("#### Upload Command File by Vendor and Type")

    # Vendor selection from constants
    vendors = list(set(list(COMMANDS_PATHS.keys()) + list(BACKUP_COMMANDS_PATHS.keys())))
    vendor_labels = {v: v.replace("_eos", "").replace("_ios", "").capitalize() for v in vendors}
    selected_vendor = st.selectbox("Select Vendor", vendors, format_func=lambda x: vendor_labels[x])

    # File type selection
    cmd_type = st.selectbox("Select File Type", ["Config", "Backup"])

    # Determine expected filename and save path from constants
    if cmd_type == "Config":
        file_dict = COMMANDS_PATHS
        file_type_label = "Config"
    else:
        file_dict = BACKUP_COMMANDS_PATHS
        file_type_label = "Backup"

    expected_filename = os.path.basename(file_dict[selected_vendor])
    save_path = file_dict[selected_vendor]

    # Show existing commands if file exists
    existing_content = ""
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            existing_content = f.read()

    # Editable text area with existing content (can be empty)
    st.markdown(f"##### Edit current {file_type_label} commands for {vendor_labels[selected_vendor]}")
    updated_content = st.text_area(
        f"Commands in {expected_filename}",
        value=existing_content,
        height=200,
        key=f"{selected_vendor}_{cmd_type}_editor"
    )

    # Save edited commands button
    if st.button(f"Save {file_type_label} Commands"):
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "w") as f:
                f.write(updated_content)
            st.success(f"{expected_filename} saved to: {save_path}")
        except Exception as e:
            st.error(f"Failed to save file: {e}")

    # File uploader for config/backup commands
    uploaded_cmd = st.file_uploader(
        f"Upload {file_type_label} File (Expected: {expected_filename})", type=["cfg"], key=f"upload_{selected_vendor}_{cmd_type}"
    )
    if uploaded_cmd is not None:
        if uploaded_cmd.name != expected_filename:
            st.error(f"Invalid file name: Please upload '{expected_filename}' for vendor '{vendor_labels[selected_vendor]}'!")
        else:
            try:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(uploaded_cmd.getvalue())
                st.success(f"{expected_filename} saved to: {save_path}")
            except Exception as e:
                st.error(f"Failed to save file: {e}")

  
# --- Show Backup Files PAGE ---
elif page == "Show Backup Files":
    show_backup_files()
# --- Show Error Log PAGE ---
elif page == "Show Error Log":
    show_error_log()
