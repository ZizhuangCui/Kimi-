import os
import re

def clean_text_file(file_path):
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用正则表达式删除时间戳和行号
    #cleaned_content = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
    cleaned_content = re.sub(r'^\d+\n\d{2}:\d{2}:\d{2}\n{3}\n-->\n\d{2}:\d{2}:\d{2}\n{3}\n', '', content, flags=re.MULTILINE)
    
    # 写回清理过的内容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)

def clean_directory(directory_path):
    # 遍历目录中的所有文件
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(directory_path, file_name)
            clean_text_file(file_path)
            print(f"Cleaned {file_name}")

if __name__ == "__main__":
    # 指定要清理的目录路径
    directory_path = './txt文件夹'  # 修改为你的目录路径
    clean_directory(directory_path)
