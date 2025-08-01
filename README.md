# NumpadMouse - 小键盘鼠标控制器

一个用小键盘和数字键盘代替鼠标点击的Windows软件。

## 功能特点

- **设置模式**：用鼠标标记每个数字对应的点击位置
- **运行模式**：按下对应数字键即可模拟鼠标点击
- **配置保存**：点击位置配置自动保存在同目录的JSON文件中
- **可执行程序**：支持编译为独立的Windows可执行文件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python numpad_mouse.py
```

## 使用说明

### 设置模式
1. 选择"设置模式"
2. 点击小键盘数字按钮（1-9, 0）
3. 在屏幕上点击要设置的目标位置
4. 重复以上步骤设置所有需要的位置

### 运行模式
1. 选择"运行模式"
2. 点击"开始监听"
3. 按下小键盘对应数字键即可模拟鼠标点击
4. 按ESC键可以停止监听

## 编译为可执行文件

### 方法一：使用批处理脚本（推荐）
```bash
build.bat
```

### 方法二：手动编译
```bash
pip install -r requirements.txt
python setup.py build
```

编译完成后，可执行文件将位于 `build` 目录中。

## 配置文件

程序会在同目录下创建 `numpad_config.json` 文件来保存点击位置配置：

```json
{
  "1": {"x": 100, "y": 200},
  "2": {"x": 300, "y": 400},
  ...
}
```

## 支持的按键

- 小键盘数字键：0-9
- 主键盘数字键：0-9
- ESC键：停止监听

## 注意事项

1. 程序需要管理员权限才能正常监听键盘和模拟鼠标点击
2. 运行时请确保目标应用程序处于前台
3. 建议在使用前先测试设置的位置是否正确

## 系统要求

- Windows 7/8/10/11
- Python 3.7+ （如果从源码运行）

## 依赖包

- `pyautogui`: 鼠标自动化
- `keyboard`: 键盘监听
- `Pillow`: 图像处理
- `cx-Freeze`: 程序编译
- `tkinter`: GUI界面（Python内置）