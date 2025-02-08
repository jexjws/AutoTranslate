from . import Alignment, SplitABResult,SplitResult


class NoneAlignment(Alignment):
    def split_AB(self, oldA: str, oldB: str) -> SplitABResult:
        return SplitABResult(oldA=[oldA], oldB=[oldB], blockIDs=["FULL TEXT"])
    
    def split(self, text: str) -> SplitResult:
        return SplitResult(texts=[text], blockIDs=["FULL TEXT"])

