import subprocess
import os
import time
from datetime import datetime
from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)

# 定义要执行的脚本路径
script2 = r"C:\Users\Ran\Desktop\fs_api\知识空间节点处理\知识节点2_判断更新.py"
log_path = r'C:\Users\Ran\Desktop\fs_api\知识空间节点处理\自动运行.pylog'

# 读取pylog文件
if os.path.exists(log_path):
    with open(log_path, 'r') as log_file:
        last_run_time_str = log_file.readline().strip().split("Script run at: ")[-1]
        last_run_time = datetime.strptime(last_run_time_str, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        time_diff = (current_time - last_run_time).total_seconds()
        
        print(f"The script was last run {Fore.YELLOW}{int(time_diff)}{Style.RESET_ALL} seconds ago.")
        
        # region: 标识符A, 本存在两个相同的代码
        if time_diff < 6:
            # print(f"{Fore.GREEN}The automation script is considered to be running.{Style.RESET_ALL}")
            pass
        else:
            print(f"{Fore.RED}The automation script is not running.{Style.RESET_ALL}")
        # endregion
else:
    print(f"{Fore.RED}Log file not found. Assuming the script has not been run recently.{Style.RESET_ALL}")

# 更新日志文件
with open(log_path, 'w') as log_file:
    log_file.write(f"Script run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 运行第二个脚本
subprocess.run(["python", script2])

# region: 标识符A, 本存在两个相同的代码
if time_diff < 6:
    print(f"{Fore.GREEN}The automation script is considered to be running.{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}The automation script is not running.{Style.RESET_ALL}")
# endregion

# print(f"{Fore.BLUE}如果上两行均为绿色, 即均正常。{Style.RESET_ALL}")
print(f"↑↑↑ 如果上两行均为绿色, 即均正常 ↑↑↑")
print(f"即说明本地数据最新及自动化脚本运行正常")
