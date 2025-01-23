from . import Alignment, SplitABResult,SplitResult
from typing import List


class WikitextAlignment(Alignment):
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
            if left_equals == right_equals and left_equals > 0 and left_equals <= 3: # left_equals <= 3 不要切分的太细
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
        
        for Aline in Alines:
            uwa = wikitext_section_detect(Aline)
            if uwa > 0:
                while Bilne_i < len(Blines):
                    Bline = Blines[Bilne_i]
                    uwu = wikitext_section_detect(Bline)
                    if uwu == 0:
                        # 如果不是对应的章节行，继续添加到 BBlock_temp
                        BBlock_temp += Bline + "\n"
                        Bilne_i += 1
                    elif uwu == uwa:
                        # 找到对应的章节行，将当前的 BBlock_temp 存入 BBlocks
                        ABlocks.append(ABlock_temp)
                        BBlocks.append(BBlock_temp)
                        # 重置 ABlock_temp 和 BBlock_temp
                        ABlock_temp = ""
                        BBlock_temp = ""
                        # 将当前章节行加入新的块
                        BBlock_temp += Bline 
                        ABlock_temp += Aline 
                        # 增加 Bilne_i，继续处理下一行
                        Bilne_i += 1
                        break
                    else:
                        raise ValueError(f"章节标题{Aline}与{Bline}的级别不匹配")
                else:
                    # 如果遍历完 Blines 仍未找到对应的章节行，处理剩余内容
                    ABlocks.append(ABlock_temp)
                    BBlocks.append(BBlock_temp)
                    ABlock_temp = ""
                    BBlock_temp = ""
            else:
                ABlock_temp += Aline + "\n"
        # 处理最后剩余的块
        if ABlock_temp:
            ABlocks.append(ABlock_temp)
        if BBlock_temp:
            BBlocks.append(BBlock_temp)

        # 生成TOC
        TOC = []
        for aline in Alines:
            if wikitext_section_detect(aline) > 0:
                TOC.append(aline)

        return SplitABResult(oldA=ABlocks, oldB=BBlocks, TOC=TOC)
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
        for line in lines:
            if wikitext_section_detect(line) > 0:
                TOC.append(line)
        return SplitResult(result=blocks, TOC=TOC)