from feishu_api import FeishuOpenAPI
import datetime

api = FeishuOpenAPI()
sheet_id_write = api.config.get('sheet_id_write', '')

def find_index_date(use_local_data=True, time_zone=0):
    # 考虑时区偏移后的当前日期和时间
    current_datetime_with_offset = datetime.datetime.now() + datetime.timedelta(hours=time_zone)
    # 转换为只有日期的格式
    today_with_offset = current_datetime_with_offset.strftime("%m/%d")

    if use_local_data:
        # 导入 datetime

        # 设置初始日期字符串
        initial_date_str = str(api.config.get('a2_date', ''))

        # 将字符串转换为日期对象，格式为年-月-日
        initial_date = datetime.datetime.strptime(initial_date_str, "%Y-%m-%d").date()

        # 获取考虑时区偏移后的当前日期
        today = current_datetime_with_offset.date()

        # 计算差异（天数）
        days_difference = (initial_date - today).days

        # 计算单元格位置
        index_number = 2 + days_difference

    else:
        date_data = api.get_sheet_data("9ba2f5!A1:A", value_render_option="ToString", date_time_render_option="FormattedString")
        
        def find_date_index(data, date):
            for i, row in enumerate(data['data']['valueRange']['values'], 1):
                if row and row[0].endswith(date):
                    return i
            return None
        
        index_number = find_date_index(date_data, today_with_offset)
    
    print(f"今天的日期位于单元格: A{index_number}")
    return index_number

def find_index_hour(time_zone=0):
    letters = "BCDEFGHIJKLMNOPQRSTUVWXY"
    hour = datetime.datetime.now().hour

    # 应用时区调整
    adjusted_hour = (hour + time_zone) % 24

    # 由于 letters 是从 23 点开始的，所以我们用 23 减去调整后的小时数
    return letters[23 - adjusted_hour]

def find_now_time():
        time = datetime.datetime.now()
        return time

def output_current_data(keep_5_clock=False, time_zone=0): #time_zone为时区逻辑
    index_number = find_index_date(time_zone=time_zone)
    if keep_5_clock == True:
        index_letter = "T" #在飞书表中T列对应每日5点
    else:
        index_letter = find_index_hour(time_zone=time_zone)
        # 时区的逻辑应该在这里更新
    
    current_data = api.get_sheet_data(f"{sheet_id_write}!{index_letter}{index_number}:{index_letter}{index_number}", 
                                value_render_option="ToString", date_time_render_option="FormattedString")

    return current_data

def standardize_table_format():

    index_number = find_index_date()
    index_letter = find_index_hour()

    # 获取上次更新时间
    last_update_str = str(api.cached.get('locate_now_time', ''))
    last_update_datetime = datetime.datetime.strptime(last_update_str, '%m%d%H%M') if last_update_str else None
    current_time = datetime.datetime.now()

    # 检查是否需要执行if内的代码
    if (last_update_datetime is None or 
        last_update_datetime.strftime('%m%d%H') != current_time.strftime('%m%d%H')):
        # 重置表头样式
        init_range = "9ba2f5!B1:Y1"
        init_style = {"foreColor": "#000000", "backColor": "#D9F5D6"}
        api.update_cell_style(init_range, init_style)

        # 重置昨今明天样式
        hourly_range = f"{sheet_id_write}!B{index_number-1}:Y{index_number+1}"
        hourly_style = {"foreColor": "#000000", "backColor": "#FFFFFF"}
        api.update_cell_style(hourly_range, hourly_style)

        # 标记此时单元格
        hourly_range = f"{sheet_id_write}!{index_letter}{index_number}:{index_letter}{index_number}"
        hourly_style = {"foreColor": "#FFFFFF", "backColor": "#133C9A"}
        api.update_cell_style(hourly_range, hourly_style)

        # 标记此时表头
        hourly_range = f"{sheet_id_write}!{index_letter}1:{index_letter}1"
        hourly_style = {"foreColor": "#FFFFFF", "backColor": "#F54A45"}
        api.update_cell_style(hourly_range, hourly_style)

        api.cached['locate_now_time'] = current_time.strftime('%m%d%H%M')
        api.update_config_file("cached")  # 更新配置文件
    
    result = api.get_sheet_data(f"{sheet_id_write}!{index_letter}{index_number}:{index_letter}{index_number}", value_render_option="ToString", date_time_render_option="FormattedString")

    return result

if __name__ == "__main__":
    standardize_table_format()
    # find_index_date()
    pass