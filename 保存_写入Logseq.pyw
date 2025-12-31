import feishu_api
import json
import logging
import os

# 配置日志记录
log_path = r'C:\Users\Ran\Desktop\fs_api\保存_写入Logseq.log'
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    encoding='utf-8')

api = feishu_api.FeishuOpenAPI()

# 获取数据
data = api.get_sheet_data('9ba2f5!A1:Y')
pretty_data = json.dumps(data['data']['valueRange']['values'], indent=4, ensure_ascii=False)

# 替换 \n 为实际的换行符
pretty_data = pretty_data.replace('\\n', '\n')

# 写入文件
output_path = r'D:\项目\Logseq\Math\ranfd\ranfd.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(pretty_data)

# 计算文件大小
file_size_bytes = os.path.getsize(output_path)

# 转换文件大小为KB和MB
file_size_kb = file_size_bytes / 1024
file_size_mb = file_size_kb / 1024

# 日志记录
num_lines = pretty_data.count('\n') + 1  # 计算行数
num_chars = len(pretty_data)  # 计算字符数

logging.info(f"数据已写入文件：{output_path}")
logging.info(f"写入的数据行数：{num_lines}")
logging.info(f"写入的数据字符数：{num_chars}")
logging.info(f"写入的数据大小：{file_size_bytes} 字节 ({file_size_kb:.2f} KB / {file_size_mb:.2f} MB)")

print(pretty_data)
print("\n【成功写入】\n【成功写入！】\n【成功写入！！】\n【成功写入！！】\n【成功写入！！！】\nData has been written to", output_path)
