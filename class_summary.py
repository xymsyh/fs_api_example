def process(data, keyword):
    """
    从给定数据中提取所有特定模式之间的内容，并支持多个匹配项。

    :param data: 包含要处理的数据的列表，格式应为列表的列表。
    :param keyword: 用于构造起始和结束模式的关键词。
    :return: 提取的内容列表，格式为列表的列表。
    """
    # 定义更新 start_pattern 和 end_pattern 的函数
    def update_patterns(keyword):
        start_pattern = f"[{keyword}["
        end_pattern = f"]{keyword}]"
        return start_pattern, end_pattern

    # 获取 start_pattern 和 end_pattern
    start_pattern, end_pattern = update_patterns(keyword)

    summaries_extract = []
    for cell in data:
        # 强制转换 cell[0] 为字符串
        cell_content = str(cell[0])
        summaries = []
        start_index = 0
        while start_index != -1:
            # 查找 start_pattern 和 end_pattern 的位置
            start_index = cell_content.find(start_pattern, start_index)
            end_index = cell_content.find(end_pattern, start_index)
            if start_index != -1 and end_index != -1:
                # 提取并添加内容
                summary = cell_content[start_index + len(start_pattern):end_index]
                summaries.append(summary)
                # 更新 start_index 以在字符串中查找下一个模式
                start_index = end_index + len(end_pattern)
            else:
                break
        if summaries:
            # 用 '。' 连接多个摘要
            summaries_extract.append(["。".join(summaries)])
        else:
            # 如果找不到匹配的内容，添加 "None"
            summaries_extract.append(["N"])

    return summaries_extract

