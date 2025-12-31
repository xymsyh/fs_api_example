# 本存在符号链接

import requests
import json
import os
import time
import pprint
import re #测试


class FeishuOpenAPI:
    def __init__(self, app_id=None, app_secret=None, doc_token=None):
        script_dir = os.path.dirname(__file__)
        self.config_path = os.path.join(script_dir, 'json_config.json')
        self.cached_path = os.path.join(script_dir, 'json_cached.json')
        self.config, self.cached = self.load_config()  # 加载配置和缓存信息

        self.app_id = app_id or self.config.get('app_id')
        self.app_secret = app_secret or self.config.get('app_secret')
        self.doc_token = doc_token or self.config.get('doc_token')

        self.base_url = "https://open.feishu.cn/open-apis"

        # 处理 tenant_access_token
        self.tenant_access_token = None
        self.handle_tenant_access_token()
        print(self.tenant_access_token)

        # 处理 obj_token
        if self.doc_token == self.cached.get('doc_token'):
            self.obj_token = self.cached.get('obj_token')
        else:
            self.obj_token = self.get_obj_token()
            self.update_obj_token_config()
        
        print(self.obj_token)

    def send_request(self, method, endpoint, headers=None, data=None, params=None):
        print(f'running function: send_request. endpoint: {endpoint}. self.tenant_access_token: {self.tenant_access_token}')
        url = f"{self.base_url}/{endpoint}"

        if not headers:
            headers = {
                "Authorization": f"Bearer {self.tenant_access_token}",
                "Content-Type": "application/json; charset=utf-8"
            }

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, params=params)
            else:
                response = requests.post(url, headers=headers, json=data, params=params)

            response_json = response.json()
            # print("本次send_request返回结果: " + str(response_json))
            response.raise_for_status()

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            response_json = response.json()  # 获取响应内容

            # 检查响应中是否有特定的错误代码
            if response_json.get('code') == 99991663 or response_json.get('code') == 99991661:
                print("Invalid access token detected. Fetching a new token and retrying the request.")
                self.tenant_access_token = self.get_tenant_access_token()
                headers["Authorization"] = f"Bearer {self.tenant_access_token}"  # 更新headers中的token
                self.update_tenant_token_config() # 更新缓存的token
                return self.send_request(method, endpoint, headers, data, params)

            return None  # 如果不是特定错误代码，返回 None

        return response_json  # 正常情况下返回响应内容
    
    def send_message(self, receive_id = None, msg = None):
        if receive_id == None:
            receive_id = "Yao"

        if msg == None:
            msg = "Hello, World! (默认None值消息)"

        # 参数，指定接收者ID类型为聊天ID
        params = {"receive_id_type": "user_id"}

        # 构造消息内容的JSON对象
        msgContent = {
            "text": msg,
        }

        # 构造请求的主体，包括接收者ID、消息类型和消息内容
        req = {
            "receive_id": receive_id,  # 聊天ID
            "msg_type": "text",        # 消息类型为文本
            "content": json.dumps(msgContent)  # 消息内容，转换为JSON字符串
        }

        # 调用 send_request 方法发送请求
        response = self.send_request("POST", "im/v1/messages", data=req, params=params)
        print(response)
    
    def load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                config = json.load(file)
            with open(self.cached_path, 'r') as file:
                cached = json.load(file)
            return config, cached
        except FileNotFoundError:
            return {}, {}

    def update_obj_token_config(self):
        self.cached['doc_token'] = self.doc_token
        self.cached['obj_token'] = self.obj_token
        self.update_config_file("cached")

    def update_tenant_token_config(self):
        self.cached['tenant_token'] = self.tenant_access_token
        self.cached['tenant_token_time'] = time.time()
        self.update_config_file("cached")

    def update_config_file(self, section):
        # 根据section选择文件路径
        path = self.cached_path if section == "cached" else self.config_path
        # 获取要更新的字典
        dict_to_update = self.cached if section == "cached" else self.config

        # 将更新后的内容写回文件
        with open(path, 'w') as file:
            json.dump(dict_to_update, file, indent=4)

    def handle_tenant_access_token(self):
        current_time = time.time()
        cached_token = self.cached.get('tenant_token')
        cached_token_time = self.cached.get('tenant_token_time', 0)

        # 检查 cached_token 是否有效并且未过期
        if cached_token is not None and current_time - cached_token_time < 7200:
            self.tenant_access_token = cached_token
        else:
            self.tenant_access_token = self.get_tenant_access_token()
            self.update_tenant_token_config()


    

    def get_tenant_access_token(self):
        payload = {'app_id': self.app_id, 'app_secret': self.app_secret}
        return self.send_request('POST', 'auth/v3/tenant_access_token/internal', data=payload)['tenant_access_token']

    def get_obj_token(self, manual_input_token=None):
        if manual_input_token == None:
            manual_input_token = self.doc_token
        endpoint = f'wiki/v2/spaces/get_node?token={manual_input_token}'
        response = self.send_request('GET', endpoint)
        return response['data']['node']['obj_token']

    def update_cell_style(self, range, style):
        endpoint = f"sheets/v2/spreadsheets/{self.obj_token}/style"
        data = {"appendStyle": {"range": range, "style": style}}
        return self.send_request('PUT', endpoint, data=data)

    def get_sheet_data(self, range, spreadsheet_token=None, value_render_option=None, date_time_render_option=None, user_id_type=None, keep_origin_format=None):
        
        if keep_origin_format is None:
            if value_render_option is None:
                value_render_option="ToString"
            if date_time_render_option is None:
                date_time_render_option="FormattedString"
        
        if spreadsheet_token is None:
            spreadsheet_token = self.obj_token
            
        endpoint = f"sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}"
        params = {
            'valueRenderOption': value_render_option,
            'dateTimeRenderOption': date_time_render_option,
            'user_id_type': user_id_type
        }
        return self.send_request('GET', endpoint, params=params)
    
    def write_sheet_data(self, range, values, spreadsheet_token=None):
        if spreadsheet_token is None:
            spreadsheet_token = self.obj_token
        endpoint = f"sheets/v2/spreadsheets/{spreadsheet_token}/values"
        data = {
            "valueRange": {
                "range": range,
                "values": values,
            }
        }
        return self.send_request('PUT', endpoint, data=data)
    
    def translate_text(self, source_language, text, target_language, glossary=None):
        endpoint = "translation/v1/text/translate"
        payload = {
            "source_language": source_language,
            "text": text,
            "target_language": target_language
        }
        if glossary:
            payload["glossary"] = glossary

        response = self.send_request('POST', endpoint, data=payload)
        if response and response.get('code') == 0:
            return response['data']['text']
        else:
            error_msg = response.get('msg', 'Translation failed') if response else 'No response from server'
            # print(f"Error in translation: {error_msg}")
            # print(f"response结果：{response}")
            return response
            return None

    def create_knowledge_node(self, space_id, obj_type, title=None, parent_node_token=None, origin_node_token=None, node_type="origin"):
        """
        创建飞书知识库中的节点。

        参数:
        - space_id: 知识空间ID
        - obj_type: 文档类型（如 'doc', 'sheet', 'mindnote' 等）
        - title: 文档标题（可选）
        - parent_node_token: 父节点 token（可选）
        - origin_node_token: 快捷方式对应的实体node_token（可选）
        - node_type: 节点类型（默认为 'origin'，可选）
        """
        endpoint = f"wiki/v2/spaces/{space_id}/nodes"
        data = {
            "obj_type": obj_type,
            "node_type": node_type
        }

        if title:
            data["title"] = title
        if parent_node_token:
            data["parent_node_token"] = parent_node_token
        if origin_node_token:
            data["origin_node_token"] = origin_node_token

        return self.send_request('POST', endpoint, data=data)
    
    def replace_cells(self, find, replacement, spreadsheet_token=None, range=None, sheet_id=None, match_case=False, match_entire_cell=False, search_by_regex=False, include_formulas=False):
        if spreadsheet_token is None:
            spreadsheet_token = self.obj_token
        
        if sheet_id is None:
            sheet_id = self.config.get('sheet_id_write', '0')  # 假设默认sheet_id是'0'
        
        if range is None:
            range = f"{sheet_id}!A:Y"
        
        # 构建请求URL的路径部分
        endpoint = f"sheets/v3/spreadsheets/{spreadsheet_token}/sheets/{sheet_id}/replace"
        
        # 构建请求体
        payload = {
            "find_condition": {
                "range": range,
                "match_case": match_case,
                "match_entire_cell": match_entire_cell,
                "search_by_regex": search_by_regex,
                "include_formulas": include_formulas
            },
            "find": find,
            "replacement": replacement
        }
        
        # 使用类的send_request方法发送POST请求
        response = self.send_request('POST', endpoint, data=payload)
        
        # 根据send_request的实现，它已经处理了请求的发送、认证和错误处理
        # 因此，这里只需要返回send_request的结果即可
        return response

    def get_knowledge_space_children(self, space_id, page_size=10, page_token=None, parent_node_token=None):
        """
        获取知识空间子节点列表。
        :param space_id: 知识空间ID
        :param page_size: 分页大小
        :param page_token: 分页标记，第一次请求不填，表示从头开始遍历
        :param parent_node_token: 父节点token，可选参数
        :return: 响应的JSON数据
        # 作者 https://chatgpt.com/c/22727f01-adb7-45ce-bb51-545e22a79246

        """
        endpoint = f"wiki/v2/spaces/{space_id}/nodes"
        params = {
            "page_size": page_size
        }
        if page_token:
            params["page_token"] = page_token
        if parent_node_token:
            params["parent_node_token"] = parent_node_token

        response = self.send_request('GET', endpoint, params=params)
        return response

    def get_document_raw_content(self, document_id, lang=0):
        """
        获取文档的纯文本内容。
        :param document_id: 文档的唯一标识
        :param lang: 指定返回的 MentionUser 即 @用户 的语言
        :return: 响应的JSON数据
        """
        endpoint = f"docx/v1/documents/{document_id}/raw_content"
        params = {
            "lang": lang
        }

        response = self.send_request('GET', endpoint, params=params)
        return response
    
    def list_bitable_tables(self, app_token, page_token=None, page_size=100):
        """
        根据 app_token，获取多维表格下的所有数据表。
        :param app_token: 多维表格的唯一标识符
        :param page_token: 分页标记，第一次请求不填，表示从头开始遍历
        :param page_size: 分页大小，飞书默认值20，最大值100
        :return: 响应的JSON数据
        """
        endpoint = f"bitable/v1/apps/{app_token}/tables"
        params = {
            "page_size": page_size
        }
        if page_token:
            params["page_token"] = page_token

        response = self.send_request('GET', endpoint, params=params)
        return response
    
    def search_bitable_records(self, app_token, table_id, view_id=None, field_names=None, sort=None, filter=None, page_token=None, page_size=500, user_id_type='open_id', automatic_fields=False):
        """
        查询数据表中的现有记录。
        :param app_token: 表格token
        :param table_id: 表ID
        :param view_id: 视图的唯一标识符，获取指定视图下的记录
        :param field_names: 字段名称，用于指定本次查询返回记录中包含的字段
        :param sort: 排序条件
        :param filter: 筛选条件
        :param page_token: 分页标记，第一次请求不填，表示从头开始遍历
        :param page_size: 分页大小，飞书默认值20，最大值500
        :param user_id_type: 用户ID类型，默认为'open_id'
        :param automatic_fields: 控制是否返回自动计算的字段
        :return: 响应的JSON数据
        """
        endpoint = f"bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
        params = {
            "user_id_type": user_id_type,
            "page_token": page_token,
            "page_size": page_size
        }
        data = {
            "view_id": view_id,
            "field_names": field_names,
            "sort": sort,
            "filter": filter,
            "automatic_fields": automatic_fields
        }
        # 移除None值
        data = {k: v for k, v in data.items() if v is not None}

        response = self.send_request('POST', endpoint, params=params, data=data)
        return response

    def get_sheets(self, spreadsheet_token):
        """
        根据电子表格 token 获取表格中所有工作表及其属性信息。
        :param spreadsheet_token: 电子表格的 token
        :return: 响应的JSON数据
        """
        endpoint = f"sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
        
        response = self.send_request('GET', endpoint)
        return response

    def add_bitable_record(self, app_token, table_id, fields, user_id_type="open_id", client_token=None):
        """
        在多维表格中新增一条记录。
        
        :param app_token: 多维表格的唯一标识符
        :param table_id: 多维表格数据表的唯一标识符
        :param fields: 数据表的字段内容，格式为字典
        :param user_id_type: 用户 ID 类型，默认值为 'open_id'
        :param client_token: 操作的唯一标识，用于幂等的进行更新操作，默认值为 None
        :return: 响应的 JSON 数据
        """
        endpoint = f"bitable/v1/apps/{app_token}/tables/{table_id}/records"
        params = {"user_id_type": user_id_type}
        if client_token:
            params["client_token"] = client_token
        data = {"fields": fields}
        
        response = self.send_request('POST', endpoint, data=data, params=params)
        return response


