from feishu_api import FeishuOpenAPI

import sys

api=FeishuOpenAPI()

# --- 获取日期 ---

A1_data = api.get_sheet_data("TSnyxR!A1:A1")["data"]["valueRange"]["values"]
print("当前A1数据: " + str(A1_data))

# --- 判断A1是否今日 ---
from datetime import datetime, timedelta

def check_and_update_date(A1_data):
    """
    检查A1_data中的日期是否为今天的日期。
    如果不是，则更新为今天的日期。
    
    :param A1_data: 假设为Excel中的日期数据，格式为 [[days_since_1900]]
    :return: (is_date_today, updated_A1_data)
    """
    # Excel中的日期是从1900年1月1日开始计数的，Python的datetime从公元元年开始计数
    # 因此需要一个偏移量
    excel_start_date = datetime(1899, 12, 30).date()  # Excel的起始日期
    days_from_excel_start = A1_data[0][0]  # 从Excel获取的天数
    date_from_excel = excel_start_date + timedelta(days=days_from_excel_start)  # 计算实际日期

    # 获取今天的日期
    today = datetime.today().date()

    # 判断日期是否等于今天，并设置布尔变量
    is_date_today = date_from_excel == today

    # 如果日期不是今天，则更新A1_data为今天的日期
    if not is_date_today:
        days_since_excel_start_today = (today - excel_start_date).days
        A1_data = [[days_since_excel_start_today]]
        # is_date_today = True  # 更新布尔变量，因为现在A1_data代表今天的日期

    return is_date_today, A1_data

is_date_today, updated_A1_data = check_and_update_date(A1_data)
print("Is date today:", is_date_today)
print("Updated A1_data:", updated_A1_data)

# --- A1不是今日：新建一行并写入当前日期 ---
import requests
def insert_rows_in_feishu_sheet(spreadsheet_token, sheet_id, start_index, end_index, inherit_style, access_token):
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/insert_dimension_range"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "dimension": {
            "sheetId": sheet_id,
            "majorDimension": "ROWS",
            "startIndex": start_index,
            "endIndex": end_index
        },
        "inheritStyle": inherit_style
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
if is_date_today == False:
    spreadsheet_token = api.obj_token
    sheet_id = "TSnyxR"
    start_index = 0
    end_index = 1
    inherit_style = "BEFORE"
    access_token = api.tenant_access_token

    result = insert_rows_in_feishu_sheet(spreadsheet_token, sheet_id, start_index, end_index, inherit_style, access_token)
    print('插入行：' + str(result))
    
    
    result = api.write_sheet_data("TSnyxR!A1:A1", updated_A1_data)
    print('写入今天日期：' + str(result))


# --- 获取None值位置 ---

response = api.get_sheet_data("TSnyxR!A1:ZZ1", value_render_option="ToString", date_time_render_option="FormattedString")["data"]["valueRange"]["values"]
def find_first_none_position(row_data):
    """
    找出给定行数据中首个None值的位置，并返回其Excel列标识。
    
    :param row_data: 类Excel表格的行数据
    :return: 首个None值的Excel列标识，例如 'E1', 'AA1' 等
    """
    # 寻找首个None的位置
    first_none_index = next((i for i, x in enumerate(row_data[0]) if x is None), None)

    # 将索引转换为Excel列标识
    if first_none_index is not None:
        # 转换索引到列字母（考虑超过26列的情况）
        def get_column_letter(index):
            column_letter = ''
            while index > 0:
                index, remainder = divmod(index - 1, 26)
                column_letter = chr(65 + remainder) + column_letter
            return column_letter

        column_letter = get_column_letter(first_none_index + 1)
        return f"{column_letter}1"
    else:
        return "None not found"

# 示例使用
none_position = find_first_none_position(response)
print('None值位置: ' + none_position)


# --- 获取图片 ---
# sys.exit()

import os
from PIL import Image
import io

def get_latest_image_path(directory):
    """ 返回给定目录中最新的图片文件路径 """
    all_files = [os.path.join(directory, f) for f in os.listdir(directory)]
    all_images = [f for f in all_files if os.path.isfile(f) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    if not all_images:
        return None
    latest_image = max(all_images, key=os.path.getmtime)
    return latest_image

def convert_image_to_binary(image_path):
    """ 将图片转换为二进制数据 """
    with open(image_path, "rb") as image_file:
        return image_file.read()

# 示例使用
directory = "C:\\Users\\Ran\\Pictures\\Quicker截图"
latest_image_path = get_latest_image_path(directory)
if latest_image_path:
    image_data = convert_image_to_binary(latest_image_path)
    print("Image data:", image_data[:20])  # 打印前20个字节以验证
else:
    print("No images found in the directory.")

# --- 使用图片 ---

import requests

def upload_image_to_feishu(spreadsheet_token, cell_range, image_data, image_name, access_token):
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_image"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "range": cell_range,
        "image": list(image_data),
        "name": image_name
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# 使用示例
spreadsheet_token = api.obj_token
cell_range = f"TSnyxR!{none_position}:{none_position}"
# image_data = [123, 32, 42, 23]  # 这里应该是你的图片二进制数据
image_name = "测试名称01091151.png"
access_token = api.tenant_access_token

result = upload_image_to_feishu(spreadsheet_token, cell_range, image_data, image_name, access_token)
print(result)
