"""
BDE 计算器 - 主窗口 GUI (Apple 风格)
"""

import customtkinter as ctk
import os
from tkinter import messagebox, ttk, Menu
from typing import Optional

from .calculator import BDECalculator
from .gaussian_reader import parse_gaussian_file
from .utils import save_to_history, load_history, delete_history, clear_history

# ══════════════════════════════════════════════════════
#  Apple 风格设计常量
# ══════════════════════════════════════════════════════

# 颜色
BG_COLOR       = "#F5F5F7"   # 系统级背景浅灰（macOS 设置页）
CARD_BG        = "#FFFFFF"   # 卡片白色背景
ACCENT_BLUE    = "#007AFF"   # 苹果蓝
ACCENT_HOVER   = "#0066D9"   # 蓝色 hover
TEXT_PRIMARY   = "#1D1D1F"   # 主文字色（近黑色）
TEXT_SECONDARY = "#86868B"   # 次要文字（苹果灰）
TEXT_TERTIARY  = "#B0B0B3"   # 更浅的文字
BORDER_LIGHT   = "#E5E5EA"   # 浅分隔线
BORDER_MEDIUM  = "#D1D1D6"   # 中等边框
BTN_SECONDARY  = "#E8E8ED"   # 次要按钮底色
BTN_DANGER     = "#FF3B30"   # 删除红（苹果风格）

# 字体
FONT_FAMILY    = "Microsoft YaHei"
FONT_MONO      = "Consolas"
FONT_LIGHT     = (FONT_FAMILY, 12)
FONT_REGULAR   = (FONT_FAMILY, 13)
FONT_SEMIBOLD  = (FONT_FAMILY, 13, "bold")
FONT_TITLE     = (FONT_FAMILY, 18, "normal")
FONT_CARD_TITLE= (FONT_FAMILY, 14, "normal")
FONT_MONO_SIZE = 12
FONT_MONO_S    = (FONT_MONO, FONT_MONO_SIZE)

# 圆角
RADIUS_WINDOW  = 0
RADIUS_CARD    = 12
RADIUS_BUTTON  = 8
RADIUS_INPUT   = 8
RADIUS_TAB     = 10

# 间距
PAD_OUTER      = 16
PAD_INNER      = 12
PAD_COMPACT    = 8

