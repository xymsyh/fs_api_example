import pyperclip
from feishu_api import FeishuOpenAPI
import requests
import json

def detect_language(text):
    # Simple heuristic: if the text contains any Chinese characters
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        return "zh"
    else:
        return "en"

def prepare_text_for_translation(text):
    # 将下划线替换为空格
    return text.replace('_', ' ').replace('\n', '')

def truncate_text(text, max_length):
    if len(text) <= max_length:
        return text
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        # 如果文本是中文，则直接截断
        return text[:max_length]
    else:
        # 如果文本是英文，则找到最后一个完整单词的结束位置
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + '...'

# Initialize the FeishuOpenAPI instance
feishu_api = FeishuOpenAPI()

# Get text from clipboard
source_text = pyperclip.paste()
print("source_text: ")
print(source_text)


source_text = truncate_text(source_text, 1500)

source_text = prepare_text_for_translation(source_text)


# Detect the language of the source text
source_language = detect_language(source_text)
target_language = "zh" if source_language == "en" else "en"

## 使用飞书服务
# translated_text = feishu_api.translate_text(source_language, source_text, target_language)

'''## 使用OpenL服务
def openl_translate(codename, apikey, text, source_lang, target_lang):
    # 构建请求 URL
    url = f"https://api.openl.club/services/{codename}/translate"

    # 构建请求头
    headers = {
        'Content-Type': 'application/json'
    }

    # 构建请求体
    data = {
        'apikey': apikey,
        'text': text,
        'source_lang': source_lang,
        'target_lang': target_lang
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 处理响应
    if response.status_code == 404:
        return "Translation service not found"
    elif response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}"
translated_text = openl_translate("google", "c4fec028-287d-4f89-be4a-df03288cca41", source_text, source_language, target_language)['result']
## ---'''

## 使用DeepL服务
def translate_with_deepl(text, target_language, auth_key):
    url = "https://api-free.deepl.com/v2/translate"
    headers = {
        'Authorization': f'DeepL-Auth-Key {auth_key}'
    }
    data = {
        'text': text,
        'target_lang': target_language
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()
translated_text = translate_with_deepl(source_text, target_language, "0b2a63af-cccd-4676-a897-2f9cbf76ed2d:fx")
translated_text = translated_text['translations'][0]['text']

print(translated_text)


## --- 分割线

print("translated_text: ")
print(translated_text)

# Check the result and copy to clipboard
if translated_text:
    # Check if the source text is one or two words
    word_count = len(source_text.split())
    if word_count == 1 or word_count == 1:
#    if word_count == 1 or word_count == 2:
        result = f"翻译结果 (非句子)：{translated_text}"
    else:
        result = f"翻译结果：{translated_text}"
    print("Translation result copied to clipboard.")
else:
    print("Translation failed.")

# Write variable to file

# The variable to write
your_variable = result

# Specify the file path
file_path = r"C:\Users\Ran\Documents\Quicker\翻译结果.txt"

# Open the file for writing
with open(file_path, "w", encoding="utf-8") as file:
    # Write the variable to the file
    file.write(your_variable)

# Close the file
