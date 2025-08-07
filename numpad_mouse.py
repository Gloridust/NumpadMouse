import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import time
import pyautogui
import keyboard
from PIL import Image, ImageTk
import sys

class NumpadMouseApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("小键盘鼠标 - NumpadMouse")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # 配置文件路径
        self.config_file = "numpad_config.json"
        
        # 数字键位配置 (1-9对应小键盘位置，0为特殊键)
        self.positions = {}
        self.load_config()
        
        # 当前模式：'setup' 或 'running'
        self.mode = 'setup'
        self.is_listening = False
        
        # 位置标签窗口列表
        self.position_labels = []
        
        # 创建界面
        self.create_widgets()
        
        # 禁用pyautogui的安全机制
        pyautogui.FAILSAFE = False
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="小键盘鼠标控制器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 模式选择框架
        mode_frame = ttk.LabelFrame(main_frame, text="模式选择", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.mode_var = tk.StringVar(value="setup")
        setup_radio = ttk.Radiobutton(mode_frame, text="设置模式", variable=self.mode_var, 
                                     value="setup", command=self.switch_mode)
        setup_radio.grid(row=0, column=0, padx=(0, 20))
        
        running_radio = ttk.Radiobutton(mode_frame, text="运行模式", variable=self.mode_var, 
                                       value="running", command=self.switch_mode)
        running_radio.grid(row=0, column=1)
        
        # 设置模式框架
        self.setup_frame = ttk.LabelFrame(main_frame, text="设置点击位置", padding="10")
        self.setup_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 小键盘布局显示
        keypad_frame = ttk.Frame(self.setup_frame)
        keypad_frame.grid(row=0, column=0, padx=(0, 20))
        
        # 创建小键盘按钮 (3x3 + 0键)
        self.keypad_buttons = {}
        keypad_layout = [
            [7, 8, 9],
            [4, 5, 6],
            [1, 2, 3],
            [None, 0, None]
        ]
        
        for row_idx, row in enumerate(keypad_layout):
            for col_idx, num in enumerate(row):
                if num is not None:
                    btn = ttk.Button(keypad_frame, text=str(num), width=8,
                                   command=lambda n=num: self.set_position(n))
                    btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)
                    self.keypad_buttons[num] = btn
        
        # 位置信息显示
        info_frame = ttk.Frame(self.setup_frame)
        info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N))
        
        ttk.Label(info_frame, text="已设置的位置:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        # 位置列表
        self.position_listbox = tk.Listbox(info_frame, height=10, width=30)
        self.position_listbox.grid(row=1, column=0, pady=(5, 0))
        
        # 清除按钮
        clear_btn = ttk.Button(info_frame, text="清除所有位置", command=self.clear_all_positions)
        clear_btn.grid(row=2, column=0, pady=(10, 0))
        
        # 运行模式框架
        self.running_frame = ttk.LabelFrame(main_frame, text="运行控制", padding="10")
        self.running_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # 控制按钮
        control_frame = ttk.Frame(self.running_frame)
        control_frame.grid(row=0, column=0, columnspan=2)
        
        self.start_btn = ttk.Button(control_frame, text="开始监听", command=self.start_listening)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="停止监听", command=self.stop_listening, state="disabled")
        self.stop_btn.grid(row=0, column=1)
        
        # 状态显示
        self.status_label = ttk.Label(self.running_frame, text="状态: 未开始", font=("Arial", 10))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        # 使用说明
        help_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="10")
        help_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 0))
        
        help_text = """设置模式：
1. 点击小键盘数字按钮
2. 在屏幕上点击要设置的目标位置
3. 重复以上步骤设置所有需要的位置

运行模式：
1. 点击"开始监听"
2. 按下小键盘对应数字键即可模拟鼠标点击
3. 按ESC键可以停止监听"""
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.grid(row=0, column=0, sticky=tk.W)
        
        # 初始化界面状态
        self.switch_mode()
        self.update_position_list()
        
    def switch_mode(self):
        """切换模式"""
        self.mode = self.mode_var.get()
        
        if self.mode == 'setup':
            self.setup_frame.grid()
            self.running_frame.grid_remove()
        else:
            self.setup_frame.grid_remove()
            self.running_frame.grid()
            
    def set_position(self, num):
        """设置指定数字键的点击位置"""
        self.root.withdraw()  # 隐藏主窗口
        
        # 创建全屏透明窗口用于捕获点击
        capture_window = tk.Toplevel()
        capture_window.attributes('-fullscreen', True)
        capture_window.attributes('-alpha', 0.3)
        capture_window.configure(bg='red')
        capture_window.attributes('-topmost', True)
        
        # 添加提示标签
        label = tk.Label(capture_window, text=f"请点击数字键 {num} 对应的目标位置\n按ESC取消", 
                        font=("Arial", 20), bg='red', fg='white')
        label.place(relx=0.5, rely=0.5, anchor='center')
        
        def on_click(event):
            x, y = event.x_root, event.y_root
            self.positions[str(num)] = {'x': x, 'y': y}
            self.save_config()
            self.update_position_list()
            capture_window.destroy()
            self.root.deiconify()  # 显示主窗口
            messagebox.showinfo("设置成功", f"数字键 {num} 的位置已设置为: ({x}, {y})")
            
        def on_escape(event):
            capture_window.destroy()
            self.root.deiconify()
            
        capture_window.bind('<Button-1>', on_click)
        capture_window.bind('<Escape>', on_escape)
        capture_window.focus_set()
        
    def clear_all_positions(self):
        """清除所有位置设置"""
        if messagebox.askyesno("确认", "确定要清除所有位置设置吗？"):
            self.positions.clear()
            self.save_config()
            self.update_position_list()
            
    def update_position_list(self):
        """更新位置列表显示"""
        self.position_listbox.delete(0, tk.END)
        for num in sorted(self.positions.keys(), key=int):
            pos = self.positions[num]
            self.position_listbox.insert(tk.END, f"数字 {num}: ({pos['x']}, {pos['y']})")
            
    def start_listening(self):
        """开始监听键盘"""
        if not self.positions:
            messagebox.showwarning("警告", "请先在设置模式中设置至少一个位置！")
            return
            
        self.is_listening = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="状态: 正在监听小键盘...")
        
        # 显示位置标签
        self.show_position_labels()
        
        # 在新线程中监听键盘
        self.listen_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        self.listen_thread.start()
        
    def stop_listening(self):
        """停止监听键盘"""
        self.is_listening = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="状态: 已停止监听")
        
        # 隐藏位置标签
        self.hide_position_labels()
        
    def keyboard_listener(self):
        """键盘监听线程"""
        def on_key_press(event):
            if not self.is_listening:
                return
                
            # 获取按键名称
            key_name = event.name
            
            # 处理小键盘数字键
            numpad_map = {
                'kp_0': '0', 'kp_1': '1', 'kp_2': '2', 'kp_3': '3', 'kp_4': '4',
                'kp_5': '5', 'kp_6': '6', 'kp_7': '7', 'kp_8': '8', 'kp_9': '9'
            }
            
            # 也支持主键盘数字键
            if key_name in numpad_map:
                num = numpad_map[key_name]
            elif key_name in '0123456789':
                num = key_name
            elif key_name == 'esc':
                self.root.after(0, self.stop_listening)
                return
            else:
                return
                
            # 执行点击
            if num in self.positions:
                pos = self.positions[num]
                try:
                    # 先隐藏标签
                    self.root.after(0, self.hide_position_labels)
                    # 等待一小段时间确保标签隐藏
                    time.sleep(0.05)
                    # 执行点击
                    pyautogui.click(pos['x'], pos['y'])
                    print(f"点击位置 {num}: ({pos['x']}, {pos['y']})")
                    # 点击完成后重新显示标签
                    self.root.after(100, self.show_position_labels)
                except Exception as e:
                    print(f"点击失败: {e}")
                    # 即使点击失败也要重新显示标签
                    self.root.after(100, self.show_position_labels)
                    
        # 注册键盘监听
        keyboard.on_press(on_key_press)
        
        # 保持监听状态
        while self.is_listening:
            time.sleep(0.1)
            
        # 取消监听
        keyboard.unhook_all()
        
    def show_position_labels(self):
        """显示位置标签"""
        for num, pos in self.positions.items():
            # 创建小的透明窗口
            label_window = tk.Toplevel(self.root)
            label_window.overrideredirect(True)  # 去除窗口边框
            label_window.attributes('-topmost', True)  # 置顶显示
            label_window.attributes('-alpha', 0.7)  # 半透明
            
            # 创建圆形标签
            canvas = tk.Canvas(label_window, width=40, height=40, highlightthickness=0, bg='black')
            canvas.pack()
            
            # 绘制圆形背景
            canvas.create_oval(2, 2, 38, 38, fill='#4CAF50', outline='#2E7D32', width=2)
            
            # 绘制数字文本
            canvas.create_text(20, 20, text=str(num), fill='white', font=('Arial', 14, 'bold'))
            
            # 设置窗口位置（标签中心对准点击位置）
            x = pos['x'] - 20  # 标签宽度40，所以减去20使中心对准
            y = pos['y'] - 20  # 标签高度40，所以减去20使中心对准
            label_window.geometry(f"40x40+{x}+{y}")
            
            # 强制更新窗口显示
            label_window.update()
            
            # 设置窗口穿透（Windows系统）- 在窗口显示后设置
            def set_click_through():
                try:
                    import ctypes
                    # 获取窗口句柄
                    hwnd = label_window.winfo_id()
                    
                    # 设置窗口样式为穿透
                    GWL_EXSTYLE = -20
                    WS_EX_LAYERED = 0x80000
                    WS_EX_TRANSPARENT = 0x20
                    
                    # 获取当前扩展样式
                    ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                    # 添加透明和穿透属性
                    new_ex_style = ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT
                    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_ex_style)
                except Exception as e:
                    print(f"设置窗口穿透失败: {e}")
            
            # 延迟设置穿透，确保窗口已完全创建
            label_window.after(100, set_click_through)
            
            # 添加到标签列表
            self.position_labels.append(label_window)
            
    def hide_position_labels(self):
        """隐藏位置标签"""
        for label_window in self.position_labels:
            try:
                label_window.destroy()
            except:
                pass
        self.position_labels.clear()
        
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.positions = json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.positions = {}
            
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.positions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
            
    def on_closing(self):
        """程序关闭时的处理"""
        if self.is_listening:
            self.stop_listening()
        # 清理所有标签窗口
        self.hide_position_labels()
        self.root.destroy()
        
    def run(self):
        """运行程序"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = NumpadMouseApp()
    app.run()