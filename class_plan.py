import re
import feishu_methods
import copy


# 本合并下代码为一个

def process(daily_data, keyword):
    # Function to process each cell
    daily_data_copy = copy.deepcopy(daily_data)

    def process_cell(cell):
        # Find all occurrences of the pattern 
        # print(cell)
        if keyword == "规划" or "FT":
            pattern = fr'\[{keyword}(.*?)\]{keyword}\]'
        else:
            pattern = fr'\[{keyword}\[(.*?)\]{keyword}\]'
        expenses = re.findall(pattern, cell)
        # Return the count of occurrences
        result = [str(len(expenses))] + expenses
        # Join the results as multi-line string
        return '\n'.join(result)

    # Process each cell in the table
    for i in range(len(daily_data_copy)):
        for j in range(len(daily_data_copy[i])):
            daily_data_copy[i][j] = process_cell(daily_data_copy[i][j])

    return daily_data_copy



# 主逻辑流程

if __name__ == "__main__":

    from feishu_api import FeishuOpenAPI
    api = FeishuOpenAPI()
    header = api.get_sheet_data("egx6yn!A1:Z1")['data']['valueRange']['values']
    column_letter = feishu_methods.find_column_letter(header, "[每日全文汇总公式]")
    daily_data_copy = api.get_sheet_data(f"egx6yn!{column_letter}2:{column_letter}", value_render_option="ToString", date_time_render_option="FormattedString")['data']['valueRange']['values']

    keyword = "支出"
    write_data = process(daily_data_copy, keyword)
    print("写入数据")
    print(write_data)
    # sys.exit()

    column_letter = feishu_methods.find_column_letter(header, "[每日支出]")
    print(api.write_sheet_data(f"egx6yn!{column_letter}2:{column_letter}", write_data))