import sys
from pathlib import Path
import subprocess
import datetime
import argparse
from colorama import init, Fore, Style


def add_project_root_to_sys_path():
    # 获取当前文件的绝对路径  
    current_file_path = Path(__file__).resolve()

    # 获取当前文件的父目录的父目录（即项目根目录）
    project_root = current_file_path.parent.parent

    # 将项目根目录添加到 sys.path
    sys.path.append(str(project_root))

add_project_root_to_sys_path()

import feishu_api
import os
import json
import time

# 导入知识节点3_更新下载.pyw中的main函数
from 知识节点3_更新下载 import main as update_main
from 后删_时间间隔 import format_time_difference as format_time_difference
from 知识节点4_判断更新 import *

# 初始化colorama
init(autoreset=True)

def save_data_to_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_data_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def check_for_changes(old_data, new_data):
    changes = {}
    latest_edit_time = None
    
    for node_token, new_item in new_data.items():
        if node_token in old_data:
            if new_item['obj_edit_time'] != old_data[node_token]['obj_edit_time']:
                changes[node_token] = new_item
        else:
            changes[node_token] = new_item

        # 更新最新的编辑时间
        if latest_edit_time is None or new_item['obj_edit_time'] > latest_edit_time:
            latest_edit_time = new_item['obj_edit_time']

    return changes, latest_edit_time


def log_changes(changes):
    log_filename = knowledge_space_log_path
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write(f"Changes detected at {datetime.datetime.now()}:\n")
        for change in changes.values():
            log_file.write(f"Title: {change['title']}, Edit Time: {change['obj_edit_time']}\n")
        log_file.write("\n")

def main(wait_for_exit=False):  # 将wait_for_exit的默认值设为False
    api = feishu_api.FeishuOpenAPI()

    from 知识节点4_判断更新 import space_id

    page_size = 50  # 每页大小 (50为最大值)
    page_token = None  # 第一次请求不填，表示从头开始遍历
    parent_node_token = None  # 父节点token，可选

    result = api.get_knowledge_space_children(space_id, page_size, page_token, parent_node_token)

    if result['code'] == 0:
        new_data = {item['node_token']: item for item in result['data']['items']}
        data_filename = knowledge_space_data_path
        changes_filename = knowledge_space_changes_path
        
        old_data = load_data_from_file(data_filename)
        
        changes, 上次飞书更新时间_时间戳 = check_for_changes(old_data, new_data)

        # 转化时间戳为可读时间
        dt_object = datetime.datetime.fromtimestamp(int(上次飞书更新时间_时间戳))
        上次飞书更新时间_时间 = dt_object.strftime("%H:%M:%S")
        上次飞书更新时间_日期 = dt_object.strftime("%m月%d日")

        更新时间间隔 = format_time_difference(上次飞书更新时间_时间戳)
        
        if changes:
            print("Detected changes:")
            # 获取当前时间
            
            now = datetime.datetime.now().strftime('%H:%M:%S')

            print(f"【需在GUI显示】{now} 存在变化！")
            for change in changes.values():
                print(f"Title: {change['title']}, Edit Time: {change['obj_edit_time']}")
            save_data_to_file(changes_filename, changes)
            log_changes(changes)
            print("Changes have been saved to knowledge_space_changes.json and logged.")

            now = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"【需在GUI显示】{now} 已保存到本地，并记录日志。")

            # 调用知识节点3_更新下载.py脚本中的main函数
            update_main()
            print(f"Executed update_main function")
        else:
            now = datetime.datetime.now().strftime('%H:%M:%S')
            # print(f"【安全】本地均已同步\n上次更新时间: {上次飞书更新时间}\n当前实时时间: {now}")
            print(f"本地均已同步")
            print(f"上次更新时间: {上次飞书更新时间_时间}")
            print(f"当前实时时间: {now}")
            # print(f"【需在GUI显示】{上次飞书更新时间_日期} {上次飞书更新时间_时间} {now}")
            # print(f"【需在GUI显示】{now} {更新时间间隔} ")
            print(f"【需在GUI显示】{更新时间间隔} ")

        # 需更新
        
        save_data_to_file(data_filename, new_data)
        # print(f"{Fore.GREEN}对比完毕本地与云端更新时间, 本地所有数据已为最新。{Style.RESET_ALL}")
    else:
        print(f"Error: {result['msg']}")

    if wait_for_exit:
        input("Press Enter to exit...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Knowledge Space Monitor")
    parser.add_argument("--wait", action="store_true", help="Wait for user input to exit")
    args = parser.parse_args()
    
    main(args.wait)


"""
这样，在运行脚本时，你可以使用 --wait 参数来决定是否需要等待用户手动退出。例如：

python script_name.py --wait

如果不使用 --wait 参数，脚本将会在完成后自动退出。

"""
