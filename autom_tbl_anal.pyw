import requests
import json
from datetime import datetime
import re
from feishu_api import FeishuOpenAPI

# automated_table_analysis 

api = FeishuOpenAPI()

#获取表格数据

# spreadsheet_token = api.obj_token
range = "egx6yn!A2:A"
# data = api.get_sheet_data(spreadsheet_token, range, "ToString", "FormattedString")['data']['valueRange']['values']
daily_data = api.get_sheet_data(range, value_render_option="ToString", date_time_render_option="FormattedString")['data']['valueRange']['values']


print(daily_data)

#更新data数据：将Excel数字日期转换成标准日期并统计字数


def convert_excel_date(data):
    from datetime import datetime, timedelta

    # 初始化字数和行数列表
    char_counts = []
    line_counts = []

    def replace_date_in_string(original_string):
        date_str = original_string.split('\n')[0]
        if date_str.isdigit():
            # Convert the date string and get the parts after the first newline
            base_date = datetime(1899, 12, 30)
            delta = timedelta(days=int(date_str))
            date = base_date + delta
            weekday_map = ['一', '二', '三', '四', '五', '六', '日']
            parts = original_string.split('\n', 1)
            char_count = len(parts[1]) if len(parts) > 1 else 0
            line_count = parts[1].count('\n') + 1 if len(parts) > 1 else 0

            formatted_data = f'{line_count}\n{char_count}'


            # 添加字数和行数到相应的列表
            char_counts.append([char_count])
            line_counts.append([formatted_data])

            formatted_date = f'【{date.strftime("%Y年%m月%d日")} 周{weekday_map[date.weekday()]}】C{char_count}'
            formatted_date = f'周{weekday_map[date.weekday()]} {date.strftime("%m/%d")}'
            formatted_date = f'周{weekday_map[date.weekday()]} {date.strftime("%m/%d")}\n字符数：{char_count}'
            return original_string.replace(date_str, formatted_date, 1)
        else:
            # 如果没有日期，则添加0
            char_counts.append([0])
            line_counts.append([0])
        return original_string

    updated_data = [[replace_date_in_string(item[0])] for item in data]

    return updated_data, char_counts, line_counts
char_counts = []
line_counts = []

daily_data, char_counts, line_counts = convert_excel_date(daily_data)

# 打印更新后的数据
print(daily_data)
print(char_counts)
print(line_counts)

#写入表格
def find_column_letter(header, target):
    """
    Find the column number (as a letter) for a given target in the header row.
    This version of the function searches for a column whose header contains the target string.

    :param header: List of headers.
    :param target: The target header substring to find.
    :return: Column letter as a string or an error message if not found.
    """
    if not header or not header[0]:
        return "Header is empty or invalid"

    for i, column_name in enumerate(header[0]):
        if target in column_name:
            # Convert index to column letter (A=0, B=1, C=2, ...)
            column_number = chr(65 + i)
            return column_number

    return "Target not found in header"

header = api.get_sheet_data("egx6yn!A1:Z1")['data']['valueRange']['values']
column_letter = find_column_letter(header, "[每日全文汇总]")
range = f"egx6yn!{column_letter}2:{column_letter}"
print(api.write_sheet_data(range, daily_data))

#下为计算支出 --------------------------------------------------------

def process_expenses(daily_data):
    def format_total(total):
        if total >= 1000:
            return f"¥{total/1000:.1f}k"
        return f"¥{int(total)}"

    def calculate_expense(text):
        if not isinstance(text, str):
            return "0"
        amounts = re.findall(r'\[支出\[(\d+\.?\d*)\]支出\]', text)
        total = sum(map(float, amounts)) if amounts else 0

        if total == 0:
            return "0\n未支出"

        formatted_total = format_total(total)
        lines = text.split('\n')
        processed_lines = [re.sub(r'\[\d{2}\]\s?', '', line) for line in lines]
        # expense_lines = '\n'.join(line for line in processed_lines if '[支出[' in line)
        expense_lines = '\n'.join(line for line in lines if '[支出[' in line)
        return f"{formatted_total}\n{total}\n{expense_lines}" if amounts else "0"

    for i, value in enumerate(daily_data):
        if value and isinstance(value[0], str):
            daily_data[i] = [calculate_expense(value[0])]

    return daily_data

# 写入数据
column_letter = find_column_letter(header, "[每日支出]")
range = f"egx6yn!{column_letter}2:{column_letter}"
# range = "egx6yn!C2:C50"
write_data = process_expenses(daily_data)
print(api.write_sheet_data(range, write_data))
print("Data write success!")

#上为计算支出 --------------------------------------------------------


# 写入数值计算

# column_letter = find_column_letter(header, "[字数]")
# range = f"egx6yn!{column_letter}2:{column_letter}"
# print(api.write_sheet_data(range, char_counts))

column_letter = find_column_letter(header, "[行数]")
range = f"egx6yn!{column_letter}2:{column_letter}"
print(api.write_sheet_data(range, line_counts))
