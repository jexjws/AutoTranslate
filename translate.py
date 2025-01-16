from connector.mediawiki import archlinuxcnPage
from openai import OpenAI

def get_diff(oldA: str, latestA: str) -> str:
    # 这里可以使用 diff 工具来生成 oldA 和 latestA 之间的差异
    # 例如使用 difflib 库
    import difflib
    diff = difflib.unified_diff(oldA.splitlines(), latestA.splitlines(), lineterm='')
    return '\n'.join(diff)

# TODO: 不要直接让AI生成全部内容，应该以目录为单位，把需要翻译的段落提取出给他
def generate_latestB(oldB: str, diff: str) -> str:
    client = OpenAI(api_key="sk-91825a9750c648e99c0899feddeeeb9a", base_url="https://api.deepseek.com")
    
    # 构建 prompt，将 oldB 和 diff 提供给 AI
    prompt = f"以下是旧版中文文档（oldB）：，旧版英文文档和最新版英文文档的差异（diff信息），请根据这些信息生成最新版中文文档（latestB）：\n\n旧版中文文档（oldB）：\n{oldB}\n\n英文文档diff：\n{diff}\n\n最新版中文文档（latestB）："
    
    response = client.chat.completions.create(
        model="deepseek-chat",  # 选择合适的模型
        messages=[
        {"role": "system", "content": "你是一位精通archlinux的热心小子，经常为archwiki做贡献"},
        {"role": "user", "content": prompt},
    ],
        max_tokens=8192,  # 根据需要调整
        temperature=0.3,  # 控制生成文本的随机性
        stream=False
    )
    print(response.choices)
    return str(response.choices[0].message.content)

def main():
    c = archlinuxcnPage(page_title="安装指南")
    print(c.page.section())
    exit()
    # 获取 oldA 和 latestA
    oldA = c.get_old_A()
    latestA = c.get_latest_A()
    
    # 获取 oldB
    oldB = c.get_old_B()
    
    # 计算 oldA 和 latestA 之间的差异
    diff = get_diff(oldA, latestA)
    print(diff)
    # 生成 latestB
    latestB = generate_latestB(oldB, diff)
    c.commit_latest_B(latestB)


    
    # c.commit_latest_B(latestB)
    # print(c.page.text)

if __name__ == "__main__":
    main()