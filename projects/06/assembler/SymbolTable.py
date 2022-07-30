class Symbol_Table:
    """一個map table，紀錄所有變數代表的address數字"""
    def __init__(self):
        self.symbol_default_address = 16
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
        return self.table[symbol]


    def add_new_symbol(self, symbol):
        self.add_entry(symbol, self.symbol_default_address)
        self.symbol_default_address += 1
        
