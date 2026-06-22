# 🔬 BDE 计算器 — 键解离能计算工具

**专为计算化学设计** — 输入 Gaussian 等软件计算出的能量数据，一键计算 BDE（Bond Dissociation Energy，键解离能）。

---

## 📖 背景知识

### BDE 计算公式

```
键解离能 (BDE) = H(R·) + H(X·) − H(RX)

其中：
  H = E_sp + H_corr
  E_sp     = 高精度方法单点能（如 CCSD(T), CBS-QB3, G4 等）
  H_corr   = 热力学校正量到焓（Thermal correction to Enthalpy）
```

### 单位换算

```
1 Hartree = 627.509 kcal/mol
1 kcal    = 4.184 kJ
```

### 从 Gaussian 输出文件中获取数据

在 Gaussian `.log` 或 `.out` 文件中，搜索以下内容：

```
SCF Done:  E(RB3LYP) = -345.67890123     A.U.
...
Zero-point correction=                           0.123456 (Hartree/Particle)
Thermal correction to Energy=                    0.130123
Thermal correction to Enthalpy=                  0.131234      ← 用这个！
Thermal correction to Gibbs Free Energy=         0.132345

或者直接读取：
Sum of electronic and thermal Enthalpies=        -345.547667   ← 相当于 E_sp + H_corr（用于快速验算）
```

---

## ✨ 功能

| 功能 | 说明 |
|------|------|
| ✅ **单组 BDE 计算** | 输入分子+两个自由基的 E_sp 和 H_corr，直接算出 BDE |
| ✅ **详细计算过程** | 显示每一步的焓值计算、BDE 推导、双单位结果 |
| ✅ **批量计算** | 一次处理多组数据，支持 Excel 导入/导出 |
| ✅ **历史记录** | 自动保存每次计算结果，随时查看和删除 |
| ✅ **单位换算** | 同时输出 kcal/mol 和 kJ/mol |

---

## 🚀 快速开始

### 安装

确保已安装 Python 3.8 或更高版本。

```bash
# 1. 进入程序目录
cd BDECalc

# 2. 安装依赖
pip install -r requirements.txt
```

### 运行

```bash
python main.py
```

### 打包为独立 exe（无需 Python 环境）

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "BDE计算器" main.py
```

打包后 `dist/BDE计算器.exe` 可直接双击运行，无需安装 Python。

---

## 📝 使用指南

### 单组计算

1. 打开程序，进入 **「📐 BDE 计算」** 选项卡
2. 填写反应式名称（可选，如 `CH₃OH → CH₃O· + H·`）
3. 在三列卡片中分别填入分子、自由基1、自由基2的能量数据
4. 点击 **「🧮 计算 BDE」**
5. 右侧显示详细计算过程和结果
6. 点击 **「💾 保存结果」** 保存到历史记录

### 批量计算

1. 切换到 **「📋 批量计算」** 选项卡
2. 点击 **「➕ 添加一行」** 手动输入，或 **「📂 从 Excel 导入」**
3. 双击单元格可编辑数据
4. 点击 **「🧮 全部计算」**
5. 点击 **「💾 导出结果到 Excel」** 保存结果

#### Excel 导入格式

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| 反应名 | E_sp(RX) | H_corr(RX) | E_sp(R·) | H_corr(R·) | E_sp(X·) | H_corr(X·) |

### 历史记录

- 所有计算结果自动保存
- **双击** 条目查看详细计算过程
- 可删除单条或清空全部

---

## 📁 文件结构

```
BDECalc/
├── main.py                # 程序入口
├── requirements.txt       # Python 依赖
├── README.md              # 本文件
├── app/                   # 核心代码
│   ├── __init__.py
│   ├── calculator.py      # BDE 计算逻辑
│   ├── gui.py             # 图形界面
│   └── utils.py           # 工具函数（历史记录管理）
└── data/                  # 运行时自动创建
    └── history.json       # 历史记录文件
```

---

## ⚙️ 技术细节

### 依赖库

| 库 | 用途 |
|---|---|
| `customtkinter` | 现代化桌面 GUI |
| `pandas` | 批量计算时的 Excel 读写 |
| `openpyxl` | Excel 文件支持 |

### 兼容性

- **系统**: Windows / macOS / Linux
- **Python**: 3.8+

---

## 📬 反馈

如有问题或建议，欢迎提交 Issue！

---

*Made with ❤️ for computational chemistry researchers*
