#!/usr/bin/env python3
"""
BDE 计算器 — 键解离能计算工具
用于计算 Gaussian 等量子化学软件输出的键解离能 (Bond Dissociation Energy)
"""

import sys
import os

# 修复 Windows 下中文/emoji 输出乱码
# 注意: --windowed 打包时 stdout/stderr 为 None，需加守卫
if sys.platform == "win32":
    import io
    if sys.stdout is not None:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if sys.stderr is not None:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 确保可以找到 app 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gui import BDEApp


def main():
    app = BDEApp()
    app.mainloop()


if __name__ == "__main__":
    main()
