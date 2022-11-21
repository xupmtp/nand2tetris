class VMWriter:
    """寫入VM命令到.vm檔"""
    def __init__(self, o_file) -> None:
        self.file = o_file

    def writePush(self, segment, index: int) -> None:
        self.file.write(f"push {segment} {index}\n")

    def writePop(self, segment, index: int) -> None:
        self.file.write(f"pop {segment} {index}\n")

    def writeArithmetic(self, command) -> None:
        self.file.write(command + "\n")

    def writeLabel(self, label) -> None:
        self.file.write(f"label {label}\n")

    def writeGoto(self, label) -> None:
        self.file.write(f"goto {label}\n")

    def writeIf(self, label) -> None:
        self.file.write(f"if-goto {label}\n")

    def writeCall(self, name, nArgs: int) -> None:
        self.file.write(f"call {name} {nArgs}\n")

    def writeFunction(self, name, nLocals: int) -> None:
        self.file.write(f"function {name} {nLocals}\n")

    def writeReturn(self) -> None:
        self.file.write("return\n")
