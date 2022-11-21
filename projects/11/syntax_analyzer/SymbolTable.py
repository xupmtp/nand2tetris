from Constant import *


class SymbolTable:
    """建立symbol table, 儲存使用的變數"""
    def __init__(self) -> None:
        self.class_table = {}
        self.sub_table = {}

        # define kind
        self.index = {IDT_STATIC: 0, IDT_FIELD: 0, IDT_VAR: 0, IDT_ARG: 0}

    def getTableByKind(self, kind):
        if kind == IDT_STATIC or kind == IDT_FIELD:
            return self.class_table

        return self.sub_table

    def startSubroutine(self) -> None:
        """初始化子區塊所有參數, class不需初始化"""
        self.sub_table = {}
        self.index[IDT_VAR] = 0
        self.index[IDT_ARG] = 0

    def define(self, name, i_type, kind) -> None:
        """定義一個變數到table"""
        table = self.getTableByKind(kind)
        table[name] = {'type': i_type, 'index': self.index[kind], 'kind': kind}
        self.index[kind] += 1

    def varCount(self, kind) -> int:
        """取得變數種類的數量, TODO 之後可將相關程式替換成呼叫此函數"""
        table = self.getTableByKind(kind)
        return len([1 for k, v in table.items() if v['kind'] == kind])

    def kindOf(self, name) -> str:
        jack_to_vm = {IDT_STATIC: VM_STATIC, IDT_FIELD: VM_THIS, IDT_VAR: VM_LOCAL, IDT_ARG: VM_ARG}
        kind = self._getTableByName(name, 'kind')
        return jack_to_vm[kind] if kind in jack_to_vm else None

    def typeOf(self, name) -> str:
        return self._getTableByName(name, 'type')

    def indexOf(self, name) -> int:
        return self._getTableByName(name, 'index')

    def _getTableByName(self, name, key):
        """以name查屬性, 子域優先"""
        if name in self.sub_table:
            return self.sub_table[name][key]
        elif name in self.class_table:
            return self.class_table[name][key]
        return None

    def paramOf(self, name):
        return self.typeOf(name), self.kindOf(name), self.indexOf(name)
