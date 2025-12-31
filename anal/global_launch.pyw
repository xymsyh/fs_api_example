import sys
from pathlib import Path
def add_project_root_to_sys_path():
    # 获取当前文件的绝对路径  
    current_file_path = Path(__file__).resolve()

    # 获取当前文件的父目录的父目录（即项目根目录）
    project_root = current_file_path.parent.parent

    # 将项目根目录添加到 sys.path
    sys.path.append(str(project_root))
add_project_root_to_sys_path()
from feishu_api import FeishuOpenAPI
import copy
import re
import subprocess
import feishu_methods
import class_summary #这些class_* 其实都用到了，只是pylance没发现而已
import class_kfc
import class_plan
import class_gpt


# 非命令行启动
script_path = r"C:\Users\Ran\Desktop\飞书api第二版\autom_tbl_anal.pyw"

## 设置启动参数，以隐藏命令行窗口
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

## 使用subprocess.Popen运行脚本
process = subprocess.Popen(["pythonw", script_path], startupinfo=startupinfo)

# 获取数据
api = FeishuOpenAPI()
header = api.get_sheet_data("egx6yn!A1:ZZ1")['data']['valueRange']['values']
column_letter = feishu_methods.find_column_letter(header, "[每日全文汇总公式]")
daily_data = api.get_sheet_data(f"egx6yn!{column_letter}2:{column_letter}", value_render_option="ToString", date_time_render_option="FormattedString")['data']['valueRange']['values']



def update_and_write_data(daily_data, header, key, keyword, keyword_id):
    """
    更新模式，提取内容，找到列号，然后写入数据。

    :param daily_data: 每日数据
    :param header: 工作表头信息
    :param api: 用于写入数据的API
    :param pattern: 要更新的模式
    :param column_title: 列标题
    """
    module = globals().get(key)
    if module and hasattr(module, 'process'):
        write_data = module.process(daily_data, keyword)
        column_letter = feishu_methods.find_column_letter(header, keyword_id)
        api.write_sheet_data(f"egx6yn!{column_letter}2:{column_letter}", write_data)
        print(f"Data for {keyword} updated and written to column {column_letter}")
    else:
        print(f"Module '{key}' not found or does not have a 'process' method")


## 运行函数
import json
import os

'''# 获取当前脚本所在的目录
script_dir = os.path.dirname(__file__)
# 构建 JSON 文件的完整路径
config_path = os.path.join(script_dir, 'json_keywords.json')

# 使用 JSON 文件
with open(config_path, 'r', encoding='utf-8') as file:
    class_text = json.load(file)'''

data = api.get_sheet_data('70fPAj!B1:B2')
# data_log = data['data']['valueRange']['values'][1][0]
data = data['data']['valueRange']['values'][0][0]
class_text = json.loads(data)

# 原有的处理逻辑
for key, value in class_text.items():
    print("模块名key为：" + key)
    for item in value:
        keyword = item["keyword"]
        keyword_id = item["keyword_id"]
        # 检查是否为有效的数据
        if keyword and keyword_id and "[" in keyword_id: #添加逻辑 "[" in keyword_id 才执行日记体系分析操作
            update_and_write_data(daily_data, header, key, keyword, keyword_id)
        else:
            print(f"Skipping invalid entry: pattern='{keyword}', column_title='{keyword_id}'")
