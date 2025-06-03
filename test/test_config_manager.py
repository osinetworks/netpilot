"""
Unit tests for config_manager.py

Tests cover:
- Validation of device dictionaries (validate_devices)
- Invalid IP and comma error handling
- Mocked config push (run_config_task)
- Loading config commands from file
- Handling of unknown device_type
"""

import pytest
from scripts import config_manager


def test_validate_devices_valid():
    """Devices with correct fields and valid IPs should be returned as valid."""
    devices = [
        {"name": "sw1", "host": "192.168.1.1", "group": "arista"},
        {"name": "sw2", "host": "10.0.0.2", "group": "cisco"}
    ]
    result = config_manager.validate_devices(devices)
    assert result == devices


def test_validate_devices_missing_fields():
    """Devices missing required fields should not be validated."""
    devices = [
        {"host": "192.168.1.1", "group": "arista"},         # missing name
        {"name": "sw2", "group": "cisco"},                  # missing host
        {"name": "sw3", "host": "10.0.0.3"}                 # missing group
    ]
    result = config_manager.validate_devices(devices)
    assert result == []


def test_validate_devices_comma_in_ip():
    """Device with comma instead of dot in IP should not be validated."""
    devices = [
        {"name": "sw1", "host": "192,168,1,1", "group": "arista"}
    ]
    result = config_manager.validate_devices(devices)
    assert result == []


def test_run_config_task_invalid_ip(monkeypatch):
    """run_config_task should fail for invalid IPs."""
    device = {"name": "sw1", "host": "999.999.999.999", "group": "arista"}
    result = config_manager.run_config_task(device, ["dummy"], "arista_eos")
    assert result["status"] == "FAILED"
    assert "Invalid IP" in result["output"]


def test_run_config_task_unreachable(monkeypatch):
    """run_config_task should fail if is_reachable returns False."""
    device = {"name": "sw1", "host": "192.0.2.1", "group": "arista"}
    # Patch is_reachable to always return False
    monkeypatch.setattr(config_manager, "is_reachable", lambda ip, timeout=2: False)
    result = config_manager.run_config_task(device, ["dummy"], "arista_eos")
    assert result["status"] == "FAILED"
    assert "IP not reachable" in result["output"]


def test_run_config_task_success(monkeypatch):
    """run_config_task should succeed if push_config_to_device returns output."""
    device = {"name": "sw1", "host": "192.168.1.1", "group": "arista"}
    monkeypatch.setattr(config_manager, "is_reachable", lambda ip, timeout=2: True)
    monkeypatch.setattr(config_manager, "validate_ip", lambda ip: True)
    monkeypatch.setattr(config_manager, "push_config_to_device", lambda d, c, t: "OK!")
    result = config_manager.run_config_task(device, ["dummy"], "arista_eos")
    assert result["status"] == "SUCCESS"
    assert "OK!" in result["output"]


def test_get_config_commands_valid():
    """Should return command file path for supported device_type."""
    device_type = "arista_eos"
    path = config_manager.get_config_commands(device_type)
    assert isinstance(path, str)
    assert path.endswith("arista_config_commands.cfg")  


def test_get_config_commands_invalid():
    """Should raise ValueError for unsupported device_type."""
    with pytest.raises(ValueError):
        config_manager.get_config_commands("unknown_type")


def test_load_commands(tmp_path):
    """Should load commands from file, skipping blank lines and comments."""
    testfile = tmp_path / "commands.cfg"
    content = """
! comment
vlan 100

interface Ethernet1
! another comment
    """
    testfile.write_text(content)
    commands = config_manager.load_commands(str(testfile))
    assert commands == ["vlan 100", "interface Ethernet1"]

