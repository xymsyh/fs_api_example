import json
import os
import re

def prepare():

    # 获取脚本所在的目录
    script_dir = os.path.dirname(__file__)

    # 构建JSON文件的完整路径
    json_file_path = os.path.join(script_dir, 'json_keywords.json')

    # 读取原始JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 遍历每个类别
    for category in data.values():
        for item in category:
            # 确保所有所需字段都存在
            item.setdefault('keyword', '留空')
            item.setdefault('keyword_id', '留空')
            item.setdefault('inp_keyword', ['留空', '留空'])
            item.setdefault('inp_content', ['留空', '留空'])
            item.setdefault('method', 'class_none')
            item.setdefault('last', '0')
    return data

def write_kws_json(data):

    # 构建新JSON文件的完整路径
    script_dir = os.path.dirname(__file__)
    updated_json_file_path = os.path.join(script_dir, 'json_keywords.json')

    # 先将数据写入JSON文件
    with open(updated_json_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

    # 读取JSON文件内容
    with open(updated_json_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 使用正则表达式在指定模式后添加换行符
    # content = re.sub(r'("class_[^"]+":)', r'\1\n', content)  # 在"class_{任意值}"后添加换行
    content = re.sub(r'("last": ".+?"}),', r'\1,\n', content) #数量为keyword个数
    content = re.sub(r'(\[\{ *?"keyword")', r'\n\1', content) #数量为class_*个数
    content = re.sub(r'(, "class_)', r'\n\1', content) #数量为class_*个数 -1


    # content = re.sub(r'("keyword": "[^"]+")', r'\1\n', content)  # 在"keyword": {任意值}后添加换行

    # 将修改后的内容写回文件
    with open(updated_json_file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return content

if __name__ == '__main__':
    data = prepare()
    write_kws_json(data)