if __name__ == "__main__":

    api = FeishuOpenAPI()

    '''# region: 测试获取知识空间子节点列表
    # 作者 https://chatgpt.com/c/22727f01-adb7-45ce-bb51-545e22a79246
    space_id = "7309775928429674500"  # 知识空间ID
    page_size = 50  # 每页大小
    page_token = None  # 第一次请求不填，表示从头开始遍历
    parent_node_token = None  # 父节点token，可选

    result = api.get_knowledge_space_children(space_id, page_size, page_token, parent_node_token)
    pprint.pprint(result)
    # endregion'''


    """# region: # 获取文档纯文本内容示例
    document_id = "MjSUdpKqHoFFFWxWYHtcwcnmnXp"  # 文档的唯一标识
    lang = 0  # 指定返回的 MentionUser 即 @用户 的语言
    document_content = api.get_document_raw_content(document_id, lang)
    pprint.pprint(document_content)
    # endregion"""


    """# region: # 获取多维表格下所有数据表示例
    app_token = "D8R0bu9bsaUpZ5sWkOIcPrD8nfc"  # 多维表格的唯一标识符
    page_token = None  # 第一次请求不填，表示从头开始遍历
    tables = api.list_bitable_tables(app_token, page_token)
    pprint.pprint(tables)
    # endregion"""

    """# 查询数据表中的记录示例
    app_token = "D8R0bu9bsaUpZ5sWkOIcPrD8nfc"  # 多维表格的唯一标识符
    table_id = "tblEPNHmAaBsJgwe"  # 表ID
    records = api.search_bitable_records(app_token, table_id)
    pprint.pprint(records)"""

    """# 获取电子表格中所有工作表示例
    spreadsheet_token = "GovcsD7RChVV6qtgULqcPByNn7N"  # 电子表格的 token
    sheets = api.get_sheets(spreadsheet_token)
    pprint.pprint(sheets)"""

    # 写入数据表中的记录示例

    space_id = "7400248247935156226"  # 知识空间ID
    page_size = 50  # 每页大小
    page_token = None  # 第一次请求不填，表示从头开始遍历
    parent_node_token = None  # 父节点token，可选

    result = api.get_knowledge_space_children(space_id, page_size, page_token, parent_node_token)
    pprint.pprint(result)

    import sys
    sys.exit()

    # 查询数据表中的记录示例
    app_token = "OpRfb0Zzla5OhPs85r0czDmZnv9"  # 多维表格的唯一标识符
    table_id = "tbl23Y7kEPyDyQKP"  # 表ID
    records = api.search_bitable_records(app_token, table_id)
    pprint.pprint(records)


    # 示例参数
    app_token = "OpRfb0Zzla5OhPs85r0czDmZnv9"  # 多维表格的唯一标识符
    table_id = "tbl23Y7kEPyDyQKP"  # 表ID
    fields = {
        "多行文本": "多行文本内容",
        "条码": "+$$3170930509104X512356",
        "数字": 100,
        "货币": 3,
        "评分": 3,
        "进度": 0.25,
        "单选": "选项1",
        "多选": ["选项1", "选项2"]
    }

    fields = {
        "记录": "多行文本内容"
    }

    # 调用新增记录的方法
    response = api.add_bitable_record(app_token, table_id, fields)
    pprint.pprint(response)