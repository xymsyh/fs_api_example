# 本复制与12261540用于备份回退

def find_column_letter(header_data, target_id_text):
    """
    Find the column number (as a letter) for a given target in the header row.
    This version of the function searches for a column whose header contains the target string.

    :param header: List of headers.
    :param target: The target header substring to find.
    :return: Column letter as a string or an error message if not found.
    """
    if not header_data or not header_data[0]:
        return "Header is empty or invalid"

    for i, column_name in enumerate(header_data[0]):
        if target_id_text in column_name:
            # Convert index to column letter (A=0, B=1, C=2, ...)
            column_number = chr(65 + i)
            return column_number

    return "Target not found in header"

# 测试代码（如果需要）
if __name__ == "__main__":
    # 测试 find_column_letter 函数
    header_example = [["姓名", "年龄", "职业", "[肯德基团购套餐剩余使用次数]"]]
    print(find_column_letter(header_example, "[肯德基团购套餐剩余使用次数]"))