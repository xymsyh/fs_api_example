import time
import subprocess
import win32event
import win32api
import winerror
from datetime import datetime

# 创建一个互斥体，用于确保只有一个实例在运行
mutex = win32event.CreateMutex(None, False, "Global\\MyUniqueAppMutexName")

if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    print("Another instance is already running. Exiting.")
    exit(1)

def get_switch_status(switch_file_path):
    """读取开关文件并提取状态"""
    try:
        # 打开开关文件并读取第一行内容
        with open(switch_file_path, 'r', encoding='utf-8') as switch_file:
            switch_status = switch_file.readline().strip()
        # 提取方头括号【】中的值
        status = switch_status[switch_status.find('【') + 1:switch_status.find('】')]
        return status
    except Exception as e:
        # 如果读取文件时发生错误，输出错误信息并返回None
        print(f"Error reading switch file: {e}")
        return None

def run_script_and_log(script_path, log_path):
    """运行指定的Python脚本并记录日志"""
    try:
        # 写入当前时间到日志文件
        with open(log_path, 'w', encoding='utf-8') as log_file:
            log_file.write(f"Script run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 使用subprocess模块运行Python脚本
        subprocess.Popen(['python', script_path], shell=True)
    except Exception as e:
        # 如果运行脚本或写入日志时发生错误，输出错误信息
        print(f"Error running script or logging: {e}")

try:
    while True:
        # 读取开关文件的内容并判断状态
        switch_path = r'C:\Users\Ran\Desktop\fs_api\知识空间节点处理\自动运行.开关'
        status = get_switch_status(switch_path)

        # 输出判断结果
        if status:
            print(f"Switch status: {status}")

            if status == "开":
                # 指定要运行的Python脚本的路径
                script_path = r'C:\Users\Ran\Desktop\fs_api\知识空间节点处理\知识节点2_判断更新.py'

                # 指定日志文件的路径
                log_path = r'C:\Users\Ran\Desktop\fs_api\知识空间节点处理\自动运行.pylog'

                # 运行脚本并记录日志
                run_script_and_log(script_path, log_path)

        # 等待五秒钟
        time.sleep(5)

finally:
    # 释放互斥体
    if mutex:
        win32event.CloseHandle(mutex)
