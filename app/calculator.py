"""
BDE 计算核心逻辑
Bond Dissociation Energy Calculator
"""

# 1 Hartree = 627.509 kcal/mol
HARTREE_TO_KCAL = 627.509
# 1 kcal = 4.184 kJ
KCAL_TO_KJ = 4.184


class BDECalculator:
    """BDE 计算器"""

    @staticmethod
    def calculate_bde(
        e_sp_rx: float,
        g_corr_rx: float,
        e_sp_r: float,
        g_corr_r: float,
        e_sp_x: float,
        g_corr_x: float,
    ) -> dict:
        """
        计算 BDE (键解离能)

        参数:
            e_sp_rx  : 分子 RX 的高精度单点能 (Hartree)
            g_corr_rx: 分子 RX 的吉布斯自由能校正 (Hartree)
            e_sp_r   : 自由基 R· 的高精度单点能 (Hartree)
            g_corr_r : 自由基 R· 的吉布斯自由能校正 (Hartree)
            e_sp_x   : 自由基 X· 的高精度单点能 (Hartree)
            g_corr_x : 自由基 X· 的吉布斯自由能校正 (Hartree)

        返回:
            包含 BDE 及相关中间结果的字典
        """
        # 计算各物种的吉布斯自由能 G = E_sp + G_corr
        g_rx = e_sp_rx + g_corr_rx
        g_r  = e_sp_r  + g_corr_r
        g_x  = e_sp_x  + g_corr_x

        # BDE = G(R·) + G(X·) - G(RX)   (单位: Hartree)
        bde_hartree = g_r + g_x - g_rx

        # 换算为 kcal/mol 和 kJ/mol
        bde_kcal = bde_hartree * HARTREE_TO_KCAL
        bde_kj   = bde_kcal * KCAL_TO_KJ

        return {
            "bde_hartree": bde_hartree,
            "bde_kcal": bde_kcal,
            "bde_kj": bde_kj,
            "g_rx": g_rx,
            "g_r": g_r,
            "g_x": g_x,
            "e_sp_rx": e_sp_rx,
            "g_corr_rx": g_corr_rx,
            "e_sp_r": e_sp_r,
            "g_corr_r": g_corr_r,
            "e_sp_x": e_sp_x,
            "g_corr_x": g_corr_x,
        }

    @staticmethod
    def format_result(result: dict, name_rx: str = "RX", name_r: str = "R·", name_x: str = "X·") -> str:
        """将计算结果格式化为可读字符串"""
        lines = []
        lines.append("=" * 55)
        lines.append("              BDE 计算结果")
        lines.append("=" * 55)
        lines.append("")
        lines.append(f"  反应:  {name_rx}  →  {name_r}  +  {name_x}")
        lines.append("")

        lines.append("  ┌─ 各物种吉布斯自由能 (G = E_sp + G_corr) ──────")
        lines.append(f"  │  G({name_rx:>6s}) = {result['e_sp_rx']:.8f} + {result['g_corr_rx']:.8f} = {result['g_rx']:.8f} Hartree")
        lines.append(f"  │  G({name_r:>6s}) = {result['e_sp_r']:.8f} + {result['g_corr_r']:.8f} = {result['g_r']:.8f} Hartree")
        lines.append(f"  │  G({name_x:>6s}) = {result['e_sp_x']:.8f} + {result['g_corr_x']:.8f} = {result['g_x']:.8f} Hartree")
        lines.append("  └────────────────────────────────────────────────")
        lines.append("")

        lines.append("  ┌─ BDE 计算 ────────────────────────────────────")
        lines.append(f"  │  BDE = G({name_r}) + G({name_x}) - G({name_rx})")
        lines.append(f"  │      = {result['g_r']:.8f} + {result['g_x']:.8f} - {result['g_rx']:.8f}")
        lines.append(f"  │      = {result['bde_hartree']:.8f}  Hartree")
        lines.append("  └────────────────────────────────────────────────")
        lines.append("")

        lines.append(f"  >> BDE = {result['bde_kcal']:>10.4f}  kcal/mol")
        lines.append(f"  >> BDE = {result['bde_kj']:>10.4f}  kJ/mol")
        lines.append("")
        lines.append("=" * 55)
        return "\n".join(lines)
