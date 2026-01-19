from netmiko import ConnectHandler
from datetime import datetime
from pathlib import Path

SWITCH_IP = "12.0.99.2"
Device_name = "政务外网边界网关节点-01"
USERNAME = "huawei"
PASSWORD = "Wxxcy#$2025"
PORT = 22

def backup_huawei_config():
    device = {
        "device_type": "huawei",   # 华为VRP
        "host": SWITCH_IP,
        "username": USERNAME,
        "password": PASSWORD,
        "port": PORT,
        "conn_timeout": 15,
        "timeout": 60,             # 命令整体超时
        "global_delay_factor": 2,  # 设备慢/网络抖时可调大
    }

    conn = ConnectHandler(**device)

    # 关闭分页，避免 --More-- 卡住
    conn.send_command("screen-length 0 temporary")

    # （可选）先保存一次启动配置（不想保存可注释掉）
    # 有的设备用 save 需要交互确认，这里用 save force 省交互
    # conn.send_command("save force", expect_string=r">|]")

    # 导出当前配置
    cfg = conn.send_command(
        "display current-configuration",
        expect_string=r">|]",
        read_timeout=120
    )

    conn.disconnect()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{Device_name}_{SWITCH_IP}_{ts}.cfg"

    date_dir = datetime.now().strftime("%Y-%m-%d")
    backup_dir = Path("/home/osmgr/Network_Device_Configuration_Backup") / date_dir
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / filename

    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(cfg)

    print(f"Backup OK -> {backup_path}")

if __name__ == "__main__":
    backup_huawei_config()

