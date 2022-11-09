class VMWriter:
    def __init__(self) -> None:
        pass

    def writePush(self, segment, index: int) -> None:
        pass

    def writePop(self, segment, index: int) -> None:
        pass

    def writeArithmetic(self, command) -> None:
        pass

    def writeLabel(self, label) -> None:
        pass

    def writeGoto(self, label) -> None:
        pass

    def writeIf(self, label) -> None:
        pass

    def writeCall(self, name, nArgs: int) -> None:
        pass

    def writeFunction(self, name, nLocals: int) -> None:
        pass

    def writeReturn(self) -> None:
        pass

    def close(self) -> None:
        pass
