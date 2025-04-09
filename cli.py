from src.connector import ConnectorFactory
from src.alignment import AlignmentFactory
from openai import AsyncOpenAI
import tomllib
from loguru import logger
import asyncio
import aiohttp

# 以二进制读取模式打开文件
with open("config.toml", "rb") as f:
    conf = tomllib.load(f)

concurrency = conf["system"]["concurrency"]

async def get_newB_async(session, oldB: str, oldA: str, newA: str, TOC:str) -> str:
    if oldA.strip() == newA.strip():
        logger.debug("原文未变化")
        return oldB #diff为none：原文没变化直接返回旧译文
    if newA.strip() == "":
        logger.debug("原文被删除")
        return "" #diff为delete：原文被删除直接返回空
    logger.debug(f"oldB: {oldB[0:30]}\n, oldA: {oldA[0:30]}, newA: {newA[0:30]}")

    def get_diff(oldA: str, newA: str) -> str:
        import difflib
        # 生成统一的diff格式
        diff = difflib.unified_diff(
            oldA.splitlines(),
            newA.splitlines(),
            fromfile='oldA',
            tofile='newA',
            lineterm=''
        )
        return '\n'.join(diff)


    prompt = f"你将获得中文站旧版文档的一部分、对应的旧版英文文档和最新版英文文档的差异（diff），请根据这些信息生成对应的最新版中文文档；中文站旧版文档若有英文（未翻译）部分的话，就把其翻译成中文；你的输出将直接作用到文档上，所以不要输出其他任何内容：\n中文站旧版文档：\n{oldB}\n\n对应的英文文档diff：\n{get_diff(oldA,newA)}\n\n最新版中文文档："
    logger.debug("发送至AI ==> "+oldA[0:30])

    client = AsyncOpenAI(base_url=conf["OPENAI-api"]["base_url"],max_retries=3)
    for i in range(3):
        try:
            response = await client.chat.completions.create(
                model=conf["OPENAI-api"]["model"],
                messages=[
                {"role": "system", "content": conf["OPENAI-api"]["system_prompt"] },
                {"role": "user", "content": prompt},
            ],
                max_tokens=8192,
                temperature=0.3,  # 控制生成文本的随机性
                stream=False,

            )
            logger.debug("AI返回 <== "+str(response.choices[0].message.content)[0:50])
            return str(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI API 调用失败，正在重试 ({i+1}/{3})... 错误信息: {e}")
            await asyncio.sleep(2)  # 等待 2 秒后重试

    logger.error("达到最大重试次数，OpenAI API 调用失败")
    raise  # 重新抛出异常


alignment = AlignmentFactory.create(type=conf["system"]["alignment"],conf=conf["alignment"][conf["system"]["alignment"]])
connector = ConnectorFactory.create(type=conf["system"]["connector"], conf=conf["connector"][conf["system"]["connector"]])


OldABblocks = alignment.split_AB(connector.get_old_A(), connector.get_old_B())
NewAblocks = alignment.split(connector.get_latest_A())

logger.debug(f"OldABblocks.TOC: {OldABblocks.blockIDs}, NewAblocks.TOC: {NewAblocks.blockIDs}")
NewB = [""] * len(NewAblocks.texts)

async def process_block(session, i, NAtext, OldABblocks, NewAblocks):
    logger.debug(f"进度： {i+1}/{len(NewB)}")
    if NewAblocks.blockIDs[i] in OldABblocks.blockIDs:
        oldABIndex = OldABblocks.blockIDs.index(NewAblocks.blockIDs[i])
        return await get_newB_async(session, OldABblocks.oldB[oldABIndex], OldABblocks.oldA[oldABIndex], NAtext ,NewAblocks.toc_to_str())
    else:
        return await get_newB_async(session, "", "", NAtext ,NewAblocks.toc_to_str())

async def main():
    NewB = [""] * len(NewAblocks.texts)
    semaphore = asyncio.Semaphore(concurrency)  # 创建信号量

    async def process_block_with_semaphore(session, i, NAtext, OldABblocks, NewAblocks):
        async with semaphore:  # 获取信号量
            return await process_block(session, i, NAtext, OldABblocks, NewAblocks)

    async with aiohttp.ClientSession() as session:
        tasks = [process_block_with_semaphore(session, i, NAtext, OldABblocks, NewAblocks) for i, NAtext in enumerate(NewAblocks.texts)]
        NewB = await asyncio.gather(*tasks)

    with open("output/newB", "w", encoding="utf-8") as f:
        for i in range(len(NewB)):
            f.write(connector.generate_latest_B(NewB[i]+"\n"))

asyncio.run(main())
