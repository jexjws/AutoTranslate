from . import Alignment, SplitABResult,SplitResult
from typing import List


class WikitextAlignment(Alignment):
    def __init__(self, split_precision: int):
        self.split_precision = split_precision
    def _wikitext_section_detect(self, line: str) -> int:
        """
        Check if the line is a Wikitext section header (e.g., '=== text ===').
        If it is, return the number of '=' characters on each side.
        If not, return 0.
        """
        line = line.strip()
        if line.startswith("=") and line.endswith("="):
            left_equals = len(line) - len(line.lstrip("="))
            right_equals = len(line) - len(line.rstrip("="))
            if left_equals == right_equals and left_equals > 0 and left_equals <= self.split_precision: 
                return left_equals
        return 0

    def split_AB(self, oldA: str, oldB: str) -> SplitABResult:
        wikitext_section_detect = self._wikitext_section_detect

        Alines = oldA.splitlines()
        Blines = oldB.splitlines()
        ABlocks: List[str] = []
        BBlocks: List[str] = []
        Bilne_i = 0

        # 遍历 Alines，遇到章节行，就用 Bilne_i+=1 找对应的 Blines 中的章节行
        ABlock_temp = ""
        BBlock_temp = ""

        def traverse_Blines():
            nonlocal Bilne_i
            nonlocal BBlock_temp
            Bline = ""
            while Bilne_i < len(Blines):
                    Bline = Blines[Bilne_i]
                    uwu = wikitext_section_detect(Bline)
                    if uwu == 0:
                         # 如果不是对应的章节行，继续添加到 BBlock_temp
                        BBlock_temp += Bline + "\n"
                        Bilne_i += 1
                    elif uwu == uwa:
                        # 找到对应的章节行，将当前的 BBlock_temp 存入 BBlocks
                        BBlocks.append(BBlock_temp)
                        # 重置 BBlock_temp ，将当前章节行加入新的块
                        BBlock_temp = Bline
                        # 增加 Bilne_i，继续处理下一行
                        Bilne_i += 1
                        return
                    else:
                        raise ValueError(f"章节标题{Aline}与{Bline}的级别不匹配")
            else:
                # 如果遍历完 Blines 仍未找到对应的章节行，处理剩余内容
                BBlocks.append(BBlock_temp)

        for Aline in Alines:
            uwa = wikitext_section_detect(Aline)
            if uwa > 0:
                traverse_Blines()
                ABlocks.append(ABlock_temp)
                ABlock_temp = Aline 
            else:
                ABlock_temp += Aline + "\n"
        traverse_Blines()        
        if ABlock_temp:
            # 处理最后剩余的块
            ABlocks.append(ABlock_temp)

        # 生成TOC
        TOC = []
        TOC.append("<条目开头>")
        for aline in Alines:
            if wikitext_section_detect(aline) > 0:
                TOC.append(aline)

        return SplitABResult(oldA=ABlocks, oldB=BBlocks, blockIDs=TOC)
    def split(self, text: str) -> SplitResult:
        wikitext_section_detect = self._wikitext_section_detect

        lines = text.splitlines()
        blocks: List[str] = []
        block_temp = ""
        for line in lines:
            if wikitext_section_detect(line) > 0:
                if block_temp:
                    blocks.append(block_temp)
                block_temp = line + "\n"
            else:
                block_temp += line + "\n"
        if block_temp:
            blocks.append(block_temp)

        # 生成TOC
        TOC = []
        TOC.append("<条目开头>")
        for line in lines:
            if wikitext_section_detect(line) > 0:
                TOC.append(line)
        return SplitResult(texts=blocks, blockIDs=TOC)

