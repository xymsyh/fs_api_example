import tkinter as tk
import subprocess
import pyperclip
import datetime
import sys
from feishu_api import FeishuOpenAPI

# Function to create knowledge node
def create_node(title, obj_type):
    if not title:
        title = datetime.datetime.now().strftime("%m%d%H%M")

    if title and obj_type:
        # Call method to create knowledge base node
        response = feishu_api.create_knowledge_node(space_id, obj_type, title=title, parent_node_token=parent_node_token)

        # Extract node_token from response
        node_token = response.get('data', {}).get('node', {}).get('node_token')

        if node_token:
            # Build URL
            url = f"https://rcentral.feishu.cn/wiki/{node_token}"
            pyperclip.copy(url)

            # Open URL in Edge app mode
            subprocess.run([edge_path, '--app=' + url])

            # Close window
            root.destroy()
        else:
            print("Node token not found in response.")

# Set fixed parameters
space_id = "7312268105748627457"
parent_node_token = "P2mXwgtt9is13mkbiqkc8wRknRU"
edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"  # Adjust based on your system

# Instantiate FeishuOpenAPI class
feishu_api = FeishuOpenAPI()

# Check if command-line arguments are provided
if len(sys.argv) > 1:
    # Parse command-line arguments
    title = None
    obj_type = None
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--title" and i + 1 < len(sys.argv):
            title = sys.argv[i + 1]
        elif sys.argv[i] == "--type" and i + 1 < len(sys.argv):
            obj_type = sys.argv[i + 1]

    # If both title and obj_type are provided, create node directly
    if title and obj_type:
        create_node(title, obj_type)
        sys.exit(0)  # Exit the script after creating the node

# Create tkinter GUI
root = tk.Tk()
root.title("创建飞书文档")

# Calculate window position for centering
window_width = 400
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
root.geometry(f'{window_width}x{window_height}+{x}+{y}')

# Title input
tk.Label(root, text="标题:").pack()
title_entry = tk.Entry(root)
title_entry.pack()

# Document type selection
obj_type_var = tk.StringVar(value="docx")  # Default value is 'doc'
obj_types = ['doc', 'docx', 'sheet', 'mindnote', 'bitable']
tk.Label(root, text="文档类型:").pack()
for obj_type in obj_types:
    tk.Radiobutton(root, text=obj_type, variable=obj_type_var, value=obj_type).pack()

# Add button to trigger document creation
button = tk.Button(root, text="创建文档", command=lambda: create_node(title_entry.get(), obj_type_var.get()))
button.pack(pady=20)

# Run GUI
root.mainloop()


"""# 示例用法1：指定标题和文档类型
python script.py --title "我的文档" --type docx
# 这将启动GUI并在标题输入框中预先填充"我的文档"，文档类型选择为docx。

# 示例用法2：只指定文档类型
python script.py --type sheet
# 这将启动GUI并将文档类型选择为sheet，标题输入框保持空白，可以手动输入标题后创建文档。

# 示例用法3：不指定任何参数
python script.py
# 这将启动GUI，用户可以手动输入标题和选择文档类型后创建文档。
"""