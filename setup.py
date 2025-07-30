import sys
from cx_Freeze import setup, Executable

# 依赖包
build_exe_options = {
    "packages": ["tkinter", "json", "os", "threading", "time", "pyautogui", "keyboard", "PIL"],
    "excludes": ["unittest"],
    "include_files": [],
    "optimize": 2,
}

# 基础设置
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 使用GUI基础，避免显示控制台窗口

# 可执行文件配置
executables = [
    Executable(
        "numpad_mouse.py",
        base=base,
        target_name="NumpadMouse.exe",
        icon=None,  # 可以添加图标文件路径
    )
]

setup(
    name="NumpadMouse",
    version="1.0.0",
    description="小键盘鼠标控制器 - 用小键盘代替鼠标点击",
    author="Your Name",
    options={"build_exe": build_exe_options},
    executables=executables,
)