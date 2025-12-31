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

import feishu_api

import json
import os
from colorama import init, Fore, Style

init(autoreset=True)

from 知识节点4_判断更新 import file_path, output_dir


api = feishu_api.FeishuOpenAPI()

# 然定义表格替换处理逻辑
def process_json_string_全览sheet写入本地的格式处理(json_str):
    # 处理换行符: 将换行符标记使用真实换行
    json_str = json_str.replace('\\n', '\n')  # 处理换行符

    # 剔除空的待办事项说明、标记 (其说明与标记记录在 {} 中)
    json_str = json_str.replace('{}[', '[')  # 将空的{}剔除
    json_str = json_str.replace('}[', '}\n[')  # 将非空的{}执行换行操作

    # 剔除空的null所在行
    lines = json_str.split('\n')
    lines = [line for line in lines if line.strip() != 'null,']
    json_str = '\n'.join(lines)

    return json_str

# 定义处理函数
def process_data(data):
    for key, value in data.items():
        obj_type = value.get('obj_type', 'unknown')
        title = value.get('title', 'No Title')
        obj_token = value.get('obj_token', 'unknown')

        if obj_type == 'sheet':
            print(f"Sheet Title: {title}")
            handle_sheet(obj_token, title)
        elif obj_type == 'bitable':
            print(f"Bitable Title: {title}")
            handle_bitable(obj_token, title)
        elif obj_type == 'docx':
            print(f"Docx Title: {title}")
            handle_docx(obj_token, title, obj_type)
        else:
            print(f"Unknown Type Title: {title}")

