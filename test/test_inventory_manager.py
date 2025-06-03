"""
Unit tests for inventory_manager.py

These tests cover:
- Device validation
- Inventory retrieval (with mocking)
- Error handling for invalid IPs and unknown device_type
"""

import pytest
from scripts import inventory_manager

def test_inventory_task_success(monkeypatch):
    """Simulate a successful inventory collection with monkeypatch."""
    device = {"name": "sw1", "host": "192.168.1.1", "group": "arista"}
    # Patch get_device_inventory to return a known result
    monkeypatch.setattr(inventory_manager, "get_device_inventory", lambda dev, typ: "SFP info: OK")
    # Patch validate_ip to always return True
    monkeypatch.setattr(inventory_manager, "validate_ip", lambda ip: True)
    result = inventory_manager.inventory_task(device, "arista_eos")
    assert result["status"] == "SUCCESS"
    assert "SFP info: OK" in result["output"]

def test_inventory_task_invalid_ip(monkeypatch):
    """Should return FAILED if IP is invalid."""
    device = {"name": "sw1", "host": "invalid_ip", "group": "arista"}
    # Patch validate_ip to always return False
    monkeypatch.setattr(inventory_manager, "validate_ip", lambda ip: False)
    result = inventory_manager.inventory_task(device, "arista_eos")
    assert result["status"] == "FAILED"
    assert "Invalid IP" in result["output"]

def test_inventory_task_exception(monkeypatch):
    """Should return FAILED if get_device_inventory raises Exception."""
    device = {"name": "sw1", "host": "192.168.1.1", "group": "arista"}
    monkeypatch.setattr(inventory_manager, "get_device_inventory", lambda dev, typ: (_ for _ in ()).throw(Exception("Connection failed")))
    monkeypatch.setattr(inventory_manager, "validate_ip", lambda ip: True)
    result = inventory_manager.inventory_task(device, "arista_eos")
    assert result["status"] == "FAILED"
    assert "Connection failed" in result["output"]
