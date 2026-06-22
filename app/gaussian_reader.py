"""
Gaussian 输出文件解析器
从 .log / .out 文件中提取单点能 (E_sp) 和热力学校正-焓 (H_corr)
"""

import re
from typing import Optional


def parse_gaussian_file(filepath: str) -> dict:
    """
    解析 Gaussian 输出文件，提取能量数据。

    返回:
        {
            "e_sp": float or None,      # 最后一个 SCF Done 的能量 (Hartree)
            "h_corr": float or None,    # Thermal correction to Enthalpy (Hartree)
            "method": str or None,      # 计算方法 (如 RB3LYP)
            "route": str or None,       # 完整 Route 行 (如 # opt=calcfc freq def2svp em=gd3 m062x)
        }
    """
    result: dict = {"e_sp": None, "h_corr": None, "g_corr": None, "method": None, "route": None}

    # 匹配文件开头 # 开头的 Route 行（可能跨多行）
    route_pattern = re.compile(
        r"^\s*(#.*?)(?=\n\s*\n|\n[^\s#]|\Z)", re.MULTILINE | re.DOTALL
    )

    # 也匹配 Route card: 后面的内容
    route_card_pattern = re.compile(
        r"Route card:\s*\*\*?\s*(.*)", re.IGNORECASE
    )

    # 匹配: SCF Done:  E(RB3LYP) = -345.67890123     A.U.
    scf_pattern = re.compile(
        r"SCF\s+Done:\s+E\(([^)]+)\)\s*=\s*([-]?\d+\.\d+)"
    )

    # 匹配: Thermal correction to Enthalpy=                    0.131234
    hcorr_pattern = re.compile(
        r"Thermal correction to Enthalpy=\s+([-]?\d+\.\d+)"
    )

    # 匹配: Thermal correction to Gibbs Free Energy=          0.132345
    gcorr_pattern = re.compile(
        r"Thermal correction to Gibbs Free Energy=\s+([-]?\d+\.\d+)"
    )

    # 备选匹配: Sum of electronic and thermal Enthalpies=    -345.547667
    sum_pattern = re.compile(
        r"Sum of electronic and thermal Enthalpies=\s+([-]?\d+\.\d+)"
    )

    # 备选匹配: Sum of electronic and thermal Free Energies= -345.546556
    sumg_pattern = re.compile(
        r"Sum of electronic and thermal Free Energies=\s+([-]?\d+\.\d+)"
    )

    encoding = _detect_encoding(filepath)

    try:
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            content = f.read()
    except Exception:
        return result

    # 提取 Route 行（完整计算级别）
    route = _extract_route(content)
    if route:
        result["route"] = route

    # 查找所有 SCF Done（取最后一个，即优化收敛后的结果）
    scf_matches = scf_pattern.findall(content)
    if scf_matches:
        last_method, last_esp = scf_matches[-1]
        result["e_sp"] = float(last_esp)
        result["method"] = last_method

    # 查找 H_corr（取最后一个）
    hcorr_matches = hcorr_pattern.findall(content)
    if hcorr_matches:
        result["h_corr"] = float(hcorr_matches[-1])

    # 查找 G_corr（取最后一个）
    gcorr_matches = gcorr_pattern.findall(content)
    if gcorr_matches:
        result["g_corr"] = float(gcorr_matches[-1])

    # 如果没找到 H_corr，但有 E_sp 和 Sum Enthalpies，反推 H_corr
    if result["h_corr"] is None and result["e_sp"] is not None:
        sum_matches = sum_pattern.findall(content)
        if sum_matches:
            e_sum = float(sum_matches[-1])
            result["h_corr"] = round(e_sum - result["e_sp"], 8)

    # 如果没找到 G_corr，但有 E_sp 和 Sum Free Energies，反推 G_corr
    if result["g_corr"] is None and result["e_sp"] is not None:
        sumg_matches = sumg_pattern.findall(content)
        if sumg_matches:
            e_sum = float(sumg_matches[-1])
            result["g_corr"] = round(e_sum - result["e_sp"], 8)

    # 如果 SCF Done 没找到，尝试从 Sum + H_corr 反推 E_sp
    if result["e_sp"] is None and result["h_corr"] is not None:
        sum_matches = sum_pattern.findall(content)
        if sum_matches:
            e_sum = float(sum_matches[-1])
            result["e_sp"] = round(e_sum - result["h_corr"], 8)

    return result


def _detect_encoding(filepath: str) -> str:
    """检测文件编码，优先 utf-8，回退到 gbk"""
    import chardet
    try:
        with open(filepath, "rb") as f:
            raw = f.read(4096)
        detected = chardet.detect(raw)
        return detected.get("encoding", "utf-8") or "utf-8"
    except ImportError:
        return "utf-8"


def _extract_route(content: str) -> Optional[str]:
    """从 Gaussian 输出文件内容中提取 Route 行（只取用户写的 # 行部分）"""
    # 匹配 Route card: **# ... 行本身（只取该行内容）
    m = re.search(r"Route card:\s*\*?\*?\s*(#.*)", content, re.IGNORECASE)
    if m:
        route = m.group(1).strip()
        # 去掉末尾可能残留的符号（如换行前的空格）
        route = route.split("\n")[0].strip()
        # 只保留 # 开头的第一段（遇到路由指令 /1 就截断）
        if route:
            return route

    # 备选：匹配 # 开头的行（单行，不跨行）
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped

    return None
