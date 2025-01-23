from abc import ABCMeta, abstractmethod
from typing import  List
from dataclasses import dataclass

@dataclass
class SplitABResult:
    oldA: List[str]  
    oldB: List[str]  
    TOC : List[str]
    
    def toc_to_str(self) -> str:
        return "\n".join(self.TOC)

@dataclass
class SplitResult:
    result: List[str] 
    TOC : List[str]
    
    def toc_to_str(self) -> str:
        return "\n".join(self.TOC)

class Alignment(metaclass=ABCMeta):
    @abstractmethod
    def split_AB(self,oldA:str,oldB:str) -> SplitABResult:
        """
        按照TOC切分oldA、oldB，附带基本的TOC格式是否匹配的检查。
        返回切分后的AB和TOC。
        TOC相当于“块的ID”
        """
        pass
    @abstractmethod
    def split(self,text:str) -> SplitResult:
        pass

class AlignmentFactory():
    def __init__(self):
        pass
    @staticmethod
    def create(type:str) -> Alignment:
        if type == "wikitext":
            from .wikitext import WikitextAlignment
            return WikitextAlignment()
        if type == "none":
            from .none import NoneAlignment
            return NoneAlignment()
        else:
            raise ValueError("Unknown Alignment type")

