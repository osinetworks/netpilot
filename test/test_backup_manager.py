"""
Unit tests for backup_manager.py

These tests focus on:
- Correct validation of device data
- Exception handling for invalid IPs
- Simulated backup process (Netmiko should be mocked in real tests)
"""

import pytest
from scripts import backup_manager


def test_validate_ip_valid():
    """Should return True for valid IP formats"""

    assert backup_manager.validate_ip("192.168.1.100") is True
    assert backup_manager.validate_ip("10.10.10.10") is True


def test_validate_ip_invalid():
    """Should return False for invalid IP formats"""

    assert backup_manager.validate_ip("999.999.999.999") is False
    assert backup_manager.validate_ip("abc.def.ghi.jkl") is False
    assert backup_manager.validate_ip("192,168,1,1") is False


def test_backup_task_invalid_ip(monkeypatch):
    """Should return FAILED and error message for invalid IP"""

    device = {"name": "SW1", "host": "999.999.999.999", "group": "arista"}
    result = backup_manager.backup_task(device, "arista_eos")
    assert result["status"] == "FAILED"
    assert "Invalid IP" in result["output"]


def test_backup_task_no_device_type(monkeypatch):
    """Should return FAILED status for unknown device_type"""
    device = {"name": "SW2", "host": "192.168.1.1", "group": "unknown"}
    result = backup_manager.backup_task(device, "unknown_device_type")
    assert result["status"] == "FAILED"
    assert "no backup commands file" in result["output"].lower()


def test_backup_task_mocked(monkeypatch):
    """
    Simulate a successful backup with mocked backup_device_config.
    This prevents actual SSH sessions during unit test runs.
    """

    device = {"name": "SW3", "host": "192.168.1.10", "group": "arista"}
    def fake_backup(dev, devtype):
        return (["/tmp/fake_running.txt", "/tmp/fake_startup.txt"], "OK")
    monkeypatch.setattr(backup_manager, "backup_device_config", fake_backup)
    result = backup_manager.backup_task(device, "arista_eos")
    assert result["status"] == "SUCCESS"
    assert result["files"] == ["/tmp/fake_running.txt", "/tmp/fake_startup.txt"]
    assert result["output"] == "OK"

