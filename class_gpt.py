import re
import feishu_methods

# 本合并下代码为一个 

def process(data, keyword):
    """ 
    Processes and analyzes group purchase data.
    This function integrates multiple steps such as extracting, modifying, calculating totals,
    extracting numbers with signs, accumulating values, merging accumulated values, and formatting output.
    """
    def extract_info(entry):
        pattern = fr'\[{keyword}\[([\+\-0-9]+)\]{keyword}\]'
        entry_content = str(entry[0]) if entry else ''
        return re.findall(pattern, entry_content)

    def standardize_info_format(info):
        return [item + '+0' if item.count('+') + item.count('-') == 1 else item for item in info] or ['+0+0']
        # 在实现ChatGPT功能的时候，仅修改了上面这行代码的「'+0' + item」顺序为「item + '+0'」以及后面的一个输出格式
        # 上述修改仅涉及两行代码，目前的实现需要输入数据包含「正号」或「负号」

    def calculate_totals(info):
        if len(info) > 1:
            total_days, total_times = 0, 0
            for item in info:
                parts = re.split(r'(\+|\-)', item)
                total_days += int(parts[0] + parts[1] + parts[2])
                total_times += int(parts[3] + parts[4])
            return f'+{total_days}+{total_times}'
        return info[0]

    def extract_number_with_sign(entry, position):
        pattern = r'[+-]?\d+'
        numbers_with_sign = re.findall(pattern, entry) if entry else []
        return numbers_with_sign[position] if len(numbers_with_sign) > position else None

    def accumulate_values(numbers, decrement=False):
        accumulated = []
        current_value = 0
        for number in reversed(numbers):
            if int(number) >= 1 and current_value < 0:
                current_value += int(number) + abs(current_value) + 1
            else:
                current_value += int(number) if number is not None else 0
            # print(current_value)
            if decrement:
                current_value -= 1
                # print(current_value)
            accumulated.append(max(-99, current_value)) #这行代码限制了负数日期的最大值
        return list(reversed(accumulated))

    # Process each entry in the data
    processed_data = [calculate_totals(standardize_info_format(extract_info(entry))) for entry in data]
    print("提取数据：")
    print(processed_data)
    

    # Extract and accumulate values
    first_numbers = [extract_number_with_sign(entry, 0) for entry in processed_data]
    print("迭代前数值：")
    print(first_numbers)
    second_numbers = [extract_number_with_sign(entry, 1) for entry in processed_data]
    acc_first_numbers = accumulate_values(first_numbers, decrement=True)
    print("迭代后数值：")
    print(acc_first_numbers)
    acc_second_numbers = accumulate_values(second_numbers)

    # Merge and format the accumulated values 下一行代码定义了输出格式
    merged_values = []
    for first, second in zip(acc_first_numbers, acc_second_numbers):
        # merged_values.append(f"{first}" if first < 0 else f"{first},{second}")
        merged_values.append(f"{first}")

    print([[value] for value in merged_values])
    return [[value] for value in merged_values]

# 主逻辑流程

if __name__ == "__main__":

    from feishu_api import FeishuOpenAPI
    api = FeishuOpenAPI()
    header = api.get_sheet_data("egx6yn!A1:Z1")['data']['valueRange']['values']
    column_letter = feishu_methods.find_column_letter(header, "[每日全文汇总]")
    daily_data = api.get_sheet_data(f"egx6yn!{column_letter}2:{column_letter}")['data']['valueRange']['values']

    keyword = "肯德基"
    write_data = process(daily_data, keyword)
    print("写入数据")
    print(write_data)
    # sys.exit()

    column_letter = feishu_methods.find_column_letter(header, "[新肯德基团购套餐剩余使用次数]")
    print(api.write_sheet_data(f"egx6yn!{column_letter}2:{column_letter}", write_data))