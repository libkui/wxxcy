from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable

from netmiko import ConnectHandler

from devices import DEVICES


BACKUP_BASE_DIR = Path("/home/osmgr/Network_Device_Configuration_Backup")


def _safe_filename(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "unknown"
    return re.sub(r'[\\/:*?"<>|]+', "_", value)


def backup_huawei_config(device: Dict[str, Any]) -> Path:
    switch_ip = device["SWITCH_IP"]
    device_name = device.get("Device_name") or switch_ip
    device_type = device.get("device_type", "huawei")
    username = device["USERNAME"]
    password = device["PASSWORD"]
    port = device.get("PORT", 22)

    conn = ConnectHandler(
        device_type=device_type,
        host=switch_ip,
        username=username,
        password=password,
        port=port,
        conn_timeout=15,
        timeout=60,
        global_delay_factor=2,
    )

    conn.send_command("screen-length 0 temporary")
    cfg = conn.send_command(
        "display current-configuration",
        expect_string=r"return",
        read_timeout=120,
    )
    conn.disconnect()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{_safe_filename(device_name)}_{switch_ip}_{ts}.cfg"

    date_dir = datetime.now().strftime("%Y-%m-%d")
    backup_dir = BACKUP_BASE_DIR / date_dir
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / filename
    backup_path.write_text(cfg, encoding="utf-8")
    return backup_path


def backup_all_devices(devices: Iterable[Dict[str, Any]] = DEVICES) -> None:
    for device in devices:
        backup_path = backup_huawei_config(device)
        print(f"Backup OK -> {backup_path}")


if __name__ == "__main__":
    backup_all_devices()

