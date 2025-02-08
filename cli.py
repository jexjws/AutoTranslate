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
    logger.debug(f"oldB: {oldB[0:30]}\n, oldA: {oldA[0:30]}, latestA: {latestA[0:30]}")
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


    prompt = f"你将获得中文站旧版文档的一部分（oldB）、对应的旧版英文文档和最新版英文文档的差异（diff），请根据这些信息生成对应的最新版中文文档（latestB）；中文站旧版文档若是英文（未翻译）的话，就把其翻译成中文；你的输出将直接作用到文档上，所以不要输出其他任何内容：\n部分中文站旧版文档（oldB）：\n{oldB}\n\n对应的英文文档diff：\n{get_diff(oldA,latestA)}\n\n最新版中文文档（latestB）："
    import time
    logger.debug("发送至AI ==> "+oldA[0:30])

    client = OpenAI(base_url=conf["OPENAI-api"]["base_url"])
    for i in range(3):
        try:
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
        except Exception as e:
            logger.error(f"OpenAI API 调用失败，正在重试 ({i+1}/{3})... 错误信息: {e}")
            time.sleep(2)  # 等待 2 秒后重试

    logger.error("达到最大重试次数，OpenAI API 调用失败")
    raise  # 重新抛出异常


alignment = AlignmentFactory.create(type=conf["system"]["alignment"],conf=conf["alignment"][conf["system"]["alignment"]])
connector = ConnectorFactory.create(type=conf["system"]["connector"], conf=conf["connector"][conf["system"]["connector"]])


OldABblocks = alignment.split_AB(connector.get_old_A(), connector.get_old_B())
LatestAblocks = alignment.split(connector.get_latest_A())

logger.debug(f"OldABblocks.TOC: {OldABblocks.blockIDs}, LatestAblocks.TOC: {LatestAblocks.blockIDs}")
diff = SequenceMatcher(None, OldABblocks.blockIDs, LatestAblocks.blockIDs)

logger.debug(f"Diff opcodes: {diff.get_opcodes()}")
LatestB = [""] * len(LatestAblocks.texts)

for i,LAtext in enumerate(LatestAblocks.texts):
    logger.debug(f"进度： {i}/{len(LatestB)}")
    if LatestAblocks.blockIDs[i] in OldABblocks.blockIDs:
        oldABIndex = OldABblocks.blockIDs.index(LatestAblocks.blockIDs[i])
        LatestB[i] = get_latestB(OldABblocks.oldB[oldABIndex], OldABblocks.oldA[oldABIndex], LatestAblocks.texts[i],LatestAblocks.toc_to_str())
    else:
        LatestB[i] = get_latestB("", "", LatestAblocks.texts[i],LatestAblocks.toc_to_str())

with open("output/latestB", "w", encoding="utf-8") as f:
    for i in range(len(LatestB)):
        f.write(connector.generate_latest_B(LatestB[i]+"\n"))
