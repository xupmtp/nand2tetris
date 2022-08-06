class Code_Writer:
    def __init__(self, f_name) -> None:
        try:
            self.out_file = open(f'./{f_name}.asm', 'w')
        except:
            print('open out file fail')


    def write_arithmetic(self, cmd) -> None:
        pass


    def write_push_pop(self, cmd, segment, index) -> None:
        pass


    def close(self) -> None:
        self.out_file.close()