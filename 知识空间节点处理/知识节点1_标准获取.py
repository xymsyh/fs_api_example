
import sys
from pathlib import Path
def add_project_root_to_sys_path():
    # 获取当前文件的绝对路径  
    current_file_path = Path(__file__).resolve()

    # 获取当前文件的父目录的父目录（即项目根目录）
    project_root = current_file_path.parent.parent

    # 将项目根目录添加到 sys.path
    sys.path.append(str(project_root))
add_project_root_to_sys_path()

import feishu_api

api = feishu_api.FeishuOpenAPI()


space_id = "7309775928429674500"  # 知识空间ID
page_size = 50  # 每页大小
page_token = None  # 第一次请求不填，表示从头开始遍历
parent_node_token = None  # 父节点token，可选

result = api.get_knowledge_space_children(space_id, page_size, page_token, parent_node_token)
print(result)
