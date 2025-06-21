# netpilot_gui.py

import streamlit as st
import datetime
import time
import csv
import yaml
import io
import os
import pandas as pd

from scripts import config_manager, backup_manager, inventory_manager, firmware_manager
from scripts.constants import (
    DEVICES_FILE_PATH, 
    BACKUP_FOLDER_PATH, 
    ERROR_LOG_PATH, 
    CONFIG_RESULT_FILE_PATH, 
    CONFIG_COMMANDS_PATHS,
    BACKUP_RESULT_FILE_PATH,
    BACKUP_COMMANDS_PATHS,
    CONFIG_BUTTON,
    BACKUP_BUTTON,
    INVENTORY_BUTTON,
    FIRMWARE_BUTTON,
    CLEAR_LOGS_BUTTON,
    SHOW_ERRORS_BUTTON,
    INVENTORY_RESULT_FILE_PATH,
    FIRMWARE_RESULT_FILE_PATH,
)
from utils.logger_utils import setup_logger, parse_log
from utils.network_utils import validate_ip, is_reachable
from scripts.config_parser import load_yaml

st.set_page_config(page_title="Netpilot Automation Suite", layout="centered")

# Sidebar page selector
page = st.sidebar.selectbox(
    "Select Page",
    ("Main", "Show Backup Files", "Show Error Log", "Run Command"),
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
    st.markdown("#### Error Log Viewer")
    log_path = ERROR_LOG_PATH
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log_content = f.read()
        if not log_content:
            st.info("No errors found in error.log.")
        else:
            # Line reversal for better readability
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
            st.download_button("Download error.log", log_content, file_name=log_path, mime="text/plain")
    else:
        st.warning("Error log file not found.")

def show_task_progress(devices):
    st.info("Task started...")

    progress_bar = st.progress(0)
    status_placeholder = st.empty()

    for i, device in enumerate(devices):
        status_placeholder.write(f"Progress: {device.get('name')}")
        time.sleep(1)
        progress_bar.progress((i + 1) / len(devices))


def show_task_results_table(task_result_path, task_type="config"):
    """
    Show results in a colored, filterable table.
    :param task_result_path: Path to the YAML result file.
    :param task_type: For labeling.
    """
    try:
        with open(task_result_path, "r") as f:
            results = yaml.safe_load(f)
    except Exception as e:
        st.warning(f"Could not read {task_type} results: {e}")
        return

    if not results:
        st.info(f"No results found for {task_type} task.")
        return

    #  Prepare data for display
    table_data = []
    for item in results:
        color = "🟢" if item.get("status") == "SUCCESS" else "🔴"
        table_data.append({
            "Device": item.get("device"),
            "IP": item.get("host"),
            "Status": color + " " + item.get("status", ""),
            "Message": item.get("output", "")[:100],  # first 100 chars
        })
    st.write(f"### {task_type.capitalize()} Task Results")
    st.dataframe(table_data, use_container_width=True)

    # Filter for failed devices only
    failed = [i for i in results if i.get("status") != "SUCCESS"]
    if failed:
        st.error(f"{len(failed)} device(s) failed. Check error log for details.")

def show_error_msg_table():
    """Show error messages in a table: Time, Device, Error"""
    st.write("### Error Messages")
    try:
        with open(ERROR_LOG_PATH, "r") as f:
            error_log_content = f.read()
        if not error_log_content.strip():
            st.info("No errors found in the error log.")
            return
    except Exception as e:
        st.warning(f"Could not read error log: {e}")
        return

    error_messages = []
    for line in error_log_content.strip().splitlines():
        # Log format: "2025-06-21 11:56:26,825 ERROR [backup_manager]: Device not reachable for device cisco-sw-001: 10.10.10.11"
        try:
            # Split time and rest
            result = parse_log(line)
            # Device and error part
            timestamp = result.get("timestamp")
            log_level = result.get("error_level", "ERROR")
            function = result.get("function")
            error_message = result.get("error_message")
            ip_address = result.get("ip_address")
            error_messages.append({
                "Time": timestamp.strip(),
                "Function": function.strip(),
                "Device": ip_address,
                "Error": error_message
            })
        except Exception:
            # if line is not in expected format, skip it
            continue

    # Pandas DataFrame for better display
    if not error_messages:
        st.info("No valid error messages found.")
        return

    df = pd.DataFrame(error_messages)
    # for better readability, reverse the order
    df = df.iloc[::-1]

    # Streamlit dataframe with custom styling
    st.dataframe(
        df,
        use_container_width=True,
        height=450,     # Adjust as needed
        hide_index=True
    )


# --- Main PAGE ---
if page == "Main":
    st.title("Netpilot Automation Suite")
    st.markdown("A simple web-based automation panel for your network tasks.")
    
    log_panel = st.empty()
    selected_button = None
    devices_yaml = load_yaml(DEVICES_FILE_PATH)
    devices_list = devices_yaml.get("devices", [])
    
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

    # --- BACKUP, INVENTORY, FIRMWARE UPGRADE TASKS ---
    st.markdown("### Automation Tasks")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(CONFIG_BUTTON):
            selected_button = CONFIG_BUTTON

    with col2:
        if st.button(BACKUP_BUTTON):
            selected_button = BACKUP_BUTTON

    with col3:
        if st.button(INVENTORY_BUTTON):
            selected_button = INVENTORY_BUTTON

    with col4:
        if st.button(FIRMWARE_BUTTON):
            selected_button = FIRMWARE_BUTTON

    if selected_button == CONFIG_BUTTON:
        st.session_state["log_lines"] = []
        show_task_progress(devices_list)
        try:
            logger = setup_logger("config_manager")
            logger.info("Config task started")

            show_task_results_table(CONFIG_RESULT_FILE_PATH, task_type="config")
            config_manager.main()

            logger.info("Config task completed")
            # After running, check if any device had a failure and inform user accordingly
            if os.path.exists(CONFIG_RESULT_FILE_PATH):
                with open(CONFIG_RESULT_FILE_PATH, 'r') as f:
                    results = yaml.safe_load(f) or []

                failed_devices = [r for r in results if r.get("status") == "FAILED"]
                successful_devices = [r for r in results if r.get("status") == "SUCCESS"]
                if failed_devices:
                    log("Some devices failed! Please check the error log in the 'Show Error Log' section button/tab for details.", "error")
                else:
                    st.success("Config completed successfully for all devices!")
                    log("Config completed successfully for all devices!", "success")
            else:
                st.success("Config completed, but no result file found.")
        except Exception as e:
            st.error(f"Config Error: {e}")
            with st.expander("Show Error Log", expanded=True):
                show_error_log()

    elif selected_button == BACKUP_BUTTON:
        st.session_state["log_lines"] = []
        show_task_progress(devices_list)
        try:
            logger = setup_logger("backup_manager")
            logger.info("Backup task started")

            show_task_results_table(BACKUP_RESULT_FILE_PATH, task_type="backup")
            backup_manager.main()

            logger.info("Backup task completed")
            # After running, check if any device had a failure and inform user accordingly
            if os.path.exists(BACKUP_RESULT_FILE_PATH):
                with open(BACKUP_RESULT_FILE_PATH, 'r') as f:
                    results = yaml.safe_load(f) or []

                failed_devices = [r for r in results if r.get("status") == "FAILED"]
                successful_devices = [r for r in results if r.get("status") == "SUCCESS"]
                if failed_devices:
                    log("Some devices failed! Please check the error log in the 'Show Error Log' section button/tab for details.", "error")
                else:
                    st.success("Backup completed successfully for all devices!")
                    log("Backup completed successfully for all devices!", "success")
            else:
                st.success("Backup completed, but no result file found.")
        except Exception as e:
            st.error(f"Backup Error: {e}")
            with st.expander("Show Error Log", expanded=True):
                show_error_log()

    # --- INVENTORY COLLECTION TASK ---
    elif selected_button == INVENTORY_BUTTON:
        st.session_state["log_lines"] = []
        show_task_progress(devices_list)
        try:
            logger = setup_logger("inventory_manager")
            logger.info("Inventory task started")

            show_task_results_table(INVENTORY_RESULT_FILE_PATH, task_type="inventory")
            inventory_manager.main()
            
            logger.info("Inventory task completed")
            # After running, check if any device had a failure and inform user accordingly
            if os.path.exists(INVENTORY_RESULT_FILE_PATH):
                with open(INVENTORY_RESULT_FILE_PATH, 'r') as f:
                    results = yaml.safe_load(f) or []

                failed_devices = [r for r in results if r.get("status") == "FAILED"]
                successful_devices = [r for r in results if r.get("status") == "SUCCESS"]
                if failed_devices:
                    log("Some devices failed! Please check the error log in the 'Show Error Log' section button/tab for details.", "error")
                else:
                    st.success("Inventory collection completed successfully for all devices!")
                    log("Inventory collection completed successfully for all devices!", "success")
            else:
                st.success("Inventory collection completed, but no result file found.")
        except Exception as e:
            st.error(f"Inventory Error: {e}")
            with st.expander("Show Error Log", expanded=True):
                show_error_log()
    
    # --- FIRMWARE UPGRADE TASK ---
    elif selected_button == FIRMWARE_BUTTON:
        st.session_state["log_lines"] = []
        show_task_progress(devices_list)
        try:
            logger = setup_logger("firmware_manager")
            logger.info("Firmware task started")

            show_task_results_table(FIRMWARE_RESULT_FILE_PATH, task_type="firmware")
            firmware_manager.main()

            logger.info("Firmware task completed")
            # After running, check if any device had a failure and inform user accordingly
            if os.path.exists(FIRMWARE_RESULT_FILE_PATH):
                with open(FIRMWARE_RESULT_FILE_PATH, 'r') as f:
                    results = yaml.safe_load(f) or []

                failed_devices = [r for r in results if r.get("status") == "FAILED"]
                successful_devices = [r for r in results if r.get("status") == "SUCCESS"]
                if failed_devices:
                    log("Some devices failed! Please check the error log in the 'Show Error Log' section button/tab for details.", "error")
                else:
                    st.success("Firmware upgrade completed successfully for all devices!")
                    log("Firmware upgrade completed successfully for all devices!", "success")
            else:
                st.success("Firmware upgrade completed, but no result file found.")
        except Exception as e:
            st.error(f"Firmware Upgrade Error: {e}")
            with st.expander("Show Error Log", expanded=True):
                show_error_log()

    st.markdown("---")
    # --- LOG PANEL ---
    col1, col2, col3, col4 = st.columns([2, 10, 1, 1])
    with col1:
        if st.button(CLEAR_LOGS_BUTTON):
            st.session_state["log_lines"] = []
            log_panel.markdown("Log cleared.")

    with col2:
        if st.button(SHOW_ERRORS_BUTTON):
            show_error_msg_table()
            #show_error_log()

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
    vendors = list(set(list(CONFIG_COMMANDS_PATHS.keys()) + list(BACKUP_COMMANDS_PATHS.keys())))
    vendor_labels = {v: v.replace("_eos", "").replace("_ios", "").capitalize() for v in vendors}
    selected_vendor = st.selectbox("Select Vendor", vendors, format_func=lambda x: vendor_labels[x])

    # File type selection
    cmd_type = st.selectbox("Select File Type", ["Config", "Backup"])

    # Determine expected filename and save path from constants
    if cmd_type == "Config":
        file_dict = CONFIG_COMMANDS_PATHS
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
    #show_error_log()
    show_error_msg_table()
elif page == "Run Command":
    ip = st.text_input("Device IP Address:")
    if not ip:
        st.warning("Please enter a device IP address.")
    
    if not validate_ip(ip):
        st.warning(f"Invalid IP address: {ip}")

    if not is_reachable(ip):
        st.warning(f"IP not reachable on port 22: {ip}")

    command = st.text_area("Send Command:")
    if st.button("Send Command"):
        if command:
            st.success("Command sent.")
        else:
            st.error("Command cannot be empty.")