# Windows 上字体设置
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class BDEApp(ctk.CTk):
    """BDE 计算器主窗口 — Apple 风格"""

    def __init__(self):
        super().__init__()

        self.title("BDE 计算器")
        self.geometry("880x720")
        self.minsize(760, 620)

        # 配置窗口背景
        self.configure(fg_color=BG_COLOR)

        self._history_data = []
        self._route_esp = ""
        self._route_gcorr = ""
        self._img_rx = ""
        self._img_r  = ""
        self._img_x  = ""
        self._build_main_area()
        self._refresh_history()

    # ══════════════════════════════════════════════════════
    #  顶部标题栏
    # ══════════════════════════════════════════════════════

    def _build_header(self):
        """macOS 风格标题栏"""
        header = ctk.CTkFrame(self, height=52, corner_radius=0, fg_color=CARD_BG)
        header.pack(fill="x", padx=0, pady=(0, 1))
        header.pack_propagate(False)

        # 左侧：应用名
        ctk.CTkLabel(
            header,
            text="BDE 计算器",
            font=(FONT_FAMILY, 17, "normal"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left", padx=(PAD_OUTER, 0), pady=0)

        # 中间：分割线装饰
        dot = ctk.CTkLabel(
            header,
            text="·",
            font=(FONT_FAMILY, 20, "normal"),
            text_color=TEXT_TERTIARY,
        )
        dot.pack(side="left", padx=6, pady=0)

        ctk.CTkLabel(
            header,
            text="键解离能计算工具",
            font=(FONT_FAMILY, 12),
            text_color=TEXT_SECONDARY,
        ).pack(side="left", padx=0, pady=0)

        # 右侧：版本
        ctk.CTkLabel(
            header,
            text="v1.0",
            font=(FONT_FAMILY, 11),
            text_color=TEXT_TERTIARY,
        ).pack(side="right", padx=PAD_OUTER, pady=0)

    # ══════════════════════════════════════════════════════
    #  选项卡主区域
    # ══════════════════════════════════════════════════════

    def _build_main_area(self):
        """主内容区域 — 使用 CTkTabview"""
        self.tab_view = ctk.CTkTabview(
            self,
            corner_radius=RADIUS_TAB,
            fg_color=BG_COLOR,
            segmented_button_selected_color=ACCENT_BLUE,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            segmented_button_unselected_color=BG_COLOR,
            segmented_button_unselected_hover_color="#E8E8ED",
            text_color=TEXT_PRIMARY,
            segmented_button_fg_color=BG_COLOR,
        )
        self.tab_view.pack(fill="both", expand=True, padx=PAD_OUTER, pady=(PAD_INNER, PAD_OUTER))

        # 配置选项卡标签样式
        self.tab_view._segmented_button.configure(font=(FONT_FAMILY, 13))

        tab_calc     = self.tab_view.add("  BDE 计算  ")
        tab_batch    = self.tab_view.add("  批量计算  ")
        tab_history  = self.tab_view.add("  历史记录  ")

        self._build_calc_tab(tab_calc)
        self._build_batch_tab(tab_batch)
        self._build_history_tab(tab_history)

    # ══════════════════════════════════════════════════════
    #  辅助：Apple 风格卡片容器
    # ══════════════════════════════════════════════════════

    def _make_card(self, parent, **kwargs):
        """创建一个白色圆角卡片"""
        opts = dict(
            corner_radius=RADIUS_CARD,
            fg_color=CARD_BG,
            border_width=0,
        )
        opts.update(kwargs)
        return ctk.CTkFrame(parent, **opts)

    def _card_title(self, parent, text):
        """卡片标题"""
        return ctk.CTkLabel(
            parent, text=text, font=(FONT_FAMILY, 15, "normal"),
            text_color=TEXT_PRIMARY,
        )

    def _small_label(self, parent, text, color=TEXT_SECONDARY):
        """灰色小字说明"""
        return ctk.CTkLabel(
            parent, text=text, font=(FONT_FAMILY, 11),
            text_color=color,
        )

    def _primary_btn(self, parent, text, command, **kw):
        """苹果蓝主按钮"""
        opts = dict(
            font=(FONT_FAMILY, 13, "normal"),
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_HOVER,
            text_color="white",
            corner_radius=RADIUS_BUTTON,
            height=34,
            border_width=0,
        )
        opts.update(kw)
        return ctk.CTkButton(parent, text=text, command=command, **opts)

    def _secondary_btn(self, parent, text, command, **kw):
        """灰色次要按钮"""
        opts = dict(
            font=(FONT_FAMILY, 13, "normal"),
            fg_color=BTN_SECONDARY,
            hover_color="#D1D1D6",
            text_color=TEXT_PRIMARY,
            corner_radius=RADIUS_BUTTON,
            height=34,
            border_width=0,
        )
        opts.update(kw)
        return ctk.CTkButton(parent, text=text, command=command, **opts)

    # ══════════════════════════════════════════════════════
    #  Tab 1: BDE 单组计算
    # ══════════════════════════════════════════════════════

    def _build_calc_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, corner_radius=0, fg_color=BG_COLOR, scrollbar_button_color=BG_COLOR, scrollbar_button_hover_color=BG_COLOR)
        scroll.pack(fill="both", expand=True)

        # — 公式提示卡 —
        info_card = self._make_card(scroll)
        info_card.pack(fill="x", padx=0, pady=(0, PAD_INNER))

        ctk.CTkLabel(
            info_card,
            text="BDE  =  [ G(R·) + G(X·) ]  −  G(RX)       其中  G = E_sp + G_corr",
            font=(FONT_FAMILY, 12),
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w", padx=PAD_INNER, pady=(PAD_INNER, 2))

        ctk.CTkLabel(
            info_card,
            text="1 Hartree = 627.509 kcal/mol",
            font=(FONT_FAMILY, 11),
            text_color=TEXT_TERTIARY,
        ).pack(anchor="w", padx=PAD_INNER, pady=(0, PAD_INNER))

        # — 反应式名称卡片 —
        name_card = self._make_card(scroll)
        name_card.pack(fill="x", padx=0, pady=(0, PAD_INNER))

        row = ctk.CTkFrame(name_card, fg_color="transparent")
        row.pack(fill="x", padx=PAD_INNER, pady=PAD_INNER)

        ctk.CTkLabel(row, text="反 应 式", font=(FONT_FAMILY, 12), text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_INNER))

        self.entry_name_rx = ctk.CTkEntry(
            row, placeholder_text="分子 (如 CH₃OH)", width=180,
            font=FONT_REGULAR, corner_radius=RADIUS_INPUT,
            border_color=BORDER_LIGHT, fg_color=BG_COLOR,
        )
        self.entry_name_rx.pack(side="left", padx=4)

        ctk.CTkLabel(row, text="→", font=(FONT_FAMILY, 16), text_color=TEXT_TERTIARY).pack(side="left", padx=6)

        self.entry_name_r = ctk.CTkEntry(
            row, placeholder_text="自由基1 (如 CH₃O·)", width=180,
            font=FONT_REGULAR, corner_radius=RADIUS_INPUT,
            border_color=BORDER_LIGHT, fg_color=BG_COLOR,
        )
        self.entry_name_r.pack(side="left", padx=4)

        ctk.CTkLabel(row, text="+", font=(FONT_FAMILY, 16), text_color=TEXT_TERTIARY).pack(side="left", padx=6)

        self.entry_name_x = ctk.CTkEntry(
            row, placeholder_text="自由基2 (如 H·)", width=180,
            font=FONT_REGULAR, corner_radius=RADIUS_INPUT,
            border_color=BORDER_LIGHT, fg_color=BG_COLOR,
        )
        self.entry_name_x.pack(side="left", padx=4)

        # — 三个物种卡片（并排）—
        cards_row = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_row.pack(fill="x", padx=0, pady=(0, PAD_INNER))
        cards_row.columnconfigure((0, 1, 2), weight=1, uniform="species")

        self._build_species_card(cards_row, 0, "分子  RX",    "entry_rx_sp", "entry_rx_hcorr")
        self._build_species_card(cards_row, 1, "自由基  R·",  "entry_r_sp",  "entry_r_hcorr")
        self._build_species_card(cards_row, 2, "自由基  X·",  "entry_x_sp",  "entry_x_hcorr")

        # — 操作按钮 —
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=0, pady=(0, PAD_INNER))

        self.btn_calc = self._primary_btn(btn_row, "  计算 BDE  ", self._calculate_bde)
        self.btn_calc.pack(side="left", padx=(0, PAD_COMPACT))

        self.btn_clear = self._secondary_btn(btn_row, "  清空  ", self._clear_inputs)
        self.btn_clear.pack(side="left", padx=(0, PAD_COMPACT))

        self.btn_save = ctk.CTkButton(
            btn_row, text="  保存结果  ",
            font=(FONT_FAMILY, 13, "normal"),
            fg_color="#34C759", hover_color="#28A745",  # 苹果绿
            text_color="white",
            corner_radius=RADIUS_BUTTON,
            height=34, border_width=0,
            command=self._save_result, state="disabled",
        )
        self.btn_save.pack(side="left")

        # — 结果卡片 —
        result_card = self._make_card(scroll)
        result_card.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        self._card_title(result_card, "计算结果").pack(anchor="w", padx=PAD_INNER, pady=(PAD_INNER, PAD_COMPACT))

        # ── 结果摘要区（大字展示 BDE 数值）──
        self.result_summary = ctk.CTkFrame(result_card, fg_color=BG_COLOR, corner_radius=RADIUS_INPUT)

        # 内部容器：所有子控件在此统一管理
        self.result_display = ctk.CTkFrame(self.result_summary, fg_color="transparent")

        # — 第一行：BDE 大数值 + 单位（kcal/mol）—
        frame_val = ctk.CTkFrame(self.result_display, fg_color="transparent")
        frame_val.pack(fill="x", pady=(PAD_INNER, 0))

        self.label_bde_value = ctk.CTkLabel(
            frame_val, text="",
            font=(FONT_FAMILY, 44, "bold"), text_color=ACCENT_BLUE,
        )
        self.label_bde_value.pack(side="left", padx=(0, 6))

        self.label_bde_unit = ctk.CTkLabel(
            frame_val, text="",
            font=(FONT_FAMILY, 18, "normal"), text_color=TEXT_SECONDARY,
        )
        self.label_bde_unit.pack(side="left", pady=(16, 0))

        # — 第二行：kJ/mol —
        frame_kj = ctk.CTkFrame(self.result_display, fg_color="transparent")
        frame_kj.pack(fill="x", pady=(2, PAD_COMPACT))

        self.label_bde_kj_value = ctk.CTkLabel(
            frame_kj, text="",
            font=(FONT_FAMILY, 20, "normal"), text_color=TEXT_PRIMARY,
        )
        self.label_bde_kj_value.pack(side="left", padx=(0, 4))

        self.label_bde_kj_unit = ctk.CTkLabel(
            frame_kj, text="",
            font=(FONT_FAMILY, 14, "normal"), text_color=TEXT_SECONDARY,
        )
        self.label_bde_kj_unit.pack(side="left")

        # — 分隔装饰 —
        self.result_divider = ctk.CTkFrame(self.result_display, height=1, fg_color=BORDER_LIGHT)

        # — 反应式 + 焓值摘要 —
        self.label_reaction = ctk.CTkLabel(
            self.result_display, text="",
            font=(FONT_FAMILY, 13), text_color=TEXT_SECONDARY, justify="left",
        )

        self._current_result = None
        self._current_names = ("RX", "R·", "X·")

    # ── 单个物种输入卡片 ──

    def _build_species_card(self, parent, col: int, title: str, sp_attr: str, hc_attr: str):
        card = self._make_card(parent)
        card.grid(row=0, column=col, sticky="nsew", padx=6, pady=0)

        ctk.CTkLabel(
            card, text=title,
            font=(FONT_FAMILY, 14, "normal"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=PAD_INNER, pady=(PAD_INNER, PAD_COMPACT))

        # G_corr 行（上）：输入框 + 文件按钮
        self._small_label(card, "吉布斯自由能校正  G_corr (Thermal Correction to Free Energy)").pack(anchor="w", padx=PAD_INNER, pady=(0, 2))
        hc_row = ctk.CTkFrame(card, fg_color="transparent")
        hc_row.pack(fill="x", padx=PAD_INNER, pady=(0, PAD_INNER))
        hc_row.columnconfigure(0, weight=1)

        entry_hc = ctk.CTkEntry(
            hc_row, font=FONT_MONO_S,
            corner_radius=RADIUS_INPUT,
            border_color=BORDER_LIGHT,
            fg_color=BG_COLOR,
            height=32,
        )
        entry_hc.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        setattr(self, hc_attr, entry_hc)

        btn_hc = ctk.CTkButton(
            hc_row, text="📂",
            font=(FONT_FAMILY, 14),
            fg_color="transparent",
            text_color=ACCENT_BLUE,
            hover_color="#E8F0FE",
            corner_radius=RADIUS_BUTTON,
            width=36, height=32, border_width=0,
            command=lambda a=hc_attr: self._import_gcorr(a),
        )
        btn_hc.grid(row=0, column=1)

        # E_sp 行（下）：输入框 + 文件按钮
        self._small_label(card, "单点能  E_sp").pack(anchor="w", padx=PAD_INNER, pady=(0, 2))
        sp_row = ctk.CTkFrame(card, fg_color="transparent")
        sp_row.pack(fill="x", padx=PAD_INNER, pady=(0, PAD_INNER))
        sp_row.columnconfigure(0, weight=1)

        entry_sp = ctk.CTkEntry(
            sp_row, font=FONT_MONO_S,
            corner_radius=RADIUS_INPUT,
            border_color=BORDER_LIGHT,
            fg_color=BG_COLOR,
            height=32,
        )
        entry_sp.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        setattr(self, sp_attr, entry_sp)

        btn_sp = ctk.CTkButton(
            sp_row, text="📂",
            font=(FONT_FAMILY, 14),
            fg_color="transparent",
            text_color=ACCENT_BLUE,
            hover_color="#E8F0FE",
            corner_radius=RADIUS_BUTTON,
            width=36, height=32, border_width=0,
            command=lambda a=sp_attr: self._import_esp(a),
        )
        btn_sp.grid(row=0, column=1)

        # 图片上传按钮
        img_attr = f"img_{sp_attr.split('_')[1]}".replace("_sp","")
        img_frame = ctk.CTkFrame(card, fg_color="transparent")
        img_frame.pack(fill="x", padx=PAD_INNER, pady=(0, PAD_INNER))

        img_preview = ctk.CTkLabel(img_frame, text="", font=(FONT_FAMILY, 10), text_color=TEXT_TERTIARY)
        img_preview.pack(side="left", fill="x", expand=True)

        img_btn = ctk.CTkButton(
            img_frame, text="📷 上传分子结构",
            font=(FONT_FAMILY, 11),
            fg_color="transparent", text_color=ACCENT_BLUE,
            hover_color="#E8F0FE", corner_radius=RADIUS_BUTTON,
            height=26, border_width=0,
            command=lambda a=sp_attr.split("_")[1]: self._upload_image(a),
        )
        img_btn.pack(side="right")

        setattr(self, f"lbl_{img_attr}", img_preview)

    # ── 计算逻辑 ──

    def _get_float(self, entry: ctk.CTkEntry, field_name: str) -> Optional[float]:
        try:
            val = entry.get().strip()
            if not val:
                raise ValueError("")
            return float(val)
        except (ValueError, AttributeError):
            from tkinter import messagebox
            messagebox.showerror("输入错误", f"「{field_name}」请输入有效的数值\n如  -345.67890")
            return None

    def _name_entry_from_attr(self, attr: str) -> Optional[str]:
        """根据输入框属性名推断对应的反应式名称输入框"""
        if attr.startswith("entry_rx_"):
            return "entry_name_rx"
        if attr.startswith("entry_r_"):
            return "entry_name_r"
        if attr.startswith("entry_x_"):
            return "entry_name_x"
        return None

    def _auto_fill_name(self, path: str, attr: str):
        """从文件名提取前缀，自动填入反应式名称（仅当名称框为空时）"""
        name_entry_key = self._name_entry_from_attr(attr)
        if name_entry_key is None:
            return
        name_entry = getattr(self, name_entry_key, None)
        if name_entry is None or name_entry.get().strip():
            return  # 已有名称就不覆盖

        # 提取文件名（不含扩展名）
        import re
        fname = path.split("/")[-1].split("\\")[-1]
        fname = fname.rsplit(".", 1)[0] if "." in fname else fname
        # 去掉常见计算类型后缀
        name = re.sub(r"[-_](?:E|sp|SP|freq|Freq|opt|Opt|log|g09|g16)$", "", fname)
        name = re.sub(r"[-_]\d+$", "", name)  # 去掉末尾的数字后缀
        if name:
            name_entry.insert(0, name)

    def _attr_to_method_key(self, attr: str) -> Optional[str]:
        """根据输入框属性判断属于哪个物种的方法"""
        if attr.startswith("entry_rx_"):
            return "rx"
        if attr.startswith("entry_r_"):
            return "r"
        if attr.startswith("entry_x_"):
            return "x"
        return None

    def _import_esp(self, attr: str):
        """从 Gaussian 输出文件导入 E_sp（只填 E_sp 框）"""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="选择单点能计算文件 (E_sp)",
            filetypes=[("Gaussian output", "*.log *.out"), ("All files", "*.*")]
        )
        if not path:
            return
        self._auto_fill_name(path, attr)
        data = parse_gaussian_file(path)
        name = path.split("/")[-1].split("\\")[-1]
        if data["e_sp"] is not None:
            getattr(self, attr).delete(0, "end")
            getattr(self, attr).insert(0, f"{data['e_sp']:.8f}")
            method = data.get("method") or "?"
            route = data.get("route") or ""
            # 记录 route（从任何文件读到就存）
            if route:
                self._route_esp = route
            msg = f"文件: {name}"
            if method != "?":
                msg += f"\n方法: {method}"
            if route:
                msg += f"\n计算级别: {route[:80]}{'...' if len(route)>80 else ''}"
            msg += f"\nE_sp = {data['e_sp']:.8f}"
            messagebox.showinfo("导入成功", msg)
        else:
            messagebox.showwarning(
                "未找到",
                f"文件「{name}」中未找到 SCF Done 能量\n\n"
                f"请检查是否选择了正确的 Gaussian 输出文件（.log / .out）。"
            )

    def _import_gcorr(self, attr: str):
        """从 Gaussian 输出文件导入 G_corr（只填 G_corr 框）"""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="选择频率计算文件 (G_corr)",
            filetypes=[("Gaussian output", "*.log *.out"), ("All files", "*.*")]
        )
        if not path:
            return
        self._auto_fill_name(path, attr)
        data = parse_gaussian_file(path)
        name = path.split("/")[-1].split("\\")[-1]
        # 优先取 Gibbs 校正
        g_val = data.get("g_corr")
        if g_val is not None:
            getattr(self, attr).delete(0, "end")
            getattr(self, attr).insert(0, f"{g_val:.8f}")
            method = data.get("method")
            route = data.get("route") or ""
            msg = f"文件: {name}\nG_corr = {g_val:.8f}"
            if method:
                msg += f"\n方法: {method}"
            if route:
                self._route_gcorr = route
                msg += f"\n计算级别: {route[:80]}{'...' if len(route)>80 else ''}"
            messagebox.showinfo("导入成功", msg)
        else:
            messagebox.showwarning(
                "未找到",
                f"文件「{name}」中未找到吉布斯自由能校正数据\n\n"
                f"请选择频率计算（Freq）的输出文件来读取 G_corr。"
            )

    def _upload_image(self, species_key: str):
        """上传分子结构图片"""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title=f"选择{species_key.upper()} 的分子结构图",
            filetypes=[("Image", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            from PIL import Image, ImageTk
            # 复制图片到 data/images/ 目录下持久存储
            import shutil, hashlib
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "images")
            os.makedirs(data_dir, exist_ok=True)
            ext = os.path.splitext(path)[1] or ".png"
            fname = f"{species_key}_{hashlib.md5(path.encode()).hexdigest()[:8]}{ext}"
            dst = os.path.join(data_dir, fname)
            if not os.path.exists(dst):
                shutil.copy2(path, dst)

            # 缩略图显示
            pil_img = Image.open(dst)
            pil_img.thumbnail((120, 90))
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)

            lbl_key = f"lbl_img_{species_key}"
            lbl = getattr(self, lbl_key, None)
            if lbl:
                lbl.configure(image=ctk_img, text="")

            # 记录路径
            setattr(self, f"_img_{species_key}", dst)
        except ImportError:
            messagebox.showwarning("缺少依赖", "请安装 Pillow 库：pip install Pillow")
        except Exception as e:
            messagebox.showerror("图片上传失败", str(e))

    def _calculate_bde(self):
        name_rx = self.entry_name_rx.get().strip() or "RX"
        name_r  = self.entry_name_r.get().strip()  or "R·"
        name_x  = self.entry_name_x.get().strip()  or "X·"
        self._current_names = (name_rx, name_r, name_x)

        e_sp_rx = self._get_float(self.entry_rx_sp, f"{name_rx} 单点能")
        if e_sp_rx is None:
            return
        g_corr_rx = self._get_float(self.entry_rx_hcorr, f"{name_rx} 吉布斯自由能校正")
        if g_corr_rx is None:
            return
        e_sp_r = self._get_float(self.entry_r_sp, f"{name_r} 单点能")
        if e_sp_r is None:
            return
        g_corr_r = self._get_float(self.entry_r_hcorr, f"{name_r} 吉布斯自由能校正")
        if g_corr_r is None:
            return
        e_sp_x = self._get_float(self.entry_x_sp, f"{name_x} 单点能")
        if e_sp_x is None:
            return
        g_corr_x = self._get_float(self.entry_x_hcorr, f"{name_x} 吉布斯自由能校正")
        if g_corr_x is None:
            return

        calc = BDECalculator()
        result = calc.calculate_bde(e_sp_rx, g_corr_rx, e_sp_r, g_corr_r, e_sp_x, g_corr_x)
        self._current_result = result

        self._update_result_display(result, name_rx, name_r, name_x)
        self.btn_save.configure(state="normal", fg_color="#34C759", hover_color="#28A745")

    def _clear_inputs(self):
        for attr in ("entry_name_rx", "entry_name_r", "entry_name_x",
                     "entry_rx_sp", "entry_rx_hcorr",
                     "entry_r_sp", "entry_r_hcorr",
                     "entry_x_sp", "entry_x_hcorr"):
            w = getattr(self, attr, None)
            if w:
                w.delete(0, "end")
        self._hide_result_summary()
        self._current_result = None
        self._route_esp = ""
        self._route_gcorr = ""
        self._img_rx = ""
        self._img_r  = ""
        self._img_x  = ""
        for k in ("rx", "r", "x"):
            lbl = getattr(self, f"lbl_img_{k}", None)
            if lbl:
                lbl.configure(image="", text="")
        self.btn_save.configure(state="disabled", fg_color="#A8A8AD", hover_color="#8E8E93")

    def _save_result(self):
        if not self._current_result:
            return
        n1, n2, n3 = self._current_names
        record = {
            "name_rx": n1, "name_r": n2, "name_x": n3,
            "route_esp": self._route_esp,
            "route_gcorr": self._route_gcorr,
            "img_rx": self._img_rx,
            "img_r": self._img_r,
            "img_x": self._img_x,
            "bde_kcal": self._current_result["bde_kcal"],
            "bde_kj": self._current_result["bde_kj"],
            "type": "single",
        }
        ts = save_to_history(record)
        self._refresh_history()
        messagebox.showinfo("保存成功", f"结果已保存至历史记录\n时间: {ts}")

    # ── 更新结果展示 ──

    def _update_result_display(self, result: dict, name_rx: str, name_r: str, name_x: str):
        """用美观的卡片展示 BDE 计算结果"""
        bde_kcal = result["bde_kcal"]
        bde_kj   = result["bde_kj"]
        g_rx     = result["g_rx"]
        g_r      = result["g_r"]
        g_x      = result["g_x"]

        # 显示摘要区
        if not self.result_summary.winfo_ismapped():
            self.result_summary.pack(fill="x", padx=PAD_INNER, pady=(0, PAD_INNER))
        self.result_display.pack(fill="x", padx=PAD_INNER, pady=PAD_INNER)

        # 大字 BDE 值 (kcal/mol)
        self.label_bde_value.configure(text=f"{bde_kcal:.2f}")
        self.label_bde_unit.configure(text="kcal/mol")

        # 第二行 kJ/mol
        self.label_bde_kj_value.configure(text=f"{bde_kj:.2f}")
        self.label_bde_kj_unit.configure(text="kJ/mol")

        # 分隔线
        self.result_divider.pack(fill="x", pady=(0, PAD_COMPACT))

        # 反应式 + 方法 + 焓值摘要
        reaction_text = f"{name_rx}  →  {name_r}  +  {name_x}"
        h_text = (f"G({name_rx}) = {g_rx:.4f}    "
                  f"G({name_r})  = {g_r:.4f}    "
                  f"G({name_x})  = {g_x:.4f}   Hartree")
        self.label_reaction.configure(text=f"{reaction_text}\n{h_text}")
        self.label_reaction.pack(fill="x", pady=(0, PAD_INNER))

    def _hide_result_summary(self):
        """隐藏结果摘要区"""
        self.result_divider.pack_forget()
        self.label_reaction.pack_forget()
        self.result_display.pack_forget()
        self.result_summary.pack_forget()

    # ══════════════════════════════════════════════════════
    #  Tab 2: 批量计算
    # ══════════════════════════════════════════════════════

    def _build_batch_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, corner_radius=0, fg_color=BG_COLOR, scrollbar_button_color=BG_COLOR, scrollbar_button_hover_color=BG_COLOR)
        scroll.pack(fill="both", expand=True)

        # 说明
        self._small_label(
            scroll,
            "输入多组数据一次计算所有 BDE 值，支持 Excel 导入 / 导出",
            TEXT_TERTIARY,
        ).pack(anchor="w", padx=0, pady=(0, PAD_INNER))

        # 工具栏卡片
        toolbar_card = self._make_card(scroll)
        toolbar_card.pack(fill="x", padx=0, pady=(0, PAD_INNER))

        tb = ctk.CTkFrame(toolbar_card, fg_color="transparent")
        tb.pack(fill="x", padx=PAD_INNER, pady=PAD_INNER)

        self.btn_add_row   = self._secondary_btn(tb, "  添加一行  ", self._batch_add_row)
        self.btn_import    = self._secondary_btn(tb, "  导入 Excel  ", self._batch_import)
        self.btn_export    = self._secondary_btn(tb, "  导出结果  ", self._batch_export)
        self.btn_batch_calc= self._primary_btn(tb, "  全部计算  ", self._batch_calculate)

        self.btn_add_row.pack(side="left", padx=(0, PAD_COMPACT))
        self.btn_import.pack(side="left", padx=(0, PAD_COMPACT))
        self.btn_export.pack(side="left", padx=(0, PAD_COMPACT))
        self.btn_batch_calc.pack(side="left")

        # 表格卡片
        table_card = self._make_card(scroll)
        table_card.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        self._card_title(table_card, "数据列表").pack(anchor="w", padx=PAD_INNER, pady=(PAD_INNER, PAD_COMPACT))

        frame = ctk.CTkFrame(table_card, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=PAD_INNER, pady=(0, PAD_INNER))

        columns = ("#", "反应", "E_sp(RX)", "H_corr(RX)", "E_sp(R·)", "H_corr(R·)",
                   "E_sp(X·)", "H_corr(X·)", "BDE (kcal/mol)")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Apple.Treeview",
                        background=CARD_BG, foreground=TEXT_PRIMARY,
                        fieldbackground=CARD_BG, font=(FONT_FAMILY, 11),
                        rowheight=28, borderwidth=0)
        style.configure("Apple.Treeview.Heading",
                        font=(FONT_FAMILY, 11, "normal"),
                        background=BG_COLOR, foreground=TEXT_PRIMARY,
                        borderwidth=0, relief="flat")
        style.map("Apple.Treeview.Heading", background=[("active", "#E8E8ED")])
        style.layout("Apple.Treeview", [("Apple.Treeview.treearea", {"sticky": "nswe"})])

        self.tree = ttk.Treeview(frame, columns=columns, show="headings",
                                 style="Apple.Treeview", height=12)

        col_widths = [30, 80, 110, 100, 110, 100, 110, 100, 120]
        for col, w in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self._batch_edit_cell)
        self._batch_menu = Menu(parent, tearoff=False, background=CARD_BG, fg=TEXT_PRIMARY,
                                activebackground=ACCENT_BLUE, activeforeground="white")
        self._batch_menu.add_command(label="删除选中行", command=self._batch_delete_selected)
        self.tree.bind("<Button-3>", lambda e: self._batch_menu.tk_popup(e.x_root, e.y_root))

        self._batch_data = []
        self._batch_row_counter = 0

    def _batch_add_row(self, values: Optional[list] = None):
        self._batch_row_counter += 1
        idx = self._batch_row_counter
        if values is None:
            values = [""] * 7
        while len(values) < 7:
            values.append("")
        name = values[0] if values[0] else f"反应 {idx}"
        rec = {
            "id": idx, "name": name,
            "e_sp_rx": values[0], "g_corr_rx": values[1],
            "e_sp_r": values[2], "g_corr_r": values[3],
            "e_sp_x": values[4], "g_corr_x": values[5],
            "result": values[6] if len(values) > 6 else "",
        }
        self._batch_data.append(rec)
        disp = (idx, name, values[0], values[1], values[2], values[3], values[4], values[5], rec["result"])
        self.tree.insert("", "end", values=disp, iid=str(idx))

    def _batch_delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for iid in sel:
            idx = int(iid)
            self._batch_data = [d for d in self._batch_data if d["id"] != idx]
            self.tree.delete(iid)

    def _batch_edit_cell(self, event):
        item = self.tree.selection()[0]
        col = self.tree.identify_column(event.x)
        col_idx = int(col.replace("#", "")) - 1
        if col_idx in (0, 8):
            return
        x, y, w, h = self.tree.bbox(item, col)
        value = self.tree.item(item, "values")[col_idx]

        e = ctk.CTkEntry(self.tree, font=FONT_MONO_S, width=w, height=h,
                         corner_radius=4, border_color=ACCENT_BLUE)
        e.place(x=x, y=y, width=w, height=h)
        e.insert(0, str(value))
        e.focus()
        e.bind("<Return>", lambda ev, r=item, c=col_idx, en=e: self._batch_finish_edit(r, c, en))
        e.bind("<FocusOut>", lambda ev, r=item, c=col_idx, en=e: self._batch_finish_edit(r, c, en))

    def _batch_finish_edit(self, item, col_idx, entry):
        new_val = entry.get()
        entry.destroy()
        vals = list(self.tree.item(item, "values"))
        vals[col_idx] = new_val
        self.tree.item(item, values=vals)
        idx = int(item)
        key_map = {1: "e_sp_rx", 2: "g_corr_rx", 3: "e_sp_r", 4: "g_corr_r", 5: "e_sp_x", 6: "g_corr_x"}
        for d in self._batch_data:
            if d["id"] == idx:
                if col_idx in key_map:
                    d[key_map[col_idx]] = new_val
                elif col_idx == 1:
                    d["name"] = new_val
                break

    def _batch_calculate(self):
        calc = BDECalculator()
        ok = err = 0
        for i, item in enumerate(self.tree.get_children()):
            vals = list(self.tree.item(item, "values"))
            d = self._batch_data[i] if i < len(self._batch_data) else {}
            try:
                fields = {
                    "e_sp_rx":   d.get("e_sp_rx", vals[2]) or vals[2],
                    "g_corr_rx": d.get("g_corr_rx", vals[3]) or vals[3],
                    "e_sp_r":    d.get("e_sp_r", vals[4]) or vals[4],
                    "g_corr_r":  d.get("g_corr_r", vals[5]) or vals[5],
                    "e_sp_x":    d.get("e_sp_x", vals[6]) or vals[6],
                    "g_corr_x":  d.get("g_corr_x", vals[7]) or vals[7],
                }
                if not any(fields.values()):
                    continue
                fv = {k: float(v) for k, v in fields.items() if v}
                if len(fv) < 6:
                    vals[8] = "数据不足"
                    self.tree.item(item, values=vals)
                    err += 1
                    continue
                r = calc.calculate_bde(fv["e_sp_rx"], fv["g_corr_rx"], fv["e_sp_r"], fv["g_corr_r"],
                                        fv["e_sp_x"], fv["g_corr_x"])
                vals[8] = f"{r['bde_kcal']:.2f}"
                self.tree.item(item, values=vals)
                if d:
                    d["result"] = f"{r['bde_kcal']:.2f}"
                    name = d.get("name", vals[1])
                    save_to_history({
                        "name_rx": name, "name_r": "R·", "name_x": "X·",
                        "route_esp": "", "route_gcorr": "",
                        "bde_kcal": r["bde_kcal"], "bde_kj": r["bde_kj"],
                        "type": "batch",
                    })
                ok += 1
            except (ValueError, KeyError, TypeError):
                vals[8] = "错误"
                self.tree.item(item, values=vals)
                err += 1
        self._refresh_history()
        messagebox.showinfo("批量计算完成", f"成功: {ok} 组\n失败: {err} 组")

    def _batch_import(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="选择 Excel 文件",
                                          filetypes=[("Excel", "*.xlsx *.xls"), ("CSV", "*.csv")])
        if not path:
            return
        try:
            import pandas as pd
            df = pd.read_excel(path) if path.endswith((".xlsx", ".xls")) else pd.read_csv(path)
            col_map = list(df.columns[:7])
            for _, row in df.iterrows():
                self._batch_add_row([str(row.get(c, "")) for c in col_map])
            messagebox.showinfo("导入成功", f"已导入 {len(df)} 行数据")
        except Exception as e:
            messagebox.showerror("导入失败", str(e))

    def _batch_export(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(title="保存 Excel 文件", defaultextension=".xlsx",
                                            filetypes=[("Excel", "*.xlsx")])
        if not path:
            return
        try:
            import pandas as pd
            recs = []
            for item in self.tree.get_children():
                v = self.tree.item(item, "values")
                recs.append({"序号": v[0], "反应": v[1], "E_sp(RX)": v[2], "H_corr(RX)": v[3],
                             "E_sp(R·)": v[4], "H_corr(R·)": v[5], "E_sp(X·)": v[6], "H_corr(X·)": v[7],
                             "BDE (kcal/mol)": v[8]})
            pd.DataFrame(recs).to_excel(path, index=False)
            messagebox.showinfo("导出成功", f"已导出 {len(recs)} 条记录")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    # ══════════════════════════════════════════════════════
    #  Tab 3: 历史记录（精致版）
    # ══════════════════════════════════════════════════════

    def _build_history_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, corner_radius=0, fg_color=BG_COLOR,
                                         scrollbar_button_color=BG_COLOR,
                                         scrollbar_button_hover_color=BG_COLOR)
        scroll.pack(fill="both", expand=True)

        # ── 统计摘要：4个小卡片 ──
        stats_card = self._make_card(scroll)
        stats_card.pack(fill="x", padx=0, pady=(0, PAD_INNER))

        self.stats_frame = ctk.CTkFrame(stats_card, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=PAD_INNER, pady=PAD_INNER)

        # ── 搜索 + 工具栏 ──
        tool_card = self._make_card(scroll)
        tool_card.pack(fill="x", padx=0, pady=(0, PAD_INNER))

        tb = ctk.CTkFrame(tool_card, fg_color="transparent")
        tb.pack(fill="x", padx=PAD_INNER, pady=(PAD_INNER - 2, PAD_INNER - 2))

        # 搜索框 + 清空按钮
        search_frame = ctk.CTkFrame(tb, fg_color=BG_COLOR, corner_radius=RADIUS_INPUT,
                                    border_width=1, border_color=BORDER_LIGHT)
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, PAD_INNER))

        ctk.CTkLabel(search_frame, text="  🔍", font=(FONT_FAMILY, 12),
                     text_color=TEXT_TERTIARY).pack(side="left", padx=(8, 0))

        self.entry_search = ctk.CTkEntry(
            search_frame, placeholder_text="搜索反应式...", font=(FONT_FAMILY, 12),
            corner_radius=0, border_width=0, fg_color="transparent", height=30,
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        self.entry_search.bind("<KeyRelease>", lambda e: self._refresh_history())

        self.btn_clear_search = ctk.CTkButton(
            search_frame, text="×", font=(FONT_FAMILY, 14),
            width=24, height=24, corner_radius=12,
            fg_color="transparent", text_color=TEXT_TERTIARY,
            hover_color=BORDER_LIGHT, border_width=0,
            command=self._clear_search,
        )
        self.btn_clear_search.pack(side="right", padx=(0, 4))

        # 操作按钮
        btn_refresh = ctk.CTkButton(
            tb, text="↻", font=(FONT_FAMILY, 16),
            width=34, height=34, corner_radius=RADIUS_BUTTON,
            fg_color=BTN_SECONDARY, text_color=TEXT_PRIMARY,
            hover_color="#D1D1D6", border_width=0,
            command=self._refresh_history,
        )
        btn_refresh.pack(side="left", padx=(0, PAD_COMPACT))

        btn_delete = ctk.CTkButton(
            tb, text=" 删除 ", font=(FONT_FAMILY, 12),
            fg_color=BTN_SECONDARY, text_color=BTN_DANGER,
            hover_color="#D1D1D6", corner_radius=RADIUS_BUTTON,
            height=34, border_width=0,
            command=self._delete_history_selected,
        )
        btn_delete.pack(side="left", padx=(0, PAD_COMPACT))

        btn_clear = ctk.CTkButton(
            tb, text=" 清空全部 ", font=(FONT_FAMILY, 12),
            fg_color=BTN_SECONDARY, text_color=TEXT_SECONDARY,
            hover_color="#D1D1D6", corner_radius=RADIUS_BUTTON,
            height=34, border_width=0,
            command=self._clear_history_all,
        )
        btn_clear.pack(side="left")

        # ── 记录卡片列表 ──
        self._hist_scroll_card = self._make_card(scroll)
        self._hist_scroll_card.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        self._hist_canvas_inner = ctk.CTkScrollableFrame(
            self._hist_scroll_card, fg_color="transparent",
            scrollbar_button_color=BG_COLOR,
            scrollbar_button_hover_color=BG_COLOR,
        )
        self._hist_canvas_inner.pack(fill="both", expand=True, padx=PAD_INNER, pady=(PAD_COMPACT, PAD_INNER))


    def _clear_search(self):
        """清空搜索框"""
        self.entry_search.delete(0, "end")
        self._refresh_history()

    def _get_filtered_records(self) -> list:
        all_recs = load_history()
        keyword = self.entry_search.get().strip().lower()
        if not keyword:
            return all_recs
        return [
            r for r in all_recs
            if keyword in r.get("name_rx", "").lower()
            or keyword in r.get("name_r", "").lower()
            or keyword in r.get("name_x", "").lower()
        ]

    def _refresh_history(self):
        if not hasattr(self, '_hist_canvas_inner'):
            return
        for w in self._hist_canvas_inner.winfo_children():
            w.destroy()

        records = self._get_filtered_records()
        self._history_data = records
        self._update_stats(records)

        if not records:
            ctk.CTkLabel(
                self._hist_canvas_inner, text="暂无计算记录",
                font=(FONT_FAMILY, 12), text_color=TEXT_TERTIARY,
            ).pack(anchor="w", pady=20)
            return

        type_labels = {"single": "单组", "batch": "批量"}
        _icons = {"single": "🔬", "batch": "📋"}

        for i, rec in enumerate(records):
            name_rx = rec.get("name_rx", "RX")
            name_r  = rec.get("name_r", "R·")
            name_x  = rec.get("name_x", "X·")
            bk = rec.get("bde_kcal", 0)
            ts = rec.get("timestamp", "")
            t = rec.get("type", "single")
            icon = _icons.get(t, "🔬")

            # 每个记录一张卡片
            card = self._make_card(self._hist_canvas_inner, corner_radius=10)
            card.pack(fill="x", padx=0, pady=4)
            card._rec_idx = i  # 存索引供删除/详情用

            # 绑定点击事件
            card.bind("<Button-1>", lambda e, idx=i: self._hist_card_click(idx))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, idx=i: self._hist_card_click(idx))

            # 行内：左侧图片 + 右侧信息
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=PAD_INNER, pady=PAD_INNER)

            # 左侧：分子图片缩略图（最多显示第一个有的物种）
            img_path = rec.get("img_rx") or rec.get("img_r") or rec.get("img_x") or ""
            img_label = ctk.CTkLabel(row, text="", font=(FONT_FAMILY, 10), text_color=TEXT_TERTIARY)
            img_label.pack(side="left", padx=(0, PAD_INNER))
            img_label._img_path = img_path
            img_label._rec_idx = i
            if img_path and os.path.exists(img_path):
                try:
                    from PIL import Image as PILImage
                    pi = PILImage.open(img_path)
                    pi.thumbnail((80, 60))
                    ci = ctk.CTkImage(light_image=pi, dark_image=pi, size=pi.size)
                    img_label.configure(image=ci, text="")
                    img_label._ctk_image = ci
                except Exception:
                    img_label.configure(text="🧪")
            else:
                img_label.configure(text="🧪")

            # 右侧信息区
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)

            # 第一行：反应式 + 类型标签
            r1 = ctk.CTkFrame(info, fg_color="transparent")
            r1.pack(fill="x")
            ctk.CTkLabel(r1, text=f"{icon}  {name_rx} → {name_r} + {name_x}",
                         font=(FONT_FAMILY, 13, "bold"), text_color=TEXT_PRIMARY,
                         anchor="w").pack(side="left")
            type_bg = "#E8F0FE" if t == "single" else "#FFF3E0"
            type_fg = ACCENT_BLUE if t == "single" else "#F57C00"
            ctk.CTkLabel(r1, text=type_labels.get(t, ""), font=(FONT_FAMILY, 10, "bold"),
                         fg_color=type_bg, text_color=type_fg, corner_radius=4, padx=6
            ).pack(side="right")

            # 第二行：BDE + 时间
            r2 = ctk.CTkFrame(info, fg_color="transparent")
            r2.pack(fill="x", pady=(4, 0))
            ctk.CTkLabel(r2, text=f"BDE = {bk:.2f} kcal/mol",
                         font=(FONT_FAMILY, 14, "normal"), text_color=ACCENT_BLUE, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(r2, text=ts,
                         font=(FONT_FAMILY, 10), text_color=TEXT_TERTIARY, anchor="e"
            ).pack(side="right")

            # 第三行：Route
            rte = rec.get("route_esp", "") or rec.get("route_gcorr", "")
            if rte:
                ctk.CTkLabel(info, text=rte[:80],
                             font=(FONT_MONO, 9), text_color=TEXT_TERTIARY,
                             anchor="w").pack(fill="x")

    def _update_stats(self, records: list):
        """更新统计摘要——4个迷你卡片"""
        for w in self.stats_frame.winfo_children():
            w.destroy()

        if not records:
            ctk.CTkLabel(
                self.stats_frame, text="暂无计算记录",
                font=(FONT_FAMILY, 12), text_color=TEXT_TERTIARY,
            ).pack(anchor="w")
            return

        values = [r.get("bde_kcal", 0) for r in records]
        n = len(values)
        avg = sum(values) / n
        mn = min(values)
        mx = max(values)

        emoji = [("📊", f"{n}", "条记录"),
                 ("🎯", f"{avg:.1f}", "平均"),
                 ("⬇️", f"{mn:.1f}", "最小"),
                 ("⬆️", f"{mx:.1f}", "最大 kcal/mol")]

        for icon, val, label in emoji:
            card = ctk.CTkFrame(self.stats_frame, fg_color=BG_COLOR, corner_radius=RADIUS_INPUT)
            card.pack(side="left", fill="x", expand=True, padx=3)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(inner, text=icon, font=(FONT_FAMILY, 16)).pack(side="left", padx=(0, 6))
            col = ctk.CTkFrame(inner, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(col, text=val, font=(FONT_FAMILY, 16, "bold"),
                         text_color=ACCENT_BLUE, anchor="w"
            ).pack(fill="x")
            ctk.CTkLabel(col, text=label, font=(FONT_FAMILY, 10),
                         text_color=TEXT_TERTIARY, anchor="w"
            ).pack(fill="x")

    def _hist_card_click(self, idx: int):
        """点击历史卡片打开详情"""
        if idx < len(self._history_data):
            self._show_history_detail(idx)

    def _delete_history_selected(self):
        """从工具栏删除按钮触发：弹窗选择要删除的序号"""
        from tkinter import simpledialog
        total = len(self._history_data)
        if total == 0:
            return
        n = simpledialog.askinteger("删除记录", f"当前共 {total} 条记录\n输入要删除的序号 (1-{total}):",
                                    minvalue=1, maxvalue=total, parent=self)
        if n is not None:
            delete_history(n - 1)
            self._refresh_history()

    def _clear_history_all(self):
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
            clear_history()
            self._refresh_history()

    def _copy_bde_value(self):
        """工具栏复制按钮：弹窗选择要复制的序号"""
        total = len(self._history_data)
        if total == 0:
            return
        from tkinter import simpledialog
        n = simpledialog.askinteger("复制 BDE", f"当前共 {total} 条记录\n输入要复制的序号 (1-{total}):",
                                    minvalue=1, maxvalue=total, parent=self)
        if n is not None:
            rec = self._history_data[n - 1]
            bk = rec.get("bde_kcal", 0)
            self.clipboard_clear()
            self.clipboard_append(f"{bk:.2f}")
            messagebox.showinfo("已复制", f"BDE = {bk:.2f} kcal/mol")

    def _show_history_detail(self, idx: int):

        name_rx = rec.get("name_rx", "RX")
        name_r  = rec.get("name_r", "R·")
        name_x  = rec.get("name_x", "X·")
        bde_kcal = rec.get("bde_kcal", 0)
        bde_kj   = rec.get("bde_kj", 0)

        # ── 详情窗口 ──
        win = ctk.CTkToplevel(self)
        t = rec.get("type", "single")
        type_tag = "单组" if t == "single" else "批量"
        win.title(f"详情 — {name_rx} → {name_r} + {name_x}")
        win.geometry("640x420")
        win.transient(self)
        win.grab_set()
        win.configure(fg_color=BG_COLOR)
        win.minsize(540, 320)

        scroll_win = ctk.CTkScrollableFrame(win, fg_color=BG_COLOR,
                                             scrollbar_button_color=BG_COLOR,
                                             scrollbar_button_hover_color=BG_COLOR)
        scroll_win.pack(fill="both", expand=True, padx=0, pady=0)


        # ── BDE 结果卡片 ──
        result_card = ctk.CTkFrame(scroll_win, fg_color=CARD_BG, corner_radius=RADIUS_CARD)
        result_card.pack(fill="x", padx=PAD_INNER, pady=(PAD_INNER, 0))

        inner = ctk.CTkFrame(result_card, fg_color="transparent")
        inner.pack(fill="x", padx=PAD_INNER*2, pady=(PAD_INNER+4, PAD_INNER+4))

        # 反应式 + 标签
        info_row = ctk.CTkFrame(inner, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, PAD_INNER))
        ctk.CTkLabel(info_row, text=f"{name_rx}  →  {name_r}  +  {name_x}",
                     font=(FONT_FAMILY, 13), text_color=TEXT_PRIMARY
        ).pack(side="left")

        type_bg = "#E8F0FE" if t == "single" else "#FFF3E0"
        type_fg = ACCENT_BLUE if t == "single" else "#F57C00"
        ctk.CTkLabel(info_row, text=type_tag, font=(FONT_FAMILY, 10, "bold"),
                     fg_color=type_bg, text_color=type_fg,
                     corner_radius=4, padx=6
        ).pack(side="right")

        # BDE 大字
        val_row = ctk.CTkFrame(inner, fg_color="transparent")
        val_row.pack(fill="x")
        ctk.CTkLabel(val_row, text=f"{bde_kcal:.2f}",
                     font=(FONT_FAMILY, 42, "bold"), text_color=ACCENT_BLUE
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(val_row, text="kcal/mol",
                     font=(FONT_FAMILY, 16), text_color=TEXT_SECONDARY
        ).pack(side="left", pady=(16, 0))

        # kJ 行
        ctk.CTkLabel(inner, text=f"= {bde_kj:.2f}  kJ/mol",
                     font=(FONT_FAMILY, 14), text_color=TEXT_SECONDARY, anchor="w"
        ).pack(fill="x")

        # 时间
        ctk.CTkLabel(inner, text=rec.get("timestamp", ""),
                     font=(FONT_FAMILY, 10), text_color=TEXT_TERTIARY, anchor="w"
        ).pack(fill="x", pady=(PAD_COMPACT, 0))

        # Route（两个文件各自的计算级别）
        r_esp = rec.get("route_esp") or ""
        r_gcorr = rec.get("route_gcorr") or ""
        lines = []
        if r_gcorr:
            lines.append(f"G_corr: {r_gcorr}")
        if r_esp:
            lines.append(f"E_sp: {r_esp}")
        if lines:
            for line in lines:
                ctk.CTkLabel(inner, text=line,
                             font=(FONT_MONO, 9), text_color=TEXT_TERTIARY, anchor="w",
                             justify="left", wraplength=520
                ).pack(fill="x")

        # ── 分子结构图 ──
        img_keys = [("img_rx", "分子 RX"), ("img_r", "自由基 R·"), ("img_x", "自由基 X·")]
        has_img = False
        for ik, il in img_keys:
            ip = rec.get(ik, "")
            if ip and os.path.exists(ip):
                if not has_img:
                    img_card = ctk.CTkFrame(scroll_win, fg_color=CARD_BG, corner_radius=RADIUS_CARD)
                    img_card.pack(fill="x", padx=PAD_INNER, pady=(PAD_INNER, 0))
                    ctk.CTkLabel(img_card, text="分子结构",
                                 font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY
                    ).pack(anchor="w", padx=PAD_INNER, pady=(PAD_INNER, PAD_COMPACT))
                    has_img = True
                try:
                    from PIL import Image as PILImage
                    pi = PILImage.open(ip)
                    pi.thumbnail((160, 120))
                    ci = ctk.CTkImage(light_image=pi, dark_image=pi, size=pi.size)
                    ctk.CTkLabel(img_card, text=f"{il}:", font=FONT_REGULAR,
                                 text_color=TEXT_SECONDARY).pack(anchor="w", padx=PAD_INNER)
                    ctk.CTkLabel(img_card, text="", image=ci).pack(anchor="w", padx=PAD_INNER, pady=(0, PAD_COMPACT))
                except Exception:
                    pass

        # ── 运算过程 ──
        detail_card = ctk.CTkFrame(scroll_win, fg_color=CARD_BG, corner_radius=RADIUS_CARD)
        detail_card.pack(fill="x", padx=PAD_INNER, pady=(PAD_INNER, PAD_INNER))

        ctk.CTkLabel(detail_card, text="运算过程",
                     font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=PAD_INNER, pady=(PAD_INNER, PAD_COMPACT))

        detail_text = ctk.CTkTextbox(
            detail_card, height=100,
            font=FONT_MONO_S, wrap="word",
            fg_color=BG_COLOR, text_color=TEXT_PRIMARY,
            corner_radius=RADIUS_INPUT, border_width=0,
        )
        detail_text.pack(fill="x", padx=PAD_INNER, pady=(0, PAD_INNER))
        detail_text.insert("0.0",
            f"  BDE = G(R·) + G(X·) - G(RX)\n"
            f"      = {bde_kcal:.2f} kcal/mol\n"
            f"      = {bde_kj:.2f} kJ/mol\n"
            f"\n"
            f"  反应: {name_rx} → {name_r} + {name_x}"
        )
        detail_text.configure(state="disabled")

