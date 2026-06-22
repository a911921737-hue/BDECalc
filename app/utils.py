"""
工具函数：文件读写、历史记录管理
"""

import json
import os
import sys
from datetime import datetime
from typing import Optional

# 全局配置路径（%APPDATA%/BDE-Calculator/config.json），指向真实的 data 目录
_CONFIG_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "BDE-Calculator"
)
_CONFIG_FILE = os.path.join(_CONFIG_DIR, "config.json")


def _get_data_dir() -> str:
    """
    数据目录查找策略：
    1. 读取 %APPDATA%/BDE-Calculator/config.json 中记录的 data_dir
    2. 没有则用 exe 旁边的 data/（首次运行会自动创建）
    """
    # 优先读全局配置
    if os.path.exists(_CONFIG_FILE):
        try:
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            d = cfg.get("data_dir", "")
            if d:
                return d
        except Exception:
            pass

    # 兜底：exe 旁边的 data/
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(exe_dir, "data")


def _save_data_dir(data_dir: str):
    """把 data 目录写入全局配置（首次写入后不再覆盖）"""
    try:
        os.makedirs(_CONFIG_DIR, exist_ok=True)
        if not os.path.exists(_CONFIG_FILE):
            with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"data_dir": data_dir}, f)
    except Exception:
        pass


# 初始化数据目录
HISTORY_DIR = _get_data_dir()
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")

# 如果是 frozen 模式，写入全局配置（供复制到桌面后使用）
if getattr(sys, "frozen", False):
    _save_data_dir(HISTORY_DIR)


def ensure_history_dir():
    """确保历史记录目录存在"""
    os.makedirs(HISTORY_DIR, exist_ok=True)


def save_to_history(record: dict):
    """保存一条计算记录到历史"""
    ensure_history_dir()
    records = load_history()
    record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records.append(record)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return record["timestamp"]


def load_history() -> list:
    """加载所有历史记录"""
    ensure_history_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []


def delete_history(index: int) -> bool:
    """删除指定索引的历史记录"""
    records = load_history()
    if 0 <= index < len(records):
        records.pop(index)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return True
    return False


def clear_history():
    """清空所有历史记录"""
    ensure_history_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
