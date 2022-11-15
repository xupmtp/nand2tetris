class VMWriter:
    def __init__(self, o_file) -> None:
        self.file = o_file

    def writePush(self, segment, index: int) -> None:
        self.file.write(f"push {segment} {index}")

    def writePop(self, segment, index: int) -> None:
        self.file.write(f"pop {segment} {index}")

    def writeArithmetic(self, command) -> None:
        self.file.write(command)

    def writeLabel(self, label) -> None:
        self.file.write(f"label {label}")

    def writeGoto(self, label) -> None:
        self.file.write(f"goto {label}")

    def writeIf(self, label) -> None:
        self.file.write(f"if-goto {label}")

    def writeCall(self, name, nArgs: int) -> None:
        self.file.write(f"call {name} {nArgs}")

    def writeFunction(self, name, nLocals: int) -> None:
        self.file.write(f"function {name} {nLocals}")

    def writeReturn(self) -> None:
        self.file.write("return")
