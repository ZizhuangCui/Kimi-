from openai import OpenAI
from dotenv import load_dotenv
from replacements import replacements
import requests
import json
import os
import re
import time

def load_configuration():
    """ 加载配置和环境变量 """
    load_dotenv()
    api_key = os.getenv('MOONSHOT_API_KEY')
    if not api_key:
        raise ValueError("MOONSHOT_API_KEY environment variable is not set.")
    return api_key

def create_client(api_key):
    """ 创建 OpenAI 客户端 """
    return OpenAI(api_key=api_key, base_url="https://api.moonshot.cn/v1")

def read_file_content(filepath):
    """ 读取文件内容 """
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    return sanitize_text(content)  # 清洗敏感词内容后返回
    
def sanitize_text(text, replacements=replacements):
    """通过替换指定词汇来清理文本。"""
    if replacements is None:
        replacements = {
            '习大大': '***',  # 将'不良词汇1'替换为'****'
            '党委书记': '****',  # 将'不良词汇2'替换为'****'
            # 根据需要添加更多词汇。
        }
    
    # 使用正则表达式替换每个不良词汇为对应的占位符
    regex = re.compile('|'.join(map(re.escape, replacements.keys())))
    sanitized_text = regex.sub(lambda match: replacements[match.group(0)], text)
    return sanitized_text

def estimate_token_count(messages, api_key):
    """ 估计给定消息列表中的令牌数量 """
    url = "https://api.moonshot.cn/v1/tokenizers/estimate-token-count"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = json.dumps({"model": "moonshot-v1-8k", "messages": messages})
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['data']['total_tokens']
    print("Failed to estimate token count:", response.text)
    return None

def chat(client, query, history):
    """ 发送聊天请求并返回响应，同时估计使用的令牌数量 """
    new_message = {"role": "user", "content": query}
    history.append(new_message)
    completion = client.chat.completions.create(model="moonshot-v1-32k", messages=history, temperature=0.3)
    response = completion.choices[0].message.content
    history.append({"role": "assistant", "content": response})
    token_count = estimate_token_count(history, client.api_key)
    print(f"Token Count for this session: {token_count}")
    return response

def main():

    api_key = load_configuration()
    client = create_client(api_key)

    input_folder = '/Users/cui/Desktop/deepglint/DeepSeek/186action'  # 修改为你的文件夹路径
    output_folder = 'output_txt'

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Recursively iterate through each directory and subdirectory to find .txt files
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(".txt"):
                file_path = os.path.join(root, filename)
                file_content = read_file_content(file_path)
                time.sleep(10)  # Wait for 10 seconds after reading each file

                # Clean the content
                sanitized_content = sanitize_text(file_content)

                # Prepare the history with initial content
                history = [
                    {"role": "user", "content": "你是 Kimi，擅长中文长文本的处理，我需要你根据我提供的txt文件，给我一个文本内容的评分"},
                    {"role": "user", "content": "我提供给你的文本中通常是两人的对话，一般情况下其中一个人说的比较多，另一个人说的较少，希望这能帮到你"},
                    {"role": "user", "content": sanitized_content},
                    {"role": "user", "content":"""
                        我需要你判断文本中是否有这些“客户的信息”：
                        首付预算
                        总购房预算
                        意向户型
                        意向购房面积
                        居住地：客户目前住在哪里
                        工作地：客户在哪里工作
                        购房常住人数
                        家庭结构：有无孩子；是否结婚
                        职业：客户的工作职业
                        网红、公务员、教师、医生、企业高管、律师、企业老板、个体工商户、家庭主妇
                        认知途径：客户从哪里了解到楼盘的（如：安居客、电视广告等）
                        置业目的：客户购买的目的是什么（如：自主、投资等）
                        意向竞品：客户提到的有意向购买的竞品楼盘
                        竞品意向点：对于竞品比较满意的地方
                        付款方式：贷款、全款
                        置业次数
                        决策人
                        意向点
                        抗性点：什么阻碍了客户买房
                        是否有购房资格
                        是否为老业主：是否已是开发商的业主
                        籍贯：哪里人
                        兴趣爱好
                        是否卖房
                        认房不认贷
                        """}
                    #{"role": "user", "content": "遵照模板，选择简短的词回答，答案请用原文解释备注，或合理使用是否回答。并且在每个答案后面给出一个0-100%的该答案的准确率比例。 最终在末尾根据准确率的总值，给出一个评分0-100，80分合格，只需要将这个最终的评分提供给我，和评分计算就够了，控制在10个字以内，前面的模板不输出了，模板只作为你计算评分使用."}
                ]

                # Use a generic query or you can tailor queries based on file content or name
                try:
                    query = "遵照模板，判断根据文本内容判断能多大程度回答这份模板。 反馈给我一个数字，是文本可以回答了几个模板里的问题，“可答问题数量：”，最终在末尾根据准确率的总值，给出一个评分0-100，80分合格，“评分：”，只需要将这个最终的评分提供给我，和评分计算就够了，控制在10个字以内，不用输出模板内容."
                    response = chat(client, query, history)
                except Exception as e:
                    response = "Error"
                    print(f"Error processing {filename} - {e}")

                folder_name = os.path.basename(root)
                output_file_path = os.path.join(output_folder, 'combined_responses.txt')
                with open(output_file_path, 'a', encoding='utf-8') as output_file:
                    output_file.write(f"Folder: {folder_name}\n")
                    output_file.write(f"评分：{response}\n\n")
                history = []
                print(f"Processed {filename} - response saved under folder {folder_name}")
                time.sleep(30)

if __name__ == "__main__":
    main()