# region: 表格处理
def column_index_to_letter(column_index):
    """将列索引转换为Excel列字母表示"""
    letters = ''
    while column_index > 0:
        column_index, remainder = divmod(column_index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters

def handle_sheet(obj_token, title):
    # 获取工作表信息
    sheets_response = api.get_sheets(obj_token)
    if sheets_response and sheets_response.get('code') == 0:

        # 定义输出文件路径
        obj_type_dir = os.path.join(output_dir, 'sheet')
        os.makedirs(obj_type_dir, exist_ok=True)
        output_file_path = os.path.join(obj_type_dir, obj_token, f"_info_sheet.txt")
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # 将信息写入文件
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            json.dump(sheets_response, output_file, ensure_ascii=False, indent=4)
        print(f"Sheet data for {title} saved to {output_file_path}")

        # 遍历每个工作表
        sheets_info = sheets_response['data']['sheets']
        for sheet in sheets_info:
            sheet_id = sheet['sheet_id']
            if 'grid_properties' in sheet and sheet['resource_type'] == 'sheet':

                # region: 写入表格到本地的逻辑

                # 定义表格范围
                column_count = sheet['grid_properties'].get('column_count', 1)
                end_column_letter = column_index_to_letter(column_count)
                range_str = f"{sheet_id}!A1:{end_column_letter}"

                # 获取表格数据
                sheet_data_response = api.get_sheet_data(range_str, obj_token)

                # 写入文件
                if sheet_data_response and sheet_data_response.get('code') == 0:
                    def save_sheet_data(sheet_data, title, sheet, output_dir, obj_token, sheet_id):
                        # 定义输出文件路径
                        obj_type_dir = os.path.join(output_dir, 'sheet')
                        os.makedirs(obj_type_dir, exist_ok=True)
                        output_file_path = os.path.join(obj_type_dir, obj_token, f"{sheet_id}.txt")
                        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                        # 写入文件 (然定逻辑)
                        json_str = json.dumps(sheet_data, ensure_ascii=False, indent=4)
                        json_str = process_json_string_全览sheet写入本地的格式处理(json_str)

                        with open(output_file_path, 'w', encoding='utf-8') as output_file:
                            output_file.write(json_str)

                        print(f"Sheet data for {title} - {sheet['title']} saved to {output_file_path}")

                    def check_sheet_data(sheet_data):
                        try:
                            # 判断 A1 单元格内容是否存在并且是否包含「[然标]本表不git[然标]」
                            if not sheet_data[0][0] or "[然标]本表不git[然标]" not in sheet_data[0][0]:
                                return 1  # 代码 1 表示可以执行后续操作
                            else:
                                return 2  # 代码 2 表示 A1 单元格包含指定内容，不执行后续操作
                        except (IndexError, TypeError):
                            return 1  # 代码 1 表示可以执行后续操作，即使发生异常

                    # 获取 sheet_data
                    sheet_data = sheet_data_response['data']['valueRange']['values']
                    status_code = check_sheet_data(sheet_data)

                    if status_code == 1:
                        save_sheet_data(sheet_data, title, sheet, output_dir, obj_token, sheet_id)
                    elif status_code == 2:
                        print(f"Sheet data for {title} - {sheet['title']} is marked as [然标]本表不git[然标], skipped.")
                        print(f"{Fore.GREEN}解释上述行:「{title} - {sheet['title']}」A1单元格包含了标记 [然标]本表不git[然标]，表示该行的内容不进行git管理，因此跳过该行写入本地。{Style.RESET_ALL}")
                else:
                    print(f"Failed to get sheet data for {title} - {sheet['title']}")
            else:
                # 定义输出文件路径
                obj_type_dir = os.path.join(output_dir, 'sheet')
                os.makedirs(obj_type_dir, exist_ok=True)
                output_file_path = os.path.join(obj_type_dir, obj_token, f"{sheet_id}.txt")
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                # 写入无 grid_properties 的信息，包括所有详细信息
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(f"Sheet ID: {sheet_id}\n")
                    output_file.write(f"Title: {sheet['title']}\n")
                    output_file.write(f"Hidden: {sheet.get('hidden', False)}\n")
                    output_file.write(f"Index: {sheet.get('index', 'N/A')}\n")
                    output_file.write(f"Resource Type: {sheet.get('resource_type', 'N/A')}\n")
                    output_file.write("No corresponding grid_properties.\n")
                print(f"Sheet info for {title} - {sheet['title']} with no grid_properties saved to {output_file_path}")
    else:
        print(f"Failed to get sheets info for {title}")

# endregion

# region: 多维表格处理

def handle_bitable(obj_token, title):
    # 获取多维表格信息
    bitable_response = api.list_bitable_tables(obj_token)
    if bitable_response and bitable_response.get('code') == 0:
        bitable_data = bitable_response['data']

        # 定义输出文件路径
        obj_type_dir = os.path.join(output_dir, 'bitable')
        os.makedirs(obj_type_dir, exist_ok=True)
        output_file_path = os.path.join(obj_type_dir, obj_token, f"_info_table.txt")
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # 将多维表格信息写入文件
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            json.dump(bitable_response, output_file, ensure_ascii=False, indent=4)
        print(f"Bitable data for {title} saved to {output_file_path}")

        # 对每个表执行 search_bitable_records
        for item in bitable_data.get('items', []):
            table_id = item['table_id']
            table_title = item['name']
            records_response = api.search_bitable_records(obj_token, table_id)
            if records_response and records_response.get('code') == 0:
                records_data = records_response['data']

                # 定义输出文件路径
                table_output_file_path = os.path.join(obj_type_dir, obj_token, f"{table_id}.txt")
                os.makedirs(os.path.dirname(table_output_file_path), exist_ok=True)

                # 将记录内容写入文件
                with open(table_output_file_path, 'w', encoding='utf-8') as output_file:
                    json.dump(records_data, output_file, ensure_ascii=False, indent=4)
                print(f"Records for table {table_title} ({table_id}) saved to {table_output_file_path}")
            else:
                print(f"Failed to get records for table {table_title} ({table_id})")
    else:
        print(f"Failed to get bitable data for {title}")

# endregion

# region: 文档处理

def handle_docx(obj_token, title, obj_type):
    # 获取文档内容
    document_content_response = api.get_document_raw_content(obj_token)
    if document_content_response and document_content_response.get('code') == 0:
        document_content = document_content_response['data']['content']
        # 定义输出文件路径
        obj_type_dir = os.path.join(output_dir, obj_type)
        os.makedirs(obj_type_dir, exist_ok=True)
        output_file_path = os.path.join(obj_type_dir, obj_token, f"main.txt")
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        # 将内容写入文件
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(document_content)
        print(f"Document content saved to {output_file_path}")
    else:
        print(f"Failed to get document content for {title}")

# endregion

def main():
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 处理数据
        process_data(data)
    else:
        print(f"The file {file_path} does not exist.")

if __name__ == "__main__":
    main()
