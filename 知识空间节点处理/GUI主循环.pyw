import tkinter as tk
from tkinter import scrolledtext
import ctypes
import threading
import datetime
import os
import queue
import win32event
import win32api
import winerror
import sys

# 导入同目录下的 main 函数
from 知识节点2_判断更新 import main as script_main

# 设置应用的图标
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID()

换行符 = ""
换行符 = "\n"

# 定义主窗口类
class App:
    def __init__(self, root):
        self.root = root  # 初始化主窗口
        self.root.title("知识节点处理")  # 设置窗口标题
        self.root.iconbitmap("D:\\Users\\Ran\\Downloads\\hi223.ico")  # 设置窗口图标
        
        self.is_running = False  # 初始化脚本运行状态为False
        self.script_queue = queue.Queue(maxsize=2)  # 初始化一个最大长度为2的队列
        
        # 创建一个框架用于按钮和复选框的布局
        self.frame = tk.Frame(root)
        self.frame.pack()
        
        # 创建并设置“开始”按钮
        self.start_button = tk.Button(self.frame, text="开始", command=self.start)
        self.start_button.grid(row=0, column=0, padx=(0, 10))  # 使用grid布局，右边留空白
        
        # 创建并设置“停止”按钮
        self.stop_button = tk.Button(self.frame, text="停止", command=self.stop)
        self.stop_button.grid(row=0, column=1, padx=(10, 10))  # 使用grid布局，两边留空白
        
        # 创建一个复选框用于切换模式
        self.mode_var = tk.BooleanVar(value=True)
        self.mode_checkbutton = tk.Checkbutton(self.frame, text="精简模式", variable=self.mode_var)
        self.mode_checkbutton.grid(row=0, column=2, padx=(10, 0))  # 使用grid布局，左边留空白

        # 创建一个带滚动条的文本框，用于显示脚本输出，并使其具有延展性
        self.output_box = scrolledtext.ScrolledText(root, width=100, height=20)
        self.output_box.pack(expand=True, fill='both')
        
        # 创建一个标签显示当前状态
        self.status_label = tk.Label(root, text="状态：未运行")
        self.status_label.pack()

        # 启动脚本
        self.start()

    def start(self):
        if not self.is_running:  # 检查当前是否已在运行
            self.is_running = True  # 设置运行状态为True
            self.status_label.config(text="状态：运行中")  # 更新状态标签
            self.run_script()  # 开始运行脚本

    def stop(self):
        self.is_running = False  # 设置运行状态为False
        self.status_label.config(text="状态：已停止")  # 更新状态标签

    def run_script(self):
        if self.is_running:  # 检查当前是否应继续运行
            if self.script_queue.full():
                #self.output_box.insert(tk.END, "等待中...\n")
                self.output_box.insert(tk.END, f"等待中...{换行符}")
                self.output_box.see(tk.END)  # 自动滚动到文本框底部
                #self.log_message("等待中...\n")
                self.log_message(f"等待中...{换行符}")
            else:
                self.script_queue.put(1)
                # 创建一个新线程来运行脚本，以避免阻塞主线程
                threading.Thread(target=self.execute_script).start()
            # 设置1秒后再次调用run_script方法
            self.root.after(1000, self.run_script)

    def execute_script(self):
        try:
            output = self.run_main_script()
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取当前时间
            # 在插入新数据前检查行数，如果超过100行，则删除多余行
            self.trim_output_box()
            # 在文本框中显示脚本输出和当前时间
            if self.mode_var.get():  # 精简模式
                self.output_box.insert(tk.END, output + 换行符)
            else:  # 详细模式
                message = f"{output}\n{current_time}\n"
                self.output_box.insert(tk.END, message)
            self.output_box.see(tk.END)  # 自动滚动到文本框底部
            self.log_message(output if self.mode_var.get() else message)
        except Exception as e:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取当前时间
            # 在插入新数据前检查行数，如果超过100行，则删除多余行
            self.trim_output_box()
            # 在文本框中显示错误信息和当前时间
            message = f"Error: {e}\n{current_time}\n"
            self.output_box.insert(tk.END, message)
            self.output_box.see(tk.END)  # 自动滚动到文本框底部
            self.log_message(message)
        finally:
            self.script_queue.get()
            self.script_queue.task_done()

    def run_main_script(self):
        import io
        import sys
        # 捕获主脚本的输出
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        try:
            script_main()
            output = new_stdout.getvalue()
            if self.mode_var.get():  # 如果是精简模式
                # 注意开头的 换行符 不可以剔除, 否则会导致多行的gui提示消息无法正常以多行显示
                output = 换行符.join(line for line in output.splitlines() if "【需在GUI显示】" in line) + ""
        finally:
            sys.stdout = old_stdout
        return output

    def trim_output_box(self):
        lines = self.output_box.get("1.0", tk.END).split("\n")
        if len(lines) > 100:
            self.output_box.delete("1.0", f"{len(lines) - 100}.0")

    def log_message(self, message):
        current_time = datetime.datetime.now()
        date_str = current_time.strftime('%Y_%m_%d')
        hour_str = current_time.strftime('%H')
        log_dir = fr"C:\Users\Ran\Desktop\fs_api\知识空间节点处理\GUI主循环日志\{date_str}"
        log_file = f"{log_dir}\\{hour_str}.log"
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(message)

# 创建一个互斥锁以确保只存在一个实例
mutex = win32event.CreateMutex(None, False, "KnowledgeNodeProcessingAppMutex")

if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    print("另一个实例正在运行, 本已取消运行。")
    sys.exit(0)

# 创建主窗口实例
root = tk.Tk()
app = App(root)

# 运行主循环
root.mainloop()

# 释放互斥锁
win32api.CloseHandle(mutex)
