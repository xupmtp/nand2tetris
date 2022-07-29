class Symbol_Table:
    def __init__(self):
        self.table = {
            'SP': 0, 'LCL': 1, 'ARG': 2,
            'THIS': 3, 'THAT': 4, 
            'SCREEN': 0x4000,'KBD': 0x6000
        }
        for i in range(0, 16):
            self.table[f'R{i}'] = i

    
    def add_entry(self, symbol: str, address: int) -> None:
        if not symbol:
            print('add symbol to table fail')
            return
        self.table[symbol] = address


    def contains(self, symbol: str) -> bool:
        return symbol in self.table


    def get_address(self, symbol: str) -> int:
        if symbol not in self.table:
            print('get address fail')
            return -1
        return self.table[symbol]
        