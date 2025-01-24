from src.connector import ConnectorFactory
from src.alignment import AlignmentFactory
from difflib import SequenceMatcher
from openai import OpenAI
import tomllib
from loguru import logger

# 以二进制读取模式打开文件
with open("config.toml", "rb") as f:
    conf = tomllib.load(f)

def get_latestB(oldB: str, oldA: str, latestA: str, TOC:str) -> str:
    if oldA == latestA:
        logger.debug("原文未变化")
        return oldB #diff为none：原文没变化直接返回旧译文
    if latestA.strip() == "":
        logger.debug("原文被删除")
        return "" #diff为delete：原文被删除直接返回空
    
    def get_diff(oldA: str, latestA: str) -> str:
        import difflib
        # 生成统一的diff格式
        diff = difflib.unified_diff(
            oldA.splitlines(),
            latestA.splitlines(),
            fromfile='oldA',
            tofile='latestA',
            lineterm=''
        )
        return '\n'.join(diff)


    prompt = f"你将获得中文站旧版文档的一部分（oldB）、对应的旧版英文文档和最新版英文文档的差异（diff），请根据这些信息生成对应的中文文档（latestB）；中文站旧版文档若是英文（未翻译）的话，就把其翻译成中文；你的输出将直接作用到文档上，所以不要输出其他任何内容：\n部分中文站旧版文档（oldB）：\n{oldB}\n\n对应的英文文档diff：\n{get_diff(oldA,latestA)}\n\n最新版中文文档（latestB）："
    logger.debug("发送至AI ==> "+prompt[0:50])

    client = OpenAI(base_url=conf["OPENAI-api"]["base_url"])
    response = client.chat.completions.create(
        model=conf["OPENAI-api"]["model"], 
        messages=[
        {"role": "system", "content": conf["OPENAI-api"]["system_prompt"] },
        {"role": "user", "content": prompt},
    ],
        max_tokens=8192, 
        temperature=0.3,  # 控制生成文本的随机性
        stream=False
    )
    logger.debug("AI返回 <== "+str(response.choices[0].message.content)[0:50])
    return str(response.choices[0].message.content)



alignment = AlignmentFactory.create(type=conf["system"]["alignment"],conf=conf["alignment"][conf["system"]["alignment"]])
connector = ConnectorFactory.create(type=conf["system"]["connector"], conf=conf["connector"][conf["system"]["connector"]])


OldABblocks = alignment.split_AB(connector.get_old_A(), connector.get_old_B())
LatestAblocks = alignment.split(connector.get_latest_A())

logger.debug(f"OldABblocks.TOC: {OldABblocks.TOC}, LatestAblocks.TOC: {LatestAblocks.TOC}")
diff = SequenceMatcher(None, OldABblocks.TOC, LatestAblocks.TOC)

logger.debug(f"Diff opcodes: {diff.get_opcodes()}")
LatestB = [""] * len(OldABblocks.oldA)

def apply_diff(tag:str,i1:int,i2:int,j1:int,j2:int):
    for i in range(i1, i2):
        logger.debug(f"进度： {i}/{len(LatestB)-1}")
        if tag == "equal": # None / Update
            LatestB[i] = get_latestB(OldABblocks.oldB[i], OldABblocks.oldA[i], LatestAblocks.result[j1 + (i - i1)],LatestAblocks.toc_to_str())
        elif tag == "insert": 
            LatestB.insert(i1, get_latestB("", "", LatestAblocks.result[j1 + (i - i1)],LatestAblocks.toc_to_str()))
        elif tag == "delete":
            LatestB.pop(i1)
        elif tag == "replace":
            LatestB[i] = get_latestB(OldABblocks.oldB[i], OldABblocks.oldA[i], LatestAblocks.result[j1 + (i - i1)],LatestAblocks.toc_to_str())
        else:
            raise ValueError(f"Unknown tag: {tag}")
        
for tag, i1, i2, j1, j2 in diff.get_opcodes():
    logger.debug(f"{tag:7} oldAblocks[{i1}:{i2}] --> latestAblocks[{j1}:{j2}]")
    apply_diff(tag, i1, i2, j1, j2)

with open("output/latestB", "w", encoding="utf-8") as f:
    for i in range(len(LatestB)):
        f.write(connector.generate_latest_B(LatestB[i]+"\n"))
