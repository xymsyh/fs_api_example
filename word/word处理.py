import re

# 读取原始文件
with open("C:\\Users\\Ran\\Desktop\\工程造价\\工程造价\\课程讲座 v2.md", "r", encoding='utf-8') as file:
    content = file.read()

# 使用正则表达式删除所有形式的 “（约X字）”
# modified_content = re.sub(r"\（\d+字\）", "", content)
modified_content = re.sub(r"第[\u4e00-\u9fa5]讲：", "", content)

# 将修改后的内容写入新文件
with open("C:\\Users\\Ran\\Desktop\\工程造价\\工程造价\\课程讲座 v3.md", "w", encoding='utf-8') as file:
    file.write(modified_content)